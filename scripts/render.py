import json, datetime

with open("weeks_full.json") as f:
    weeks = json.load(f)

START = datetime.date(2026, 6, 15)
MONTHS_ES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

TYPE_CLASS = {
    "rest":"rest-day","ez":"ez-day","tempo":"tempo-day","interval":"interval-day",
    "strength":"strength-day","long":"long-day","race":"race-day"
}
TYPE_LABEL_COLOR = {
    "rest":"var(--muted)","ez":"var(--accent2)","tempo":"var(--accent)","interval":"var(--accent3)",
    "strength":"var(--purple)","long":"var(--warm)","race":"var(--accent)"
}
TYPE_NAME = {
    "rest":"DESCANSO","ez":"RODAJE FÁCIL","tempo":"TEMPO","interval":"INTERVALOS",
    "strength":"FUERZA","long":"LONG RUN","race":"CARRERA"
}

# Block colors
BLOCK_COLORS = {1: "var(--accent2)", 2: "var(--purple)", 3: "var(--accent3)"}
BLOCK_NAMES = {
    1: "BLOQUE 1 · BEHOBIA-SAN SEBASTIÁN (20km) · 8 NOV 2026",
    2: "BLOQUE 2 · TRANSICIÓN + BASE MARATÓN · GETAFE (21km) 31 ENE 2027",
    3: "BLOQUE 3 · MARATÓN DE MADRID (42,2km) · 25 ABR 2027",
}

def fmt_date(d):
    return f"{d.day} {MONTHS_ES[d.month]}"

def fmt_km(v):
    if isinstance(v, float):
        if v == int(v):
            return f"{int(v)}"
        return f"{v:.1f}".replace(".", ",")
    return str(v)

def day_card(day, date):
    cls = TYPE_CLASS[day["type"]]
    color = TYPE_LABEL_COLOR[day["type"]]
    type_name = TYPE_NAME[day["type"]]
    title = day["title"]
    pace = day.get("pace","")
    dist = day.get("dist","")
    detail = day.get("detail","")
    steps = day.get("steps",[])

    html = f'<div class="day-card {cls}">'
    html += f'<div class="day-card-head">'
    html += f'<div class="day-card-date"><span class="day-name-big">{day["d"]}</span><span class="day-date-small">{fmt_date(date)}</span></div>'
    html += f'<div class="day-type-chip" style="color:{color};border-color:{color}40;background:{color}1a">{type_name}</div>'
    html += f'</div>'
    if day["type"]=="race":
        html += f'<div class="day-title" style="color:{color};font-weight:700;font-size:1rem">{title}</div>'
    else:
        html += f'<div class="day-title">{title}</div>'

    if pace and dist:
        html += f'<div class="day-summary"><span class="day-summary-pace" style="color:{color}">{pace}</span><span class="day-summary-dist">{dist}</span></div>'
    elif pace:
        html += f'<div class="day-summary"><span class="day-summary-pace" style="color:{color}">{pace}</span></div>'

    if steps:
        html += '<div class="step-list">'
        for s in steps:
            html += f'<div class="step-row"><span class="step-label">{s["label"]}</span><span class="step-detail">{s["detail"]}</span></div>'
        html += '</div>'

    if detail:
        html += f'<div class="day-note">{detail}</div>'

    html += '</div>'
    return html

week_blocks = []
current_block = None

for w in weeks:
    start = START + datetime.timedelta(days=(w["num"]-1)*7)
    end = start + datetime.timedelta(days=6)
    block = w["block"]
    color = BLOCK_COLORS[block]

    # Insert block separator header when block changes
    if block != current_block:
        week_blocks.append(f'''
    <div class="block-separator" style="border-color:{color}">
      <div class="block-separator-label" style="color:{color}">{BLOCK_NAMES[block]}</div>
    </div>
        ''')
        current_block = block

    deload_badge = '<span class="deload-badge">DESCARGA</span>' if w["deload"] else ''
    milestone_badge = f'<span class="race-badge">{w["milestone"]}</span>' if w.get("milestone") else ''

    days_html = "".join(day_card(d, start + datetime.timedelta(days=idx)) for idx, d in enumerate(w["days"]))

    lr_label = "MARATÓN" if w["num"] == 45 else ("GETAFE" if w["num"] == 33 else "long run")

    block_id = f"week-{w['num']}"
    card = f'''
    <div class="week-card" data-block="{block}" data-week="{w['num']}">
      <div class="week-card-header" onclick="toggleWeek({w['num']})">
        <div class="week-accent" style="background:{color}"></div>
        <div class="week-title-block">
          <div class="week-number">SEMANA {w['num']} <span class="week-dates">· {fmt_date(start)} – {fmt_date(end)}</span>{deload_badge}{milestone_badge}</div>
          <div class="week-phase-name">{w['phase_name']}</div>
        </div>
        <div class="week-stats">
          <div class="week-stat"><span class="week-stat-val">{fmt_km(w['weekly_km'])}</span><span class="week-stat-label">km</span></div>
          <div class="week-stat"><span class="week-stat-val">{fmt_km(w['long_run'])}</span><span class="week-stat-label">{lr_label}</span></div>
        </div>
        <div class="chevron" id="chevron-{w['num']}">▾</div>
      </div>
      <div class="week-card-body" id="{block_id}">
        <div class="week-focus"><strong>Foco de la semana:</strong> {w['focus']}</div>
        <div class="days-grid">{days_html}</div>
      </div>
    </div>
    '''
    week_blocks.append(card)

WEEKS_HTML = "\n".join(week_blocks)

# Phase nav: jump to key points
phase_nav_items = [
    (1, "BLOQUE 1 · BEHOBIA", "Sem 1-21", BLOCK_COLORS[1]),
    (22, "BLOQUE 2 · TRANSICIÓN", "Sem 22-32", BLOCK_COLORS[2]),
    (33, "🎯 GETAFE (control)", "Sem 33", BLOCK_COLORS[2]),
    (34, "BLOQUE 3 · MARATÓN MADRID", "Sem 34-44", BLOCK_COLORS[3]),
    (45, "🏆 MARATÓN MADRID", "Sem 45", BLOCK_COLORS[3]),
]
phase_nav = ""
for week_num, label, sublabel, color in phase_nav_items:
    phase_nav += f'<button class="phase-nav-btn" style="border-color:{color}" onclick="scrollToWeek({week_num})">{label}<span class="phase-nav-weeks">{sublabel}</span></button>'

print("Generated", len(weeks), "weeks across", len(set(w['block'] for w in weeks)), "blocks")

with open("weeks_html.txt","w") as f:
    f.write(WEEKS_HTML)
with open("phase_nav.txt","w") as f:
    f.write(phase_nav)
