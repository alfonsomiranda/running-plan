#!/usr/bin/env python3
"""Recalibración determinista del plan desde los datos de Strava.

Reglas (sin LLM, sin criterio subjetivo):
  1. Tendencia: la mediana de ritmo de los rodajes suaves (FC 130-148)
     se compara con la historia. Un cambio de banda exige o bien un
     desajuste grande (>=30 s) o bien dos semanas seguidas en la misma
     dirección (>=8 s combinados). Tope: 15 s/semana.
  2. Carrera: tras cualquier run >= 15 km, el MP se recalcula con Riegel
     (exp 1.06) y el objetivo de maratón se reescribe.
  3. Notas: km reales vs plan, sesiones, mediana Z2. Nada más cambia.

Usage: python3 scripts/review.py [--dry-run]
"""
import datetime
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIT_PATH = os.path.join(HERE, "fitness.json")
LOG_PATH = os.path.join(HERE, "review_log.json")
ACT_PATH = (os.environ.get("STRAVA_ACTIVITIES_OUT")
            or os.path.join(os.getcwd(), "strava-activities.json"))
WEEKS_PATH = os.path.join(HERE, "weeks_full.json")
SEASON_START = datetime.date(2026, 6, 15)
EASY_MIN_PACE = 350        # s/km; más lento que 5:50 = rodaje suave
EASY_HR_RANGE = (130, 148)
SHIFT_CAP = 15             # s/semana máx por banda
BIG_MISMATCH = 30          # s: desajuste que aplica cambio inmediato
TREND_MIN = 8              # s combinados en 2 semanas para aplicar cambio
RACE_MIN_KM = 15
RIEGEL = 1.06


def psec(p):
    """'m:ss' o 'm:ss,s' (decimal) -> segundos/km"""
    if p is None:
        return None
    m, s = str(p).replace(",", ".").split(":")
    return int(m) * 60 + float(s)


def fmt(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def band(mid, width=5):
    return f"{fmt(mid - width)}-{fmt(mid + width)}"


def main(dry=False):
    today = datetime.date.today()
    with open(ACT_PATH, encoding="utf-8") as f:
        acts = json.load(f)
    with open(FIT_PATH, encoding="utf-8") as f:
        fit = json.load(f)
    with open(WEEKS_PATH, encoding="utf-8") as f:
        weeks = json.load(f)
    log = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as f:
            log = json.load(f)

    runs = [a for a in acts.get("activities", [])
            if a["type"] in ("Run", "TrailRun", "VirtualRun")]
    week_num = max(1, min(45, (today - SEASON_START).days // 7 + 1))
    planned_km = weeks[week_num - 1]["weekly_km"]
    planned_sessions = sum(1 for d in weeks[week_num - 1]["days"]
                           if d["type"] in ("ez", "interval", "tempo", "long", "race", "strength"))
    actual_km = sum(r["km"] for r in runs)

    easy = [r for r in runs
            if r["pace_min_km"] and r["pace_min_km"] >= EASY_MIN_PACE / 60
            and r.get("avg_hr") and EASY_HR_RANGE[0] <= r["avg_hr"] <= EASY_HR_RANGE[1]]
    z2_median = round(statistics.median([r["pace_min_km"] * 60 for r in easy])) if len(easy) >= 3 else None

    # --- regla 1: tendencia de bandas ---
    shift = 0
    reasons = []
    if z2_median:
        z2_fast = psec(fit["zones"]["Z2"].split("-")[0])
        gap = z2_fast - z2_median  # >0: el plan es más optimista que la realidad
        prev = log[-1].get("z2_median") if log else None
        if abs(gap) >= BIG_MISMATCH:
            shift = max(-SHIFT_CAP, min(SHIFT_CAP, gap))
            reasons.append(f"desajuste grande ({gap:+.0f}s) vs banda Z2")
        elif prev and abs(gap) >= TREND_MIN and (z2_median - prev) * gap > 0:
            shift = max(-SHIFT_CAP, min(SHIFT_CAP, gap))
            reasons.append(f"tendencia de 2 semanas ({gap:+.0f}s)")

    # --- regla 2: carrera -> MP ---
    race = max((r for r in runs if r["km"] >= RACE_MIN_KM), key=lambda r: r["km"], default=None)
    if race:
        t_mar = race["moving_min"] * 60 * (42.195 / race["km"]) ** RIEGEL
        mp_mid = t_mar / 42.195
        fit["zones"]["MP"] = band(mp_mid)
        h, rem = divmod(int(t_mar), 3600)
        fit["mp_goal"] = f"sub-{h}:{rem // 60:02d}" if h else f"sub-{rem // 60} min"
        reasons.append(f"carrera {race['km']}km a {fmt(race['pace_min_km'] * 60)}/km -> MP {fit['zones']['MP']}")

    # --- aplicar desplazamiento a las bandas de ritmo ---
    if shift:
        for key in ("Z1", "Z2", "Z2_LR", "Z3", "Z4", "Z5"):
            lo, hi = fit["zones"][key].split("-")
            fit["zones"][key] = f"{fmt(psec(lo) + shift)}-{fmt(psec(hi) + shift)}"
        reasons.append(f"bandas {shift:+.0f}s")

    # --- notas ---
    compliance = (actual_km / planned_km * 100) if planned_km else 0
    fit["notes"] = (f"Semana {week_num}: {actual_km:.1f} km reales de {planned_km} previstos "
                    f"({compliance:.0f}%), {len(runs)} de {planned_sessions} sesiones con carrera"
                    + (f", mediana Z2 {fmt(z2_median)}/km" if z2_median else "")
                    + ". " + ("Ajustes: " + "; ".join(reasons) + "." if reasons
                              else "Sin cambios de ritmo: datos estables."))

    log.append({"date": today.isoformat(), "week": week_num,
                "km": round(actual_km, 1), "km_plan": planned_km,
                "z2_median": z2_median, "shift": shift})

    if dry:
        print(json.dumps({"shift": shift, "reasons": reasons, "notes": fit["notes"],
                          "MP": fit["zones"]["MP"], "log": log[-1]}, indent=2, ensure_ascii=False))
        return

    fit["updated"] = today.isoformat()
    fit["source"] = ("Recalibración determinista desde Strava "
                     f"(sem {week_num}, {len(runs)} runs, {actual_km:.0f} km). "
                     + ("; ".join(reasons) if reasons else "sin cambios de banda"))
    with open(FIT_PATH, "w", encoding="utf-8") as f:
        json.dump(fit, f, indent=2, ensure_ascii=False)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(fit["notes"])


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
