#!/usr/bin/env python3
"""Strava sync for the running plan (stdlib only).

Credentials live OUTSIDE the repo, at the path in STRAVA_CREDS (default:
<workspace>/strava-credentials.json), so they can never be committed.

Usage:
  python3 scripts/strava_sync.py authorize-url   # print the one-time consent URL
  python3 scripts/strava_sync.py exchange CODE    # swap consent code -> refresh token
  python3 scripts/strava_sync.py fetch [days]    # write week's activities as JSON
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

CREDS_PATH = os.environ.get(
    "STRAVA_CREDS",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 os.pardir, "strava-credentials.json"),
)
CREDS_PATH = os.path.normpath(CREDS_PATH)
OUT_PATH = os.environ.get(
    "STRAVA_ACTIVITIES_OUT",
    os.path.join(os.path.dirname(CREDS_PATH), "strava-activities.json"),
)
SCOPE = "read,activity:read_all,profile:read_all"


def load_creds():
    with open(CREDS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_creds(creds):
    with open(CREDS_PATH, "w", encoding="utf-8") as f:
        json.dump(creds, f, indent=2)
    os.chmod(CREDS_PATH, 0o600)


def post(url, data):
    req = urllib.request.Request(
        url, data=urllib.parse.urlencode(data).encode(),
        headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def authorize_url():
    c = load_creds()
    q = urllib.parse.urlencode({
        "client_id": c["client_id"], "response_type": "code",
        "redirect_uri": "http://localhost/exchange_token",
        "approval_prompt": "force", "scope": SCOPE})
    print("1. Open this URL in your browser and approve:\n")
    print(f"https://www.strava.com/oauth/authorize?{q}")
    print("\n2. You'll land on http://localhost/exchange_token?code=XXXX (page won't load).")
    print("3. Copy the CODE value from the address bar and run:")
    print(f"   python3 scripts/strava_sync.py exchange CODE")


def exchange(code):
    c = load_creds()
    t = post("https://www.strava.com/oauth/token", {
        "client_id": c["client_id"], "client_secret": c["client_secret"],
        "code": code, "grant_type": "authorization_code"})
    c.update({"refresh_token": t["refresh_token"],
              "access_token": t["access_token"],
              "expires_at": t["expires_at"], "scope": t.get("scope", SCOPE)})
    save_creds(c)
    print("Saved. Refresh token stored in", CREDS_PATH)


def access_token():
    c = load_creds()
    if c.get("expires_at", 0) > time.time() + 60 and c.get("access_token"):
        return c["access_token"]
    t = post("https://www.strava.com/oauth/token", {
        "client_id": c["client_id"], "client_secret": c["client_secret"],
        "grant_type": "refresh_token", "refresh_token": c["refresh_token"]})
    c.update({"access_token": t["access_token"], "expires_at": t["expires_at"]})
    if t.get("refresh_token"):
        c["refresh_token"] = t["refresh_token"]
    save_creds(c)
    return c["access_token"]


def fetch(days=7):
    after = int(time.time() - days * 86400)
    token = access_token()
    acts = get(f"https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=100", token)
    runs = [a for a in acts if a.get("type") in ("Run", "TrailRun", "VirtualRun")]
    out = {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "window_days": days,
        "total_activities": len(acts),
        "runs": len(runs),
        "total_run_km": round(sum(a["distance"] for a in runs) / 1000, 1),
        "activities": [{
            "date": a["start_date"][:10],
            "name": a["name"],
            "type": a["type"],
            "km": round(a["distance"] / 1000, 2),
            "moving_min": round(a["moving_time"] / 60, 1),
            "pace_min_km": (round(a["moving_time"] / 60 / (a["distance"] / 1000), 2)
                            if a["distance"] else None),
            "avg_hr": a.get("average_heartrate"),
            "max_hr": a.get("max_heartrate"),
            "elev_m": a.get("total_elevation_gain"),
            "workout_type": a.get("workout_type"),
            "kudos": a.get("kudos_count"),
        } for a in acts],
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"{len(acts)} activities ({len(runs)} runs, {out['total_run_km']} km) -> {OUT_PATH}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "authorize-url":
        authorize_url()
    elif cmd == "exchange" and len(sys.argv) > 2:
        exchange(sys.argv[2])
    elif cmd == "fetch":
        fetch(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    else:
        print(__doc__)
