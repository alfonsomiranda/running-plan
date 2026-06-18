import datetime, json

START = datetime.date(2026, 6, 15)

# ═══════════════════════════════════════════════════════════════
# ZONAS CALIBRADAS CON DATOS REALES DE COROS (Alfonso Miranda)
# Umbral láctico: 4:37/km · FC umbral: 158 bpm
# FC máxima estimada: 175 bpm · FC en reposo: 49 bpm (medida)
# Método: Karvonen para FC, % velocidad umbral para ritmos
# ═══════════════════════════════════════════════════════════════

# Ritmos por zona (min/km)
Z1     = "6:47-7:41"   # Recovery — <124 bpm
Z2     = "5:37-6:35"   # Aeróbico base — 124-143 bpm
Z2_LR  = "5:50-6:35"   # Long run (mitad alta de Z2) — 124-140 bpm
Z3     = "5:07-5:37"   # Tempo / umbral bajo — 143-156 bpm
Z4     = "4:45-5:07"   # Umbral láctico — 156-166 bpm
Z5     = "4:18-4:45"   # VO2max — 166-175 bpm
RACE_BEHOBIA = "5:00-5:10"  # Ritmo Behobia 20km (~Z3 alto/Z4 bajo)
MP     = "5:15-5:25"   # Marathon Pace entrenamiento — objetivo carrera ~3:45-3:50

# FC por zona (Karvonen: FCrep=49, FCmax=175, FC reserva=126)
FC_Z1  = "<124"
FC_Z2  = "124-143"
FC_Z3  = "143-156"
FC_Z4  = "156-166"
FC_Z5  = "166-175"
FC_UMBRAL = "158"  # umbral láctico real Coros

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def km(v):
    if isinstance(v, float) and v == int(v):
        v = int(v)
    return f"{v} km"

def mins(minutes, label=""):
    return f"{minutes} min" + (f" {label}" if label else "")

def warm(dist_km, pace=None, label="Calentamiento"):
    """Warm-up: always Z1 pace (clearly slower than the main run)."""
    return {"label": label, "detail": f"{dist_km} km a {Z1}/km · FC {FC_Z1} · trote muy suave para activar"}

def cool(dist_km=None, pace=None, label="Enfriamiento"):
    """Cool-down: Z1 or walking, time-cued."""
    return {"label": label, "detail": f"5-8 min caminando o trote muy suave a {Z1}/km · deja que la FC baje por debajo de 120"}

def z2_block(minutes, label="Rodaje Z2"):
    """Time-based Z2 block — FC is the target, pace is the consequence."""
    return {"label": label, "detail": f"{minutes} min a FC {FC_Z2} · ritmo orientativo {Z2}/km · conversacional, frases completas"}

def main_reps(reps, rep_dist, rep_pace, rec_desc, label="Serie principal"):
    """Quality intervals — distance + pace (pace IS the goal)."""
    return {"label": label, "detail": f"{reps} × {rep_dist} a {rep_pace}/km · recuperación: {rec_desc}"}

def main_continuous(dist_km, pace, fc_or_label=None, label="Cuerpo principal"):
    """Continuous block. For Z2/long runs use FC prescription; for quality use pace."""
    # Determine FC to show: if pace is Z2_LR or Z2, use FC_Z2; if Z3 use FC_Z3 etc.
    if fc_or_label and fc_or_label.startswith("Cuerpo"):
        label = fc_or_label
        fc_or_label = None
    if pace in (Z2, Z2_LR):
        fc_str = FC_Z2
    elif pace == Z3:
        fc_str = FC_Z3
    elif pace in (Z4, RACE_BEHOBIA):
        fc_str = FC_Z4
    elif pace == MP:
        fc_str = "140-155"
    elif pace == Z1:
        fc_str = FC_Z1
    else:
        fc_str = fc_or_label or FC_Z2
    return {"label": label, "detail": f"{dist_km} km a {pace}/km · FC {fc_str}"}

def total_line(total_km, extra=""):
    return f"Total: ~{total_km} km" + (f" · {extra}" if extra else "")

def total_time(minutes, extra=""):
    return f"Duración total: ~{minutes} min" + (f" · {extra}" if extra else "")

STRENGTH_A_STEPS = [
    {"label":"1. Goblet Squat","detail":"3×15 · 10kg · descanso 60\""},
    {"label":"2. Staggered RDL","detail":"3×12 c/lado · 17.5kg · descanso 75\""},
    {"label":"3. Búlgara","detail":"3×10 c/lado · peso corporal · descanso 90\""},
    {"label":"4. Puente glúteo c/pausa","detail":"3×12 · +10kg · descanso 60\""},
    {"label":"5. Gemelo excéntrico","detail":"3×15 · bilateral · descanso 60\""},
    {"label":"6. Plancha + Pallof","detail":"3×40\" plancha + 3×10 Pallof c/lado"},
]
STRENGTH_B_STEPS = [
    {"label":"1. Press banca/flexiones","detail":"3×12 · 50% RM · descanso 75\""},
    {"label":"2. Remo mancuerna","detail":"3×12 c/lado · 20-22kg · descanso 60\""},
    {"label":"3. Hurdle hops","detail":"4×8 · peso corporal · descanso 90\""},
    {"label":"4. Hip thrust","detail":"4×10 · 30-40kg · descanso 75\""},
    {"label":"5. Elevación piernas rectas","detail":"3×12 · peso corporal"},
    {"label":"6. Zancada caminada","detail":"3×10 c/lado · 10kg/mano"},
]
STRENGTH_C_STEPS = [
    {"label":"1. Nórdico isquio","detail":"3×5-8 · bajada 4-5\" · descanso 120\""},
    {"label":"2. Excéntrico gemelo","detail":"3×12 c/lado · bajada 3\" · descanso 60\""},
    {"label":"3. Búlgara excéntrica","detail":"3×8 c/lado · bajada 4\" · descanso 90\""},
    {"label":"4. Step-down excéntrico","detail":"3×10 c/lado · bajada 3\" · descanso 60\""},
    {"label":"5. Plancha lateral dinámica","detail":"3×12 c/lado · descanso 45\""},
]

def strength_plus_run(d, session_letter, run_km, run_pace=Z2, run_label="Trote de activación"):
    """Tuesday/Thursday: short easy run (activation) BEFORE strength session.
    Per Luis del Águila guidance: short activation jog before strength is better
    than adding km after, which accumulates residual fatigue with little aerobic benefit."""
    steps_map = {"A": STRENGTH_A_STEPS, "B": STRENGTH_B_STEPS, "C": STRENGTH_C_STEPS}
    note_map = {
        "A": "Ver tabla completa de 'Sesión A' (Piernas+Core) en la pestaña Fuerza.",
        "B": "Ver tabla completa de 'Sesión B' (Cuerpo completo) en la pestaña Fuerza.",
        "C": "Ver tabla completa de 'Sesión C' (Excéntrica) en la pestaña Fuerza. Foco en control, no velocidad.",
    }
    steps = [{"label": f"1. {run_label}", "detail": f"{run_km}km a {run_pace}/km · FC<140 · activación antes de la fuerza, no fatiga"}]
    # renumber strength steps starting from 2
    for idx, s in enumerate(steps_map[session_letter]):
        new_label = s["label"].split(". ", 1)[-1]
        steps.append({"label": f"{idx+2}. {new_label}", "detail": s["detail"]})
    return {"d":d,"title":f"{run_km}km activación + Fuerza {session_letter}","type":"strength","pace":f"Sesión {session_letter}","dist":f"{run_km}km + 35-40min",
            "steps":steps, "detail":note_map[session_letter] + f" Trote corto antes de la fuerza como activación (no como entrenamiento aeróbico) — llega fresco a la fuerza. {total_line(run_km)}"}

def rest_day(d, detail="Estiramientos suaves opcionales 10 min. Foam roller si tienes."):
    return {"d":d,"title":"Descanso total","type":"rest","steps":[],"total":"0 km","detail":detail}

def sunday_optional(dist_km=5, note="Opcional: solo si llegas fresco tras el long run del sábado. Si hay fatiga, descansa."):
    return {"d":"DOM","title":"Z2 muy suave (opcional)","type":"ez","pace":"5:50-6:30","dist":km(dist_km),
        "steps":[{"label":"Rodaje muy suave","detail":f"30-40 min a FC {FC_Z1}-{FC_Z2.split("-")[0]} · ritmo orientativo {Z2_LR}/km · totalmente opcional"}],
        "detail":note + " " + total_line(dist_km)}

def sunday_rest():
    return rest_day("DOM", "Descanso total. Recuperación tras el long run del sábado.")


weeks = []

# ================================================================
# BLOQUE 1: BEHOBIA — semanas 1-21 (8 nov 2026, 20km)
# Nueva estructura semanal:
#   LUN: descanso | MAR: Fuerza+Z2 | MIÉ: Intervalos/Cuestas
#   JUE: Fuerza+Z2 | VIE: Z2 suave/Recovery | SÁB: Long Run | DOM: Z2 opcional/descanso
# ================================================================

# ---- FASE 1: semanas 1-6, base aeróbica ----
# Cargas revisadas: incrementos 5-10%, deload suave en S5
lr_phase1 = [14, 15, 16, 16, 15, 16]
vol_phase1 = [32, 35, 38, 41, 38, 40]

for i in range(6):
    w = i+1
    lr = lr_phase1[i]
    deload = (i == 4)
    days = []

    days.append(rest_day("LUN"))

    days.append(strength_plus_run("MAR", "A", 3 if not deload else 3))

    if w % 2 == 1:
        days.append({"d":"MIÉ","title":"Cuestas 8×60\"","type":"interval","pace":Z5,"dist":km(7 if not deload else 5),
            "steps":[
                warm(2, Z2, "Calentamiento"),
                main_reps(8, "60\" cuesta", Z5, "bajada trotando muy suave (~90\")", "Serie: 8 × 60\" en cuesta"),
                cool(1.5, Z1, "Enfriamiento"),
            ],
            "detail":f"Busca una cuesta de 4-6% que dure ~60-80m. Esfuerzo Z5 (170-180 FC), sube fuerte sin perder técnica. {total_line(7 if not deload else 5)}"})
    else:
        days.append({"d":"MIÉ","title":"6×400m","type":"interval","pace":Z5,"dist":km(7 if not deload else 5),
            "steps":[
                warm(2, Z2, "Calentamiento"),
                main_reps(6, "400m", Z5, "400m trote muy suave (~2')", "Serie: 6 × 400m"),
                cool(1.5, Z1, "Enfriamiento"),
            ],
            "detail":f"400m a {Z5}/km (ritmo ~1:47-1:51 por 400m). Recuperación trotando, no caminando. {total_line(7 if not deload else 5)}"})

    days.append(strength_plus_run("JUE", "B", 3 if not deload else 3))

    days.append({"d":"VIE","title":"Z2 suave","type":"ez","pace":Z2,"dist":"35-40 min",
        "steps":[
            warm(1.5, Z2, "Inicio"),
            main_continuous((6 if not deload else 5)-3, Z2, "Cuerpo"),
            cool(1.5, Z1, "Final"),
        ],
        "detail":"FC<145. Día de transición antes del long run del sábado. " + total_line(6 if not deload else 5)})

    if deload:
        days.append({"d":"SÁB","title":"Long Run de recuperación","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo del rodaje"), cool(2, Z1, "Final")],
            "detail":f"Ritmo cómodo toda la distancia, FC<150. Semana de descarga: recupera del bloque anterior, sin prisa. {total_line(lr)}"})
    else:
        days.append({"d":"SÁB","title":"Long Run progresivo","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo del rodaje"), cool(2, Z1, "Final")],
            "detail":f"Ritmo cómodo, FC<150. Termina sintiéndote capaz de seguir 2-3km más — esa es la sensación correcta. {total_line(lr)}"})

    days.append(sunday_optional(5 if not deload else 4))

    weeks.append({
        "num": w, "block": 1, "phase": 1, "phase_name": "Behobia · Fase 1 — Base aeróbica",
        "weekly_km": vol_phase1[i], "long_run": lr,
        "focus": "Adaptación de tendones y articulaciones al volumen. Fuerza martes y jueves. Progresión gradual del long run (14→16km) con incrementos de 5-10%.",
        "deload": deload, "days": days
    })

print(f"Fase 1 generada: {len(weeks)} semanas")

# ---- FASE 2: semanas 7-14, desarrollo de ritmo ----
# Cargas revisadas: incrementos 5-10%, deload en S10 y S14
lr_phase2 = [17, 18, 18, 17, 18, 19, 20, 17]
vol_phase2 = [43, 46, 49, 45, 47, 51, 54, 46]
deload_p2 = [3, 7]  # week 10, week 14

for i in range(8):
    w = i+7
    lr = lr_phase2[i]
    deload = i in deload_p2

    days = []
    days.append(rest_day("LUN"))

    days.append(strength_plus_run("MAR", "A", 4 if not deload else 3))

    if deload:
        days.append({"d":"MIÉ","title":"Z2 + strides","type":"ez","pace":Z2,"dist":km(6),
            "steps":[warm(1.5, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), main_reps(4, "20\"", "<4:27", "40\" trote suave", "Strides finales")],
            "detail":"Semana de descarga: sin intervalos esta semana, solo activación. " + total_line(6)})
    else:
        if w % 2 == 1:
            days.append({"d":"MIÉ","title":"5×1000m","type":"interval","pace":Z4,"dist":km(11),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(5, "1000m", Z4, "90\" trote suave", "Serie: 5 × 1000m"), cool(2, Z1, "Enfriamiento")],
                "detail":f"1000m a {Z4}/km (~4:44-5:03 cada km), FC 160-175. Recuperación trotando, no parado. {total_line(11)}"})
        else:
            days.append({"d":"MIÉ","title":"Fartlek 6×(3'/2')","type":"interval","pace":Z4,"dist":km(11),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(6, "3' fuerte", Z4, "2' trote suave (Z1-Z2)", "Fartlek: 6 × (3' fuerte / 2' suave)"), cool(2, Z1, "Enfriamiento")],
                "detail":f"3' a {Z4}/km, FC 160-175, seguido de 2' de trote de recuperación. {total_line(11)}"})

    days.append(strength_plus_run("JUE", "B", 4 if not deload else 3))

    days.append({"d":"VIE","title":"Recovery suave","type":"ez","pace":Z1,"dist":"25-30 min",
        "steps":[{"label":"Recorrido completo","detail":f"5km continuos a {Z1}/km · FC <130"}],
        "detail":"Solo regeneración activa, deja las piernas listas para el long run del sábado. " + total_line(5)})

    last_km = min(5, 3 + (w-7)//2)
    if deload:
        days.append({"d":"SÁB","title":"Long Run de descarga","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":f"Semana de descarga: todo suave, sin ritmo final. FC<150. {total_line(lr)}"})
    else:
        days.append({"d":"SÁB","title":"Long Run + ritmo final","type":"long","pace":f"{Z2_LR} → {last_km}km a {RACE_BEHOBIA}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-last_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {last_km}km a ritmo Behobia","detail":f"{last_km} km a {RACE_BEHOBIA}/km · FC 150-163 · simula final de carrera"},
            ],
            "detail":f"Primeros {lr-last_km}km a FC<150. Los últimos {last_km}km suben a ritmo objetivo — sin recuperación entre tramos. {total_line(lr)}"})

    days.append(sunday_optional(5 if not deload else 4))

    weeks.append({
        "num": w, "block": 1, "phase": 2, "phase_name": "Behobia · Fase 2 — Desarrollo de ritmo",
        "weekly_km": vol_phase2[i], "long_run": lr,
        "focus": "Subir volumen progresivamente (incrementos 5-10%) + introducir ritmo específico en el long run del sábado.",
        "deload": deload, "days": days
    })

print(f"Fase 2 añadida, total: {len(weeks)} semanas")

# ---- FASE 3: semanas 15-18, específico Behobia ----
# Cargas revisadas: pico reducido de 64 a 61km, LR max 21 (antes 22)
lr_phase3 = [18, 20, 21, 17]
vol_phase3 = [48, 52, 55, 44]

for i in range(4):
    w = i+15
    lr = lr_phase3[i]
    deload = i == 3

    days = []
    days.append(rest_day("LUN", "Movilidad + foam roller."))

    days.append(strength_plus_run("MAR", "C", 4 if not deload else 3))

    if deload:
        days.append({"d":"MIÉ","title":"2×3km a ritmo Behobia","type":"tempo","pace":RACE_BEHOBIA,"dist":km(9),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(2, "3km", RACE_BEHOBIA, "3' caminando + trote suave", "Serie: 2 × 3km a ritmo Behobia"), cool(1, Z1, "Enfriamiento")],
            "detail":f"Última semana antes del taper: reduce volumen, mantén calidad. {total_line(9)}"})
    else:
        days.append({"d":"MIÉ","title":"6×800m race pace+","type":"interval","pace":"4:44-4:58","dist":km(11),
            "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(6, "800m", "4:44-4:58", "2' trote suave", "Serie: 6 × 800m"), cool(2, Z1, "Enfriamiento")],
            "detail":f"Ligeramente más rápido que ritmo carrera, FC 165-175. {total_line(11)}"})

    days.append(strength_plus_run("JUE", "A", 4 if not deload else 3))

    days.append({"d":"VIE","title":"Z2 con desnivel" if not deload else "Z2 suave","type":"ez","pace":Z2,"dist":"35-40 min",
        "steps":[warm(2, Z2, "Inicio"), main_continuous((7 if not deload else 5)-3, Z2, "Cuerpo"), cool(1, Z1, "Final")],
        "detail":(f"Busca rutas con desnivel acumulado (Casa de Campo / Monte de El Pardo). FC más alta en subidas — normal. " if not deload else "Última semana antes del taper: reduce intensidad. ") + total_line(7 if not deload else 5)})

    if deload:
        days.append({"d":"SÁB","title":"Long Run suave (descarga)","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":f"Todo suave, sin ritmo. Última semana de carga alta — recupera antes del taper. {total_line(lr)}"})
    else:
        days.append({"d":"SÁB","title":"Long Run mixto (clave)","type":"long","pace":f"{Z2_LR} → 7km a {RACE_BEHOBIA}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-7, Z2_LR, "Cuerpo suave"),
                {"label":"Últimos 7km a ritmo Behobia","detail":f"7 km a {RACE_BEHOBIA}/km · FC 150-163 · sin pausa entre tramos"},
            ],
            "detail":f"⭐ Esta es tu sesión más dura del plan — simula la carrera real con fatiga acumulada. {total_line(lr)}"})

    days.append(sunday_optional(5 if not deload else 4))

    weeks.append({
        "num": w, "block": 1, "phase": 3, "phase_name": "Behobia · Fase 3 — Específico carrera",
        "weekly_km": vol_phase3[i], "long_run": lr,
        "focus": "Trabajo directo a ritmo de carrera, desnivel y prevención con fuerza excéntrica. Pico de volumen moderado (61km) para evitar sobrecarga antes del taper.",
        "deload": deload, "days": days
    })

print(f"Fase 3 añadida, total: {len(weeks)} semanas")


# ---- FASE 4: semanas 19-21, taper ----
# Note: week 21 is RACE WEEK - Behobia is on Sunday Nov 8.
# Long run normally Saturday, but race week the race itself IS Sunday.
taper_data = [
    {"vol":36,"lr":14,"last":3},
    {"vol":24,"lr":10,"last":2},
    {"vol":15,"lr":None,"last":0},
]

for i in range(3):
    w = i+19
    data = taper_data[i]
    days = []
    days.append(rest_day("LUN", "Movilidad suave."))

    if w == 21:
        # Race week: Behobia is Sunday Nov 8.
        days.append({"d":"MAR","title":"Z2 muy suave","type":"ez","pace":Z2,"dist":km(5),
            "steps":[warm(1, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), cool(1, Z1, "Final")],
            "detail":"Activación ligera. FC<145. " + total_line(5)})
        days.append({"d":"MIÉ","title":"Activación 1km a ritmo carrera","type":"tempo","pace":RACE_BEHOBIA,"dist":km(4),
            "steps":[warm(1.5, Z2, "Calentamiento"), {"label":"Serie","detail":f"1km a {RACE_BEHOBIA}/km · solo recordar la sensación"}, cool(1.5, Z1, "Enfriamiento")],
            "detail":"Nada de fatiga, esto es solo activación neuromuscular. " + total_line(4)})
        days.append(rest_day("JUE", "Empieza a pensar en la logística: bolsa, dorsal, transporte a Donosti."))
        days.append({"d":"VIE","title":"3km muy suave + estiramientos","type":"ez","pace":"5:50/km","dist":km(3),
            "steps":[{"label":"Recorrido","detail":"3km a 5:50/km muy relajado"},{"label":"Después","detail":"Estiramientos suaves 10' + foam roller"}],
            "detail":"Solo piernas activas. " + total_line(3)})
        days.append(rest_day("SÁB", "Hidratación, pasta/arroz en la cena, acostarse pronto. Prepara ropa, dorsal, geles, alfileres, vaselina. Mañana es el gran día."))
        days.append({"d":"DOM","title":"🏁 BEHOBIA-SAN SEBASTIÁN","type":"race","pace":RACE_BEHOBIA,"dist":"20 km · Meta 1h41-1h44",
            "steps":[
                {"label":"Km 0-5","detail":f"Sal CONSERVADOR — incluso 5-10\"/km más lento que {RACE_BEHOBIA}. No te dejes llevar por la multitud."},
                {"label":"Km 5-15","detail":f"Asienta el ritmo objetivo {RACE_BEHOBIA}/km. Tramo Behobia→Rentería es el más exigente — controla esfuerzo, no ritmo."},
                {"label":"Km 15-20","detail":"Si llegas bien, exprime lo que tengas. Si no, mantén ritmo y no pares — el aliento de meta en San Sebastián merece la pena."},
                {"label":"Nutrición","detail":"Gel o dátiles en km 8-10 y km 14-15 (lo que hayas probado en los long runs)."},
            ],
            "detail":"¡A disfrutarlo, te lo has ganado! 21 semanas de trabajo te respaldan."})
    else:
        # Normal taper week structure: Tue/Thu strength (reduced), Wed activation, Sat long run, Sun rest
        days.append(strength_plus_run("MAR", "A", 3))

        days.append({"d":"MIÉ","title":f"Activación: 2×{'2km' if w==19 else '1km'} a ritmo carrera","type":"tempo","pace":RACE_BEHOBIA,"dist":km(6 if w==19 else 5),
            "steps":[warm(2 if w==19 else 1.5, Z2, "Calentamiento"), main_reps(2, "2km" if w==19 else "1km", RACE_BEHOBIA, "2' trote suave", f"Serie: 2 × {'2km' if w==19 else '1km'}"), cool(1, Z1, "Enfriamiento")],
            "detail":"Recordar al cuerpo el ritmo objetivo sin generar fatiga. " + total_line(6 if w==19 else 5)})

        days.append({"d":"JUE","title":"Fuerza B (ligera)","type":"strength","pace":"Sesión B","dist":"25-30 min",
            "steps":STRENGTH_B_STEPS[:4],
            "detail":"Versión reducida — solo los 4 primeros ejercicios, cargas ligeras. Mantener activación sin generar fatiga."})

        days.append({"d":"VIE","title":"Activación piernas","type":"ez","pace":"5:50/km + 3 strides","dist":km(4),
            "steps":[{"label":"Rodaje","detail":"4km a 5:50/km muy relajado"}, main_reps(3, "20\"", "<4:27", "40\" caminar", "Strides finales")],
            "detail":"Activación neuromuscular ligera. " + total_line(4)})

        if data["last"]:
            steps = [warm(2, Z2_LR, "Inicio"), main_continuous(data["lr"]-2-data["last"], Z2_LR, "Cuerpo"),
                     {"label":f"Últimos {data['last']}km a ritmo Behobia","detail":f"{data['last']}km a {RACE_BEHOBIA}/km · solo para recordar la sensación, sin fatiga"}]
            pace_str = f"{Z2_LR} → {data['last']}km a {RACE_BEHOBIA}"
        else:
            steps = [warm(2, Z2_LR, "Inicio"), main_continuous(data["lr"]-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")]
            pace_str = Z2_LR
        days.append({"d":"SÁB","title":"Long Run de tapering","type":"long","pace":pace_str,"dist":km(data["lr"]),
            "steps":steps,
            "detail":"Ritmo cómodo, sin buscar sensaciones fuertes. " + total_line(data["lr"])})

        days.append(rest_day("DOM", "Descanso total. Hidratación y buena alimentación. La semana que viene es la de carrera."))

    weeks.append({
        "num": w, "block": 1, "phase": 4, "phase_name": "Behobia · Fase 4 — Tapering" if w<21 else "🏁 SEMANA DE CARRERA BEHOBIA",
        "weekly_km": data["vol"], "long_run": data["lr"] if data["lr"] else 20,
        "focus": "Reducir carga progresivamente, mantener frescura, llegar fuerte y descansado al 8N." if w<21 else "Descansar, viajar, y disfrutar de la carrera. El trabajo ya está hecho.",
        "deload": False, "days": days
    })

print(f"Fase 4 añadida, total: {len(weeks)} semanas")


# ================================================================
# BLOQUE 2: TRANSICIÓN + BASE MARATÓN — semanas 22-33 (12 semanas)
# Getafe media maratón (31 ene 2027) = semana 33
# Nueva estructura: Mar/Jue fuerza, Mié intervalos, Sáb long run, Dom opcional/descanso
# ================================================================

# ---- Semana 22: Recovery total post-Behobia ----
w = 22
days = []
days.append(rest_day("LUN", "Descanso total post-carrera. Piernas cargadas, es normal. Date el premio de no pensar en entrenar."))
days.append({"d":"MAR","title":"Caminar / Z1 muy suave","type":"ez","pace":Z1,"dist":km(4),
    "steps":[{"label":"Opcional","detail":f"4km muy suave a {Z1}/km, o simplemente caminar 30-40min"}],
    "detail":"Solo si las piernas lo piden. Sin presión, sin reloj. " + total_line(4)})
days.append(rest_day("MIÉ", "Descanso. Foam roller, estiramientos, baño de agua fría/caliente si te gusta."))
days.append({"d":"JUE","title":"Z1-Z2 suave","type":"ez","pace":Z1,"dist":km(5),
    "steps":[warm(1, Z1, "Inicio"), main_continuous(3, Z1, "Cuerpo"), cool(1, Z1, "Final")],
    "detail":"Empezar a reactivar piernas. Sin objetivo de ritmo. " + total_line(5)})
days.append(rest_day("VIE", "Descanso."))
days.append({"d":"SÁB","title":"Z2 muy suave","type":"long","pace":Z2_LR,"dist":km(10),
    "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(6, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
    "detail":"Recuperación activa. Sin prisa, sin ritmo objetivo — solo sentir las piernas otra vez. " + total_line(10)})
days.append(sunday_rest())

weeks.append({
    "num": w, "block": 2, "phase": 0, "phase_name": "Transición · Recovery post-Behobia",
    "weekly_km": 25, "long_run": 10,
    "focus": "Recuperación activa total tras Behobia. Sin entrenamientos exigentes. El cuerpo necesita asimilar 21 semanas de carga.",
    "deload": True, "days": days, "milestone": "Post-Behobia"
})

# ---- Semanas 23-27: Reconstrucción base (5 semanas) ----
# Rebote suavizado tras recovery: S22(25km)->S23 ahora +32% en vez de +68%
lr_base = [13, 14, 15, 16, 14]  # week 27 = deload (Navidad)
vol_base = [27, 32, 36, 40, 34]

for i in range(5):
    w = i+23
    lr = lr_base[i]
    deload = (i == 4)
    days = []
    days.append(rest_day("LUN"))

    days.append(strength_plus_run("MAR", "A", 3 if not deload else 3))

    if w % 2 == 1:
        days.append({"d":"MIÉ","title":"Cuestas 6×60\"","type":"interval","pace":Z5,"dist":km(7 if not deload else 5),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(6, "60\" cuesta", Z5, "bajada trotando (~90\")", "Serie: 6 × 60\" cuesta"), cool(1.5, Z1, "Enfriamiento")],
            "detail":f"Reintroducción gradual de intensidad. Esfuerzo controlado, sin buscar máximos. {total_line(7 if not deload else 5)}"})
    else:
        days.append({"d":"MIÉ","title":"6×400m","type":"interval","pace":Z5,"dist":km(7 if not deload else 5),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(6, "400m", Z5, "400m trote suave (~2')", "Serie: 6 × 400m"), cool(1.5, Z1, "Enfriamiento")],
            "detail":f"400m a {Z5}/km. {total_line(7 if not deload else 5)}"})

    days.append(strength_plus_run("JUE", "B", 3 if not deload else 3))

    days.append({"d":"VIE","title":"Z2 suave","type":"ez","pace":Z2,"dist":"35-40 min",
        "steps":[warm(1.5, Z2, "Inicio"), main_continuous(2, Z2, "Cuerpo"), cool(1.5, Z1, "Final")],
        "detail":"FC<145, transición hacia el long run del sábado. " + total_line(5)})

    days.append({"d":"SÁB","title":"Long Run progresivo" if not deload else "Long Run de descarga (Navidad)","type":"long","pace":Z2_LR,"dist":km(lr),
        "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
        "detail":f"Ritmo cómodo, FC<150. {'Semana de fiestas — disfruta, no fuerces.' if deload else 'Reconstruyendo la resistencia de base.'} {total_line(lr)}"})

    days.append(sunday_optional(5 if not deload else 4))

    notes = ""
    if w == 27:
        notes = " (Semana de Navidad — volumen reducido a propósito)"

    weeks.append({
        "num": w, "block": 2, "phase": 1, "phase_name": f"Transición · Reconstrucción base{notes}",
        "weekly_km": vol_base[i], "long_run": lr,
        "focus": "Reconstruir la base aeróbica tras Behobia con incrementos suaves (~10-15% desde el recovery), preparando el terreno para el bloque de maratón." + (" Semana de Navidad: prioriza el descanso y disfruta las fiestas." if deload else ""),
        "deload": deload, "days": days
    })

print(f"Bloque 2 (parte 1) añadido, total: {len(weeks)} semanas")


# ---- Semanas 28-32: Construcción específica maratón temprana (5 semanas) ----
# Rebote post-Navidad suavizado: S27(38km)->S28 ahora +8% en vez de +19%
# Long run: 15 -> 19, mini-taper en semana 32 antes de Getafe
lr_build = [15, 16, 17, 19, 15]  # week 32 = mini-taper before Getafe
vol_build = [35, 39, 43, 47, 34]

for i in range(5):
    w = i+28
    lr = lr_build[i]
    is_pretaper = (i == 4)  # week 32

    days = []
    days.append(rest_day("LUN"))
    days.append(strength_plus_run("MAR", "A", 3 if not is_pretaper else 3))

    if is_pretaper:
        days.append({"d":"MIÉ","title":"Z2 + strides","type":"ez","pace":Z2,"dist":km(6),
            "steps":[warm(1.5, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), main_reps(4, "20\"", "<4:27", "40\" trote", "Strides finales")],
            "detail":"Mini-taper antes de Getafe: sin intervalos esta semana, solo activación. " + total_line(6)})
    else:
        if w % 2 == 0:
            days.append({"d":"MIÉ","title":"5×1000m a ritmo maratón+","type":"interval","pace":Z4,"dist":km(11),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(5, "1000m", Z4, "90\" trote suave", "Serie: 5 × 1000m"), cool(2, Z1, "Enfriamiento")],
                "detail":f"1000m a {Z4}/km, FC 160-175. {total_line(11)}"})
        else:
            days.append({"d":"MIÉ","title":"Fartlek 6×(3'/2')","type":"interval","pace":Z4,"dist":km(11),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(6, "3' fuerte", Z4, "2' trote suave", "Fartlek: 6 × (3'/2')"), cool(2, Z1, "Enfriamiento")],
                "detail":f"3' a {Z4}/km seguido de 2' recuperación. {total_line(11)}"})

    days.append(strength_plus_run("JUE", "B", 3 if not is_pretaper else 3))

    if is_pretaper:
        days.append(rest_day("VIE", "Descanso completo antes de Getafe — llega fresco."))
    else:
        days.append({"d":"VIE","title":"Recovery Z1","type":"ez","pace":Z1,"dist":km(5),
            "steps":[{"label":"Trote de recuperación","detail":f"25-30 min a FC {FC_Z1} · ritmo orientativo {Z1}/km"}],
            "detail":"Regeneración activa para el long run. FC por debajo de 124 toda la sesión."})

    if is_pretaper:
        days.append({"d":"SÁB","title":"Long Run suave (pre-Getafe)","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":f"Reducción de volumen — llega a Getafe con piernas frescas. {total_line(lr)}"})
    else:
        last_km = 2 + i  # progresivo: 2, 3, 4km a ritmo tempo
        days.append({"d":"SÁB","title":"Long Run + ritmo final","type":"long","pace":f"{Z2_LR} → {last_km}km a {Z3}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-last_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {last_km}km a ritmo tempo","detail":f"{last_km}km a {Z3}/km · FC 150-163"},
            ],
            "detail":f"Introduciendo progresivamente trabajo a ritmo más exigente en el long run, preparando el cuerpo para el ritmo de maratón (se calibrará tras Getafe). {total_line(lr)}"})

    if is_pretaper:
        days.append(rest_day("DOM", "Descanso total. Mañana toca disfrutar de Getafe con tu amigo."))
    else:
        days.append(sunday_optional(5))

    weeks.append({
        "num": w, "block": 2, "phase": 2, "phase_name": "Transición · Construcción específica" if not is_pretaper else "Transición · Mini-taper pre-Getafe",
        "weekly_km": vol_build[i], "long_run": lr,
        "focus": "Construir resistencia específica para el maratón con incrementos suaves, usando Getafe como punto de control." if not is_pretaper else "Reducir carga para llegar fresco a la media maratón de Getafe (31 ene).",
        "deload": is_pretaper, "days": days
    })

print(f"Semanas 28-32 añadidas, total: {len(weeks)} semanas")

# ---- Semana 33: GETAFE media maratón (31 ene 2027) ----
# Note: Getafe is Sunday Jan 31 -> race day is Sunday this week (not Saturday like normal long run)
w = 33
days = []
days.append(rest_day("LUN", "Descanso total. Llegar fresco a la semana de Getafe."))
days.append({"d":"MAR","title":"Z2 muy suave","type":"ez","pace":Z2,"dist":km(6),
    "steps":[warm(1.5, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), cool(1.5, Z1, "Final")],
    "detail":"FC<145. Mantener soltura sin generar fatiga. " + total_line(6)})
days.append({"d":"MIÉ","title":"Activación 2×1km","type":"tempo","pace":Z3,"dist":km(6),
    "steps":[warm(2, Z2, "Calentamiento"), main_reps(2, "1km", Z3, "2' trote suave", "Serie: 2 × 1km"), cool(1, Z1, "Enfriamiento")],
    "detail":"Activación neuromuscular ligera de cara al domingo. " + total_line(6)})
days.append(rest_day("JUE", "Movilidad suave, foam roller."))
days.append({"d":"VIE","title":"Activación piernas","type":"ez","pace":"5:50/km + 3 strides","dist":km(4),
    "steps":[{"label":"Rodaje","detail":"4km a 5:50/km muy relajado"}, main_reps(3, "20\"", "<4:27", "40\" caminar", "Strides finales")],
    "detail":"Activación neuromuscular ligera. " + total_line(4)})
days.append({"d":"SÁB","title":"Descanso total","type":"rest","steps":[],"total":"0 km",
    "detail":"Hidratación, pasta/arroz en la cena, acostarse pronto. Prepara dorsal y ropa. Getafe es domingo."})
days.append({"d":"DOM","title":"🎯 GETAFE Media Maratón (como Long Run)","type":"long","pace":f"Progresivo: {Z2_LR} → {Z3} → {RACE_BEHOBIA}","dist":"21,1 km",
    "steps":[
        {"label":"Km 0-8","detail":f"A ritmo {Z2_LR}/km — acompañando a tu amigo, conversacional, sin prisa"},
        {"label":"Km 8-16","detail":f"Sube a {Z3}/km si el cuerpo lo pide — sigue siendo controlado"},
        {"label":"Km 16-21","detail":f"Opcional: cierra a ritmo {RACE_BEHOBIA}/km si te sientes bien, o mantén {Z3}/km"},
    ],
    "detail":"⭐ Esta carrera NO es un objetivo de tiempo — es tu long run de 21km con compañía y ambiente de carrera. Aprovecha para practicar nutrición/hidratación de carrera real. Sirve como excelente termómetro de cómo está tu resistencia de cara al maratón."})

weeks.append({
    "num": w, "block": 2, "phase": 3, "phase_name": "🎯 GETAFE · Media Maratón (long run de control)",
    "weekly_km": 41, "long_run": 21.1,
    "focus": "Media maratón de Getafe usada como long run largo con buen ambiente — sin presión de marca, gran oportunidad para practicar el ritmo y la nutrición de cara al maratón de Madrid. La carrera es domingo (no sábado como el resto de long runs).",
    "deload": False, "days": days, "milestone": "Getafe Media Maratón (control)"
})

print(f"Semana 33 (Getafe) añadida, total: {len(weeks)} semanas")


# ================================================================
# BLOQUE 3: MARATÓN DE MADRID — semanas 34-45 (12 semanas, 25 abr 2027)
# ================================================================

# ---- Fase A: semanas 34-38, pico de volumen (5 semanas) ----
# Long run: 17 -> 24km, con S37 como "gran sesion #1" (segundo long run largo de la temporada)
lr_A = [17, 18, 20, 24, 19]
vol_A = [38, 42, 46, 51, 44]
mp_km_A = [3, 5, 7, 11]  # mp_km for non-deload weeks (indices 0-3)

for i in range(5):
    w = i+34
    lr = lr_A[i]
    deload = (i == 4)

    days = []
    days.append(rest_day("LUN", "Recuperación post-Getafe en semana 34. Movilidad + foam roller."))
    days.append(strength_plus_run("MAR", "A", 4 if not deload else 3))

    days.append({"d":"MIÉ","title":f"Tempo continuo {25 + i*2 if not deload else 20}'","type":"tempo","pace":Z3,"dist":km(11 if not deload else 8),
        "steps":[
            warm(2.5, Z2, "Calentamiento"),
            {"label":"Cuerpo principal","detail":f"{25+i*2 if not deload else 20}' continuos a {Z3}/km · FC 152-164"},
            cool(2, Z1, "Enfriamiento"),
        ],
        "detail":f"Construyendo el umbral aeróbico para sostener el ritmo de maratón. {total_line(11 if not deload else 8)}"})

    days.append(strength_plus_run("JUE", "B", 4 if not deload else 3))

    if deload:
        days.append({"d":"VIE","title":"Z2 suave + strides","type":"ez","pace":Z2,"dist":"30-35 min",
            "steps":[z2_block(30), main_reps(4, "20\"", "<4:27", "40\" caminar", "Strides finales"), cool()],
            "detail":"FC 124-143. Descarga: reduce volumen e intensidad. Los strides al final activan el sistema neuromuscular."})
    else:
        days.append({"d":"VIE","title":"Recovery Z1","type":"ez","pace":Z1,"dist":"25 min",
            "steps":[{"label":"Trote de recuperación","detail":f"25-30 min a FC {FC_Z1} · ritmo orientativo {Z1}/km"}],
            "detail":"Regeneración activa para el long run. FC por debajo de 124 toda la sesión."})

    if deload:
        days.append({"d":"SÁB","title":"Long Run de descarga","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":f"Semana de descarga: todo suave, sin ritmo. FC<150. {total_line(lr)}"})
    else:
        mp_km = mp_km_A[i]
        is_big1 = (i == 3)  # week 37 - first "big" long run of the season
        title = f"🏆 Long Run amplio: {lr}km + {mp_km}km a MP" if is_big1 else f"Long Run + {mp_km}km a Ritmo Maratón"
        detail = (f"⭐ Segunda sesión larga clave de la temporada (la primera desde Getafe). Practica nutrición y equipo de carrera. Tras esta semana viene una descarga — aprovecha para asimilar. {total_line(lr)}"
                  if is_big1 else
                  f"⭐ El ritmo de maratón (MP={MP}/km) es una primera estimación — se recalibrará tras Getafe con tu tiempo real. La sensación debe ser 'podría mantener esto durante horas'. {total_line(lr)}")
        days.append({"d":"SÁB","title":title,"type":"long","pace":f"{Z2_LR} → {mp_km}km a {MP}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-mp_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {mp_km}km a Ritmo Maratón (MP)","detail":f"{mp_km}km a {MP}/km · FC objetivo según sensaciones, debe sentirse 'sostenible'"},
            ],
            "detail":detail})

    days.append(sunday_optional(5 if not deload else 4))

    weeks.append({
        "num": w, "block": 3, "phase": 1, "phase_name": "Maratón Madrid · Fase A — Pico de volumen",
        "weekly_km": vol_A[i], "long_run": lr,
        "focus": "Construir el pico de volumen de la temporada con incrementos suaves e introducir progresivamente el Ritmo Maratón (MP) en los long runs.",
        "deload": deload, "days": days
    })

print(f"Fase A añadida, total: {len(weeks)} semanas")


# ---- Fase B: semanas 39-42, específico maratón (4 semanas) ----
# Rebote post-deload suavizado: S38(47km)->S39 now +13% (was +32%)
# Long run: 25 -> 31km (slightly reduced from 26->32 to smooth progression)
lr_B = [20, 22, 24, 27]
vol_B = [47, 52, 56, 52]
mp_km_B = [7, 8, 10, 13]

for i in range(4):
    w = i+39
    lr = lr_B[i]
    mp_km = mp_km_B[i]
    is_peak = (i == 3)  # week 42 - the big one

    days = []
    days.append(rest_day("LUN", "Movilidad + foam roller. Cuidado extra con la recuperación en este bloque de máxima carga."))
    days.append(strength_plus_run("MAR", "C", 4 if not is_peak else 3))

    days.append({"d":"MIÉ","title":f"Tempo continuo {30 if not is_peak else 25}'","type":"tempo","pace":Z3,"dist":km(12 if not is_peak else 10),
        "steps":[
            warm(2.5, Z2, "Calentamiento"),
            {"label":"Cuerpo principal","detail":f"{30 if not is_peak else 25}' continuos a {Z3}/km · FC 152-164"},
            cool(2, Z1, "Enfriamiento"),
        ],
        "detail":("Semana del long run más largo — reduce ligeramente la intensidad del tempo. " if is_peak else "") + f"{total_line(12 if not is_peak else 10)}"})

    days.append(strength_plus_run("JUE", "A", 4 if not is_peak else 3))

    if is_peak:
        days.append(rest_day("VIE", "Descanso extra antes del long run de 31km — el más importante del plan. Hidrátate bien hoy."))
    else:
        days.append({"d":"VIE","title":"Recovery Z1","type":"ez","pace":Z1,"dist":"25 min",
            "steps":[{"label":"Trote de recuperación","detail":f"25-30 min a FC {FC_Z1} · ritmo orientativo {Z1}/km"}],
            "detail":"Regeneración activa para el long run. FC por debajo de 124 toda la sesión."})

    if is_peak:
        days.append({"d":"SÁB","title":f"🏆 Long Run más largo: {lr}km + {mp_km}km a MP","type":"long","pace":f"{Z2_LR} → {mp_km}km a {MP}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-mp_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {mp_km}km a Ritmo Maratón (MP)","detail":f"{mp_km}km a {MP}/km · simula la segunda mitad del maratón"},
            ],
            "detail":f"⭐⭐ LA SESIÓN CLAVE DE TODO EL PLAN. Practica aquí TODO lo de carrera: ropa, calzado, geles cada 45', hidratación. {total_line(lr)} · Si llega a costar mucho, no pasa nada — es la sesión más exigente y es normal sufrir."})
    else:
        days.append({"d":"SÁB","title":f"Long Run + {mp_km}km a Ritmo Maratón","type":"long","pace":f"{Z2_LR} → {mp_km}km a {MP}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-mp_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {mp_km}km a Ritmo Maratón (MP)","detail":f"{mp_km}km a {MP}/km · FC objetivo según sensaciones"},
            ],
            "detail":f"Practica nutrición: gel cada 45'-50' desde el inicio del tramo a MP. {total_line(lr)}"})

    if is_peak:
        days.append({"d":"DOM","title":"Z1 recuperación post-long run","type":"ez","pace":Z1,"dist":km(3),
            "steps":[{"label":"Opcional","detail":f"3km muy suave a {Z1}/km, o caminar 30min"}],
            "detail":"Recuperación activa tras la sesión más dura del plan. Solo si las piernas lo agradecen. " + total_line(3)})
    else:
        days.append(sunday_optional(5))

    weeks.append({
        "num": w, "block": 3, "phase": 2, "phase_name": "Maratón Madrid · Fase B — Específico maratón" if not is_peak else "Maratón Madrid · Fase B — ⭐ Pico del plan",
        "weekly_km": vol_B[i], "long_run": lr,
        "focus": "Maximizar el tiempo a Ritmo Maratón en el long run. Practicar toda la logística de carrera (nutrición, equipo, calzado)." if not is_peak else "El long run de 31km con 17km a MP es la sesión más importante de toda la temporada — simula la segunda mitad del maratón con fatiga real.",
        "deload": False, "days": days
    })

print(f"Fase B añadida, total: {len(weeks)} semanas")

# ---- Fase C: semanas 43-45, taper + carrera (3 semanas) ----
# Peak was 62 (week 41). Taper to ~75%, 55%, race week ~35%
taper3_data = [
    {"vol":46,"lr":18,"mp":6},   # week 43
    {"vol":34,"lr":12,"mp":4},   # week 44
    {"vol":22,"lr":None,"mp":0}, # week 45: race week
]

for i in range(3):
    w = i+43
    data = taper3_data[i]
    days = []
    days.append(rest_day("LUN", "Movilidad + foam roller."))

    if w == 45:
        # Race week: Marathon is Sunday Apr 25
        days.append(strength_plus_run("MAR", "A", 3))

        days.append({"d":"MIÉ","title":"Activación 3×1km a MP","type":"tempo","pace":MP,"dist":km(7),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(3, "1km", MP, "90\" trote suave", "Serie: 3 × 1km a ritmo maratón"), cool(1, Z1, "Enfriamiento")],
            "detail":"Última activación a ritmo objetivo — recordar la sensación sin generar fatiga. " + total_line(7)})

        days.append({"d":"JUE","title":"Fuerza B (muy ligera)","type":"strength","pace":"Sesión B","dist":"15-20 min",
            "steps":STRENGTH_B_STEPS[:3],
            "detail":"Versión muy reducida — solo 3 ejercicios, cargas ligeras. Mantener activación sin generar fatiga 3 días antes."})

        days.append({"d":"VIE","title":"3km muy suave + estiramientos","type":"ez","pace":"5:50/km","dist":km(3),
            "steps":[{"label":"Recorrido","detail":"3km a 5:50/km muy relajado"},{"label":"Después","detail":"Estiramientos suaves + foam roller"}],
            "detail":"Activación ligera. " + total_line(3)})

        days.append({"d":"SÁB","title":"Descanso total","type":"rest","steps":[],"total":"0 km",
            "detail":"Descanso total. Carga de carbohidratos, hidratación. Repasa el plan de ritmos y nutrición. Acuéstate pronto — la maratón es domingo por la mañana."})

        days.append({"d":"DOM","title":"🏆 MARATÓN DE MADRID","type":"race","pace":MP,"dist":"42,2 km",
            "steps":[
                {"label":"Km 0-5","detail":f"MUY CONSERVADOR — 10-15\"/km más lento que {MP}. El error más común es salir rápido."},
                {"label":"Km 5-30","detail":f"Asienta {MP}/km. Gel cada 45'. Hidratación en cada avituallamiento (pequeños sorbos)."},
                {"label":"Km 30-38","detail":"La parte dura. Si el ritmo se resiente, prioriza mantener el esfuerzo constante sobre el ritmo exacto. Aquí se decide la carrera."},
                {"label":"Km 38-42","detail":"Si quedan piernas, exprime. Si no, mantén la cadencia y cuenta los metros. Esto es lo que llevas meses entrenando."},
            ],
            "detail":"🎉 21 + 12 + 12 = 45 semanas de trabajo. Disfrútalo — cada km duro de este plan está aquí para este momento."})
    else:
        days.append(strength_plus_run("MAR", "A", 3 if w==43 else 3))

        mp_reps = 2
        rep_dist = "2km" if w==43 else "1.5km"
        days.append({"d":"MIÉ","title":f"Activación: {mp_reps}×{rep_dist} a MP","type":"tempo","pace":MP,"dist":km(8 if w==43 else 6),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(mp_reps, rep_dist, MP, "2' trote suave", f"Serie: {mp_reps} × {rep_dist} a ritmo maratón"), cool(1.5, Z1, "Enfriamiento")],
            "detail":"Mantener la sensación del ritmo objetivo. " + total_line(8 if w==43 else 6)})

        days.append({"d":"JUE","title":"Fuerza B (ligera)","type":"strength","pace":"Sesión B","dist":"25-30 min",
            "steps":STRENGTH_B_STEPS[:4],
            "detail":"Versión reducida — 4 ejercicios, cargas ligeras."})

        days.append({"d":"VIE","title":"Activación piernas","type":"ez","pace":"5:50/km + 3 strides","dist":km(5 if w==43 else 4),
            "steps":[{"label":"Rodaje","detail":f"{5 if w==43 else 4}km a 5:50/km muy relajado"}, main_reps(3, "20\"", "<4:27", "40\" caminar", "Strides finales")],
            "detail":"Activación neuromuscular ligera. " + total_line(5 if w==43 else 4)})

        days.append({"d":"SÁB","title":f"Long Run de tapering + {data['mp']}km a MP","type":"long","pace":f"{Z2_LR} → {data['mp']}km a {MP}","dist":km(data["lr"]),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(data["lr"]-2-data["mp"], Z2_LR, "Cuerpo"),
                {"label":f"Últimos {data['mp']}km a Ritmo Maratón","detail":f"{data['mp']}km a {MP}/km · recordar la sensación, sin fatiga"},
            ],
            "detail":"Ritmo cómodo, reducción de volumen progresiva. " + total_line(data["lr"])})

        days.append(rest_day("DOM", "Descanso total. Hidratación y buena cena (carbohidratos)."))

    weeks.append({
        "num": w, "block": 3, "phase": 3, "phase_name": "Maratón Madrid · Fase C — Tapering" if w<45 else "🏆 SEMANA DE LA MARATÓN",
        "weekly_km": data["vol"], "long_run": data["lr"] if data["lr"] else 30,
        "focus": "Reducir volumen progresivamente mientras se mantiene la sensación del ritmo objetivo. Llegar fresco, descansado y mentalmente preparado." if w<45 else "Descansar, cargar carbohidratos, organizar logística y disfrutar de la culminación de la temporada: la Maratón de Madrid.",
        "deload": False, "days": days, "milestone": "🏆 MARATÓN DE MADRID" if w==45 else None
    })

print(f"Fase C añadida, total: {len(weeks)} semanas")

# Cleanup None milestone fields for non-milestone weeks
for ww in weeks:
    if "milestone" not in ww:
        ww["milestone"] = None

# Fix week 45 long_run display to represent the marathon distance (42.2km)
for ww in weeks:
    if ww["num"] == 45:
        ww["long_run"] = 42.2


# Fix week 45 long_run display to represent the marathon distance (42.2km)
for ww in weeks:
    if ww["num"] == 45:
        ww["long_run"] = 42.2


if __name__ == "__main__":
    import json
    print("TOTAL WEEKS:", len(weeks))
    with open("weeks_full.json", "w") as f:
        json.dump(weeks, f, ensure_ascii=False, indent=1)
