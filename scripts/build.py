#!/usr/bin/env python3
"""
Build script for the full season training plan website
(Behobia-San Sebastian -> Getafe -> Maraton de Madrid).

Generates the 45-week plan and assembles it into index.html for GitHub Pages.

Usage: python3 scripts/build.py
Run from the repository root.
"""
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

def run(script):
    print(f"Running {script}...")
    result = subprocess.run([sys.executable, os.path.join(SCRIPT_DIR, script)],
                             cwd=SCRIPT_DIR, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

# Step 1: Generate full season plan data (weeks_full.json)
run("gen_plan.py")

# Step 2: Render week HTML blocks (weeks_html.txt, phase_nav.txt)
run("render.py")

# Step 3: Assemble final index.html
print("Assembling index.html...")
with open(os.path.join(SCRIPT_DIR, "part1_head.html")) as f:
    head = f.read()
with open(os.path.join(SCRIPT_DIR, "part2_body.html")) as f:
    body = f.read()
with open(os.path.join(SCRIPT_DIR, "part3_strength_script.html")) as f:
    tail = f.read()
with open(os.path.join(SCRIPT_DIR, "weeks_html.txt")) as f:
    weeks = f.read()
with open(os.path.join(SCRIPT_DIR, "phase_nav.txt")) as f:
    phase_nav = f.read()

body = body.replace("__WEEKS__", weeks).replace("__PHASE_NAV__", phase_nav)

full = head + "\n" + body + "\n" + tail

output_path = os.path.join(REPO_ROOT, "index.html")
with open(output_path, "w") as f:
    f.write(full)

print(f"Done. Wrote {output_path} ({len(full)} chars)")
