import json, datetime

with open("weeks_v2.json") as f:
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

PHASE_COLORS = {1:"var(--accent2)", 2:"var(--warm)", 3:"var(--accent3)", 4:"var(--accent)"}
PHASE_NAMES = {1:"FASE 1 · BASE AERÓBICA", 2:"FASE 2 · DESARROLLO DE RITMO", 3:"FASE 3 · ESPECÍFICO BEHOBIA", 4:"FASE 4 · TAPERING"}

def fmt_date(d):
    return f"{d.day} {MONTHS_ES[d.month]}"

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
for w in weeks:
    start = START + datetime.timedelta(days=(w["num"]-1)*7)
    end = start + datetime.timedelta(days=6)
    phase = w["phase"]
    color = PHASE_COLORS[phase]
    deload_badge = '<span class="deload-badge">DESCARGA</span>' if w["deload"] else ''
    race_badge = '<span class="race-badge">🏁 CARRERA</span>' if phase==4 and w["num"]==21 else ''

    days_html = "".join(day_card(d, start + datetime.timedelta(days=idx)) for idx, d in enumerate(w["days"]))

    block = f'''
    <div class="week-card" data-phase="{phase}">
      <div class="week-card-header" onclick="toggleWeek({w['num']})">
        <div class="week-accent" style="background:{color}"></div>
        <div class="week-title-block">
          <div class="week-number">SEMANA {w['num']} <span class="week-dates">· {fmt_date(start)} – {fmt_date(end)}</span>{deload_badge}{race_badge}</div>
          <div class="week-phase-name">{w['phase_name']}</div>
        </div>
        <div class="week-stats">
          <div class="week-stat"><span class="week-stat-val">{w['weekly_km']}</span><span class="week-stat-label">km</span></div>
          <div class="week-stat"><span class="week-stat-val">{w['long_run']}</span><span class="week-stat-label">long run</span></div>
        </div>
        <div class="chevron" id="chevron-{w['num']}">▾</div>
      </div>
      <div class="week-card-body" id="week-{w['num']}">
        <div class="week-focus"><strong>Foco de la semana:</strong> {w['focus']}</div>
        <div class="days-grid">{days_html}</div>
      </div>
    </div>
    '''
    week_blocks.append(block)

WEEKS_HTML = "\n".join(week_blocks)

phase_nav = ""
for p in [1,2,3,4]:
    first_week = next(w["num"] for w in weeks if w["phase"]==p)
    last_week = first_week + (5 if p<4 else 2)
    phase_nav += f'<button class="phase-nav-btn" style="border-color:{PHASE_COLORS[p]}" onclick="scrollToWeek({first_week})">{PHASE_NAMES[p]}<span class="phase-nav-weeks">Sem {first_week}-{last_week}</span></button>'

print("Generated", len(weeks), "weeks")

with open("weeks_html_v2.txt","w") as f:
    f.write(WEEKS_HTML)
with open("phase_nav_v2.txt","w") as f:
    f.write(phase_nav)
