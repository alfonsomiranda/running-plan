import datetime, json

START = datetime.date(2026, 6, 15)

# Pace zones (min/km as strings) - from Strava 5K 23:58
Z1 = "6:10-6:50"
Z2 = "5:40-6:15"
Z2_LR = "5:45-6:20"
Z3 = "5:04-5:30"
Z4 = "4:44-5:03"
Z5 = "4:27-4:43"
RACE_BEHOBIA = "5:05-5:10"
# Marathon pace: more conservative than Behobia pace (20km vs 42km)
# Behobia target ~5:07/km for 20km -> marathon pace typically 15-25"/km slower
MP = "5:25-5:35"  # Marathon Pace - to be refined after Behobia result

def km(v):
    if isinstance(v, float) and v == int(v):
        v = int(v)
    return f"{v} km"

def warm(dist_km, pace=Z2, label="Calentamiento"):
    return {"label": label, "detail": f"{dist_km} km a {pace}/km · trote suave, FC <140"}

def cool(dist_km, pace=Z1, label="Enfriamiento"):
    return {"label": label, "detail": f"{dist_km} km a {pace}/km · trote muy suave + caminar 2'"}

def main_reps(reps, rep_dist, rep_pace, rec_desc, label="Serie principal"):
    return {"label": label, "detail": f"{reps} × {rep_dist} a {rep_pace}/km · recuperación: {rec_desc}"}

def main_continuous(dist_km, pace, label="Cuerpo principal"):
    return {"label": label, "detail": f"{dist_km} km continuos a {pace}/km · esfuerzo controlado, FC 152-164"}

def total_line(total_km, extra=""):
    return f"Total: ~{total_km} km" + (f" · {extra}" if extra else "")

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

def strength_day(d, session_letter):
    steps_map = {"A": STRENGTH_A_STEPS, "B": STRENGTH_B_STEPS, "C": STRENGTH_C_STEPS}
    dur_map = {"A": "35-40 min", "B": "35-40 min", "C": "25-30 min"}
    note_map = {
        "A": "Ver tabla completa de 'Sesión A' (Piernas+Core) en la pestaña Fuerza.",
        "B": "Ver tabla completa de 'Sesión B' (Cuerpo completo) en la pestaña Fuerza.",
        "C": "Ver tabla completa de 'Sesión C' (Excéntrica) en la pestaña Fuerza. Foco en control, no velocidad.",
    }
    return {"d":d,"title":f"Fuerza {session_letter}","type":"strength","pace":f"Sesión {session_letter}","dist":dur_map[session_letter],
            "steps":steps_map[session_letter], "detail":note_map[session_letter]}

def rest_day(d, detail="Estiramientos suaves opcionales 10 min. Foam roller si tienes."):
    return {"d":d,"title":"Descanso total","type":"rest","steps":[],"total":"0 km","detail":detail}

weeks = []

# ================================================================
# BLOQUE 1: BEHOBIA — semanas 1-21 (8 nov 2026, 20km)
# ================================================================

# ---- FASE 1: semanas 1-6, base aeróbica ----
# AJUSTADO: long run progression now starts at 14 (was 16), more gradual
lr_phase1 = [14, 15, 16, 17, 15, 17]  # week 5 = deload
vol_phase1 = [38, 42, 45, 48, 40, 50]

for i in range(6):
    w = i+1
    lr = lr_phase1[i]
    deload = (i == 4)
    days = []

    days.append(rest_day("LUN"))
    days.append(strength_day("MAR", "A"))

    days.append({"d":"MIÉ","title":"Z2 Rodaje suave","type":"ez","pace":Z2,"dist":km(8 if not deload else 6),
        "steps":[
            warm(2, Z2, "Primeros 2km"),
            main_continuous(4 if not deload else 2, Z2, "Resto del rodaje"),
            cool(2, Z1, "Últimos 2km"),
        ],
        "detail":"FC <145 bpm todo el rodaje. Conversacional, sin esfuerzo. " + total_line(8 if not deload else 6)})

    if w % 2 == 1:
        days.append({"d":"JUE","title":"Cuestas 8×60\"","type":"interval","pace":Z5,"dist":km(7 if not deload else 5),
            "steps":[
                warm(2, Z2, "Calentamiento"),
                main_reps(8, "60\" cuesta", Z5, "bajada trotando muy suave (~90\")", "Serie: 8 × 60\" en cuesta"),
                cool(1.5, Z1, "Enfriamiento"),
            ],
            "detail":f"Busca una cuesta de 4-6% que dure ~60-80m. Esfuerzo Z5 (170-180 FC), sube fuerte sin perder técnica. {total_line(7 if not deload else 5)}"})
    else:
        days.append({"d":"JUE","title":"6×400m","type":"interval","pace":Z5,"dist":km(7 if not deload else 5),
            "steps":[
                warm(2, Z2, "Calentamiento"),
                main_reps(6, "400m", Z5, "400m trote muy suave (~2')", "Serie: 6 × 400m"),
                cool(1.5, Z1, "Enfriamiento"),
            ],
            "detail":f"400m a {Z5}/km (ritmo ~1:47-1:51 por 400m). Recuperación trotando, no caminando. {total_line(7 if not deload else 5)}"})

    days.append(strength_day("VIE", "B"))

    if deload:
        days.append(rest_day("SÁB", "Semana de descarga: recupera bien antes del bloque final de Fase 1."))
    else:
        days.append({"d":"SÁB","title":"Z2 muy suave (opcional)","type":"ez","pace":"5:50-6:20","dist":km(6),
            "steps":[
                warm(1, Z2, "Inicio"),
                main_continuous(4, "5:50-6:20", "Cuerpo del rodaje"),
                cool(1, Z1, "Final"),
            ],
            "detail":"Solo si llegas fresco. Si hay fatiga, descansa. " + total_line(6)})

    if deload:
        days.append({"d":"DOM","title":"Long Run de recuperación","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-4, Z2_LR, "Cuerpo del rodaje"),
                cool(2, Z1, "Final"),
            ],
            "detail":f"Ritmo cómodo toda la distancia, FC<150. Semana de descarga: recupera del bloque anterior, sin prisa. {total_line(lr)}"})
    else:
        days.append({"d":"DOM","title":"Long Run progresivo","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-4, Z2_LR, "Cuerpo del rodaje"),
                cool(2, Z1, "Final"),
            ],
            "detail":f"Ritmo cómodo, FC<150. Termina sintiéndote capaz de seguir 2-3km más — esa es la sensación correcta. {total_line(lr)}"})

    weeks.append({
        "num": w, "block": 1, "phase": 1, "phase_name": "Behobia · Fase 1 — Base aeróbica",
        "weekly_km": vol_phase1[i], "long_run": lr,
        "focus": "Adaptación de tendones y articulaciones al volumen. Construir hábito de fuerza 2x/semana. Progresión más gradual del long run (14→17km).",
        "deload": deload, "days": days
    })

print(f"Fase 1 generada: {len(weeks)} semanas")

# ---- FASE 2: semanas 7-14, desarrollo de ritmo ----
# Long run: starts at 18 (from 17), progresses to 20. Adjusted slightly down from original (18,19,20,18,19,20,20,17)
lr_phase2 = [18, 18, 19, 18, 19, 20, 20, 17]
vol_phase2 = [52, 54, 56, 50, 58, 60, 62, 48]
deload_p2 = [3, 7]  # week 10, week 14

for i in range(8):
    w = i+7
    lr = lr_phase2[i]
    deload = i in deload_p2

    days = []
    days.append(rest_day("LUN", "O paseo/walk muy suave 20-30 min. Movilidad de cadera y tobillo."))

    days.append({"d":"MAR","title":"Z2 + Strides","type":"ez","pace":Z2,"dist":km(9 if not deload else 7),
        "steps":[
            warm(2, Z2, "Calentamiento"),
            main_continuous((9 if not deload else 7)-3, Z2, "Cuerpo del rodaje"),
            main_reps(4, "20\"", "<4:27", "40\" trote suave", "Strides finales"),
            {"label":"Enfriamiento","detail":"1 km muy suave + caminar"},
        ],
        "detail":f"Los strides son progresiones controladas, no sprints máximos. Activación neuromuscular sin generar fatiga. {total_line(9 if not deload else 7)}"})

    tempo_min = 20 + min(10, (w-7)*2)
    tempo_km = round(tempo_min / 5.2, 1)
    total_tempo = 10 if not deload else 8
    days.append({"d":"MIÉ","title":f"Tempo continuo {tempo_min}'","type":"tempo","pace":Z3,"dist":km(total_tempo),
        "steps":[
            warm(2, Z2, "Calentamiento"),
            {"label":"Cuerpo principal","detail":f"{tempo_min}' continuos (~{tempo_km}km) a {Z3}/km · FC 152-164"},
            cool(2 if not deload else 1.5, Z1, "Enfriamiento"),
        ],
        "detail":("Semana de descarga: reduce volumen, mantén calidad. " if deload else "") + f"Esfuerzo 'cómodo-difícil', frases cortas. {total_line(total_tempo)}"})

    days.append({"d":"JUE","title":"Fuerza A + Z2 corto","type":"strength","pace":"Sesión A","dist":"35' + 6km Z2",
        "steps":[
            {"label":"1. Fuerza (35')","detail":"Mismas cargas Sesión A — mantenimiento, no progresión esta semana"},
            {"label":"2. Z2 corto (6km)","detail":f"A continuación, rodaje muy suave a {Z2}/km, FC<140"},
        ],
        "detail":"Fuerza primero (más fresco), luego rodaje de mantenimiento."})

    if deload:
        days.append({"d":"VIE","title":"Z2 suave","type":"ez","pace":Z2,"dist":km(6),
            "steps":[warm(1.5, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), cool(1.5, Z1, "Final")],
            "detail":"Semana de descarga: sin series esta semana. " + total_line(6)})
    else:
        if w % 2 == 1:
            days.append({"d":"VIE","title":"5×1000m","type":"interval","pace":Z4,"dist":km(11),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(5, "1000m", Z4, "90\" trote suave", "Serie: 5 × 1000m"), cool(2, Z1, "Enfriamiento")],
                "detail":f"1000m a {Z4}/km (~4:44-5:03 cada km), FC 160-175. Recuperación trotando, no parado. {total_line(11)}"})
        else:
            days.append({"d":"VIE","title":"Fartlek 6×(3'/2')","type":"interval","pace":Z4,"dist":km(11),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(6, "3' fuerte", Z4, "2' trote suave (Z1-Z2)", "Fartlek: 6 × (3' fuerte / 2' suave)"), cool(2, Z1, "Enfriamiento")],
                "detail":f"3' a {Z4}/km, FC 160-175, seguido de 2' de trote de recuperación. {total_line(11)}"})

    days.append({"d":"SÁB","title":"Recovery Z1","type":"ez","pace":Z1,"dist":km(5),
        "steps":[{"label":"Recorrido completo","detail":f"5km continuos a {Z1}/km · FC <130"}],
        "detail":"Solo regeneración activa, deja las piernas listas para el long run del domingo. " + total_line(5)})

    last_km = min(5, 3 + (w-7)//2)
    if deload:
        days.append({"d":"DOM","title":"Long Run de descarga","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":f"Semana de descarga: todo suave, sin ritmo final. FC<150. {total_line(lr)}"})
    else:
        days.append({"d":"DOM","title":"Long Run + ritmo final","type":"long","pace":f"{Z2_LR} → {last_km}km a {RACE_BEHOBIA}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-last_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {last_km}km a ritmo Behobia","detail":f"{last_km} km a {RACE_BEHOBIA}/km · FC 150-163 · simula final de carrera"},
            ],
            "detail":f"Primeros {lr-last_km}km a FC<150. Los últimos {last_km}km suben a ritmo objetivo — sin recuperación entre tramos. {total_line(lr)}"})

    weeks.append({
        "num": w, "block": 1, "phase": 2, "phase_name": "Behobia · Fase 2 — Desarrollo de ritmo",
        "weekly_km": vol_phase2[i], "long_run": lr,
        "focus": "Subir volumen progresivamente + introducir ritmo específico en el long run.",
        "deload": deload, "days": days
    })

print(f"Fase 2 añadida, total: {len(weeks)} semanas")

# ---- FASE 3: semanas 15-18, específico Behobia ----
lr_phase3 = [20, 21, 22, 18]
vol_phase3 = [58, 62, 64, 45]

for i in range(4):
    w = i+15
    lr = lr_phase3[i]
    deload = i == 3

    days = []
    days.append(rest_day("LUN", "Movilidad + foam roller. Empieza a pensar en logística de carrera si estamos cerca del taper."))

    days.append({"d":"MAR","title":"Z2 con desnivel","type":"ez","pace":Z2,"dist":km(10 if not deload else 7),
        "steps":[warm(2, Z2, "Llano inicial"), main_continuous((10 if not deload else 7)-4, Z2, "Tramo con cuestas"), cool(2, Z1, "Llano final")],
        "detail":f"Busca rutas con desnivel acumulado (Casa de Campo / Monte de El Pardo). FC más alta en subidas — normal, no fuerces el ritmo. {total_line(10 if not deload else 7)}"})

    reps = 3 if not deload else 2
    main_total = reps*3
    days.append({"d":"MIÉ","title":f"{reps}×3km a ritmo Behobia","type":"tempo","pace":RACE_BEHOBIA,"dist":km(main_total+3),
        "steps":[warm(2, Z2, "Calentamiento"), main_reps(reps, "3km", RACE_BEHOBIA, "3' caminando + trote suave", f"Serie: {reps} × 3km a ritmo Behobia"), cool(1, Z1, "Enfriamiento")],
        "detail":f"FC 150-163 durante las series. Esto ES tu ritmo de carrera — memorízalo. {total_line(main_total+3)}"})

    days.append(strength_day("JUE", "C"))

    if deload:
        days.append({"d":"VIE","title":"Z2 suave","type":"ez","pace":Z2,"dist":km(6),
            "steps":[warm(1.5, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), cool(1.5, Z1, "Final")],
            "detail":"Última semana antes del taper: reduce intensidad. " + total_line(6)})
    else:
        days.append({"d":"VIE","title":"6×800m race pace+","type":"interval","pace":"4:44-4:58","dist":km(11),
            "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(6, "800m", "4:44-4:58", "2' trote suave", "Serie: 6 × 800m"), cool(2, Z1, "Enfriamiento")],
            "detail":f"Ligeramente más rápido que ritmo carrera, FC 165-175. {total_line(11)}"})

    days.append({"d":"SÁB","title":"Z1 muy suave","type":"ez","pace":Z1,"dist":km(5),
        "steps":[{"label":"Recorrido completo","detail":f"5km a {Z1}/km · FC <125"}],
        "detail":"Solo mover las piernas, piensa en el domingo. " + total_line(5)})

    if deload:
        days.append({"d":"DOM","title":"Long Run suave (descarga)","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":f"Todo suave, sin ritmo. Última semana de carga alta — recupera antes del taper. {total_line(lr)}"})
    else:
        days.append({"d":"DOM","title":"Long Run mixto (clave)","type":"long","pace":f"{Z2_LR} → 8km a {RACE_BEHOBIA}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-8, Z2_LR, "Cuerpo suave"),
                {"label":"Últimos 8km a ritmo Behobia","detail":f"8 km a {RACE_BEHOBIA}/km · FC 150-163 · sin pausa entre tramos"},
            ],
            "detail":f"⭐ Esta es tu sesión más dura del plan — simula la carrera real con fatiga acumulada. {total_line(lr)}"})

    weeks.append({
        "num": w, "block": 1, "phase": 3, "phase_name": "Behobia · Fase 3 — Específico carrera",
        "weekly_km": vol_phase3[i], "long_run": lr,
        "focus": "Trabajo directo a ritmo de carrera, desnivel y prevención con fuerza excéntrica.",
        "deload": deload, "days": days
    })

print(f"Fase 3 añadida, total: {len(weeks)} semanas")

# ---- FASE 4: semanas 19-21, taper ----
taper_data = [
    {"vol":40,"lr":14,"last":3},
    {"vol":25,"lr":10,"last":2},
    {"vol":15,"lr":None,"last":0},
]

for i in range(3):
    w = i+19
    data = taper_data[i]
    days = []
    days.append(rest_day("LUN", "Movilidad suave."))

    if w == 21:
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
        days.append(rest_day("SÁB", "Hidratación, pasta/arroz en la cena, acostarse pronto. Prepara ropa, dorsal, geles, alfileres, vaselina."))
        days.append({"d":"DOM","title":"🏁 BEHOBIA-SAN SEBASTIÁN","type":"race","pace":RACE_BEHOBIA,"dist":"20 km · Meta 1h41-1h44",
            "steps":[
                {"label":"Km 0-5","detail":f"Sal CONSERVADOR — incluso 5-10\"/km más lento que {RACE_BEHOBIA}. No te dejes llevar por la multitud."},
                {"label":"Km 5-15","detail":f"Asienta el ritmo objetivo {RACE_BEHOBIA}/km. Tramo Behobia→Rentería es el más exigente — controla esfuerzo, no ritmo."},
                {"label":"Km 15-20","detail":"Si llegas bien, exprime lo que tengas. Si no, mantén ritmo y no pares — el aliento de meta en San Sebastián merece la pena."},
                {"label":"Nutrición","detail":"Gel o dátiles en km 8-10 y km 14-15 (lo que hayas probado en los long runs)."},
            ],
            "detail":"¡A disfrutarlo, te lo has ganado! 21 semanas de trabajo te respaldan."})
    else:
        days.append({"d":"MAR","title":"Z2 suave","type":"ez","pace":Z2,"dist":km(8 if w==19 else 6),
            "steps":[warm(1.5, Z2, "Inicio"), main_continuous((8 if w==19 else 6)-3, Z2, "Cuerpo"), cool(1.5, Z1, "Final")],
            "detail":"FC<145. Reducir volumen, mantener frescura de piernas. " + total_line(8 if w==19 else 6)})

        reps_taper = 2
        rep_dist = "2km" if w==19 else "1km"
        rep_total = 4 if w==19 else 2
        days.append({"d":"MIÉ","title":f"Activación: {reps_taper}×{rep_dist} a ritmo carrera","type":"tempo","pace":RACE_BEHOBIA,"dist":km(rep_total + (2 if w==19 else 3)),
            "steps":[warm(2 if w==19 else 1.5, Z2, "Calentamiento"), main_reps(reps_taper, rep_dist, RACE_BEHOBIA, "2' trote suave", f"Serie: {reps_taper} × {rep_dist}"), cool(1, Z1, "Enfriamiento")],
            "detail":"Recordar al cuerpo el ritmo objetivo sin generar fatiga. " + total_line(rep_total + (2 if w==19 else 3))})

        days.append(rest_day("JUE", "Movilidad suave, foam roller."))

        days.append({"d":"VIE","title":"Activación piernas","type":"ez","pace":"5:50/km + 3 strides","dist":km(4),
            "steps":[{"label":"Rodaje","detail":"4km a 5:50/km muy relajado"}, main_reps(3, "20\"", "<4:27", "40\" caminar", "Strides finales")],
            "detail":"Activación neuromuscular ligera. " + total_line(4)})

        days.append(rest_day("SÁB", "Nada de carrera. Hidratación y buena cena (carbohidratos)."))

        if data["last"]:
            steps = [warm(2, Z2_LR, "Inicio"), main_continuous(data["lr"]-2-data["last"], Z2_LR, "Cuerpo"),
                     {"label":f"Últimos {data['last']}km a ritmo Behobia","detail":f"{data['last']}km a {RACE_BEHOBIA}/km · solo para recordar la sensación, sin fatiga"}]
            pace_str = f"{Z2_LR} → {data['last']}km a {RACE_BEHOBIA}"
        else:
            steps = [warm(2, Z2_LR, "Inicio"), main_continuous(data["lr"]-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")]
            pace_str = Z2_LR
        days.append({"d":"DOM","title":"Long Run de tapering","type":"long","pace":pace_str,"dist":km(data["lr"]),
            "steps":steps,
            "detail":"Ritmo cómodo, sin buscar sensaciones fuertes. " + total_line(data["lr"])})

    weeks.append({
        "num": w, "block": 1, "phase": 4, "phase_name": "Behobia · Fase 4 — Tapering" if w<21 else "🏁 SEMANA DE CARRERA BEHOBIA",
        "weekly_km": data["vol"], "long_run": data["lr"] if data["lr"] else 20,
        "focus": "Reducir carga progresivamente, mantener frescura, llegar fuerte y descansado al 8N." if w<21 else "Descansar, viajar, y disfrutar de la carrera. El trabajo ya está hecho.",
        "deload": False, "days": days
    })

print(f"Fase 4 añadida, total: {len(weeks)} semanas")


# ================================================================
# BLOQUE 2: TRANSICIÓN + BASE MARATÓN — semanas 22-33 (12 semanas)
# Getafe media maratón (31 ene 2027) = semana 33, usada como long run de control
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
days.append({"d":"SÁB","title":"Z2 suave","type":"ez","pace":Z2,"dist":km(6),
    "steps":[warm(1.5, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), cool(1.5, Z1, "Final")],
    "detail":"Vuelta gradual a la normalidad. FC<145. " + total_line(6)})
days.append({"d":"DOM","title":"Z2 muy suave","type":"long","pace":Z2_LR,"dist":km(10),
    "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(6, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
    "detail":"Recuperación activa. Sin prisa, sin ritmo objetivo — solo sentir las piernas otra vez. " + total_line(10)})

weeks.append({
    "num": w, "block": 2, "phase": 0, "phase_name": "Transición · Recovery post-Behobia",
    "weekly_km": 25, "long_run": 10,
    "focus": "Recuperación activa total tras Behobia. Sin entrenamientos exigentes. El cuerpo necesita asimilar 21 semanas de carga.",
    "deload": True, "days": days, "milestone": "Post-Behobia"
})

# ---- Semanas 23-27: Reconstrucción base (5 semanas) ----
lr_base = [14, 15, 16, 17, 15]  # week 27 = deload
vol_base = [42, 46, 50, 53, 42]

for i in range(5):
    w = i+23
    lr = lr_base[i]
    deload = (i == 4)
    days = []
    days.append(rest_day("LUN"))
    days.append(strength_day("MAR", "A"))
    days.append({"d":"MIÉ","title":"Z2 Rodaje suave","type":"ez","pace":Z2,"dist":km(8 if not deload else 6),
        "steps":[warm(2, Z2, "Primeros 2km"), main_continuous(4 if not deload else 2, Z2, "Resto"), cool(2, Z1, "Últimos 2km")],
        "detail":"FC<145. Reconstruyendo base aeróbica tras el parón. " + total_line(8 if not deload else 6)})

    if w % 2 == 1:
        days.append({"d":"JUE","title":"Cuestas 6×60\"","type":"interval","pace":Z5,"dist":km(7 if not deload else 5),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(6, "60\" cuesta", Z5, "bajada trotando (~90\")", "Serie: 6 × 60\" cuesta"), cool(1.5, Z1, "Enfriamiento")],
            "detail":f"Reintroducción gradual de intensidad. Esfuerzo controlado, sin buscar máximos. {total_line(7 if not deload else 5)}"})
    else:
        days.append({"d":"JUE","title":"6×400m","type":"interval","pace":Z5,"dist":km(7 if not deload else 5),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(6, "400m", Z5, "400m trote suave (~2')", "Serie: 6 × 400m"), cool(1.5, Z1, "Enfriamiento")],
            "detail":f"400m a {Z5}/km. {total_line(7 if not deload else 5)}"})

    days.append(strength_day("VIE", "B"))

    if deload:
        days.append(rest_day("SÁB", "Semana de descarga (coincide con Navidad/fiestas) — aprovecha para descansar bien."))
    else:
        days.append({"d":"SÁB","title":"Z2 muy suave","type":"ez","pace":"5:50-6:20","dist":km(6),
            "steps":[warm(1, Z2, "Inicio"), main_continuous(4, "5:50-6:20", "Cuerpo"), cool(1, Z1, "Final")],
            "detail":"Opcional si llegas fresco. " + total_line(6)})

    days.append({"d":"DOM","title":"Long Run progresivo" if not deload else "Long Run de descarga","type":"long","pace":Z2_LR,"dist":km(lr),
        "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
        "detail":f"Ritmo cómodo, FC<150. {'Semana de fiestas — disfruta, no fuerces.' if deload else 'Reconstruyendo la resistencia de base.'} {total_line(lr)}"})

    notes = ""
    if w == 27:
        notes = " (Semana de Navidad — volumen reducido a propósito)"

    weeks.append({
        "num": w, "block": 2, "phase": 1, "phase_name": f"Transición · Reconstrucción base{notes}",
        "weekly_km": vol_base[i], "long_run": lr,
        "focus": "Reconstruir la base aeróbica tras Behobia, preparando el terreno para el bloque de maratón." + (" Semana de Navidad: prioriza el descanso y disfruta las fiestas." if deload else ""),
        "deload": deload, "days": days
    })

print(f"Bloque 2 (parte 1) añadido, total: {len(weeks)} semanas")


# ---- Semanas 28-32: Construcción específica maratón temprana (5 semanas) ----
# Long run: 17 -> 21, building toward Getafe (week 33) as a controlled long run
lr_build = [17, 18, 19, 21, 16]  # week 32 = mini-taper before Getafe
vol_build = [50, 54, 57, 60, 42]

for i in range(5):
    w = i+28
    lr = lr_build[i]
    is_pretaper = (i == 4)  # week 32

    days = []
    days.append(rest_day("LUN"))
    days.append(strength_day("MAR", "A"))

    days.append({"d":"MIÉ","title":f"Tempo continuo {20 + i*2}'","type":"tempo","pace":Z3,"dist":km(10 if not is_pretaper else 8),
        "steps":[
            warm(2, Z2, "Calentamiento"),
            {"label":"Cuerpo principal","detail":f"{20+i*2}' continuos a {Z3}/km · FC 152-164"},
            cool(2 if not is_pretaper else 1.5, Z1, "Enfriamiento"),
        ],
        "detail":("Última sesión de calidad fuerte antes de Getafe — reduce ligeramente. " if is_pretaper else "") + f"Construyendo el motor aeróbico para el maratón. {total_line(10 if not is_pretaper else 8)}"})

    days.append({"d":"JUE","title":"Fuerza A + Z2 corto","type":"strength","pace":"Sesión A","dist":"35' + 6km Z2",
        "steps":[
            {"label":"1. Fuerza (35')","detail":"Mismas cargas Sesión A — mantenimiento"},
            {"label":"2. Z2 corto (6km)","detail":f"Rodaje muy suave a {Z2}/km, FC<140"},
        ],
        "detail":"Fuerza primero, luego rodaje de mantenimiento."})

    if is_pretaper:
        days.append({"d":"VIE","title":"Z2 suave + strides","type":"ez","pace":Z2,"dist":km(7),
            "steps":[warm(2, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), main_reps(4, "20\"", "<4:27", "40\" trote", "Strides finales")],
            "detail":"Activación ligera, sin fatiga — pre-taper para Getafe. " + total_line(7)})
    else:
        if w % 2 == 0:
            days.append({"d":"VIE","title":"5×1000m a ritmo maratón+","type":"interval","pace":Z4,"dist":km(11),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(5, "1000m", Z4, "90\" trote suave", "Serie: 5 × 1000m"), cool(2, Z1, "Enfriamiento")],
                "detail":f"1000m a {Z4}/km, FC 160-175. {total_line(11)}"})
        else:
            days.append({"d":"VIE","title":"Fartlek 6×(3'/2')","type":"interval","pace":Z4,"dist":km(11),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(6, "3' fuerte", Z4, "2' trote suave", "Fartlek: 6 × (3'/2')"), cool(2, Z1, "Enfriamiento")],
                "detail":f"3' a {Z4}/km seguido de 2' recuperación. {total_line(11)}"})

    days.append({"d":"SÁB","title":"Recovery Z1" if not is_pretaper else "Descanso","type":"ez" if not is_pretaper else "rest",
        "pace":Z1 if not is_pretaper else None,"dist":km(5) if not is_pretaper else None,
        "steps":[{"label":"Recorrido completo","detail":f"5km a {Z1}/km · FC<130"}] if not is_pretaper else [],
        "total":"0 km" if is_pretaper else None,
        "detail":(f"Regeneración activa para el long run. {total_line(5)}") if not is_pretaper else "Descanso completo antes de Getafe — llega fresco."})

    if is_pretaper:
        days.append({"d":"DOM","title":"Long Run suave (pre-Getafe)","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":f"Reducción de volumen — llega a Getafe con piernas frescas. {total_line(lr)}"})
    else:
        last_km = 3 + i  # progresivo: 3, 4, 5km a ritmo maraton-ish (using Z3 since MP not yet calibrated)
        days.append({"d":"DOM","title":"Long Run + ritmo final","type":"long","pace":f"{Z2_LR} → {last_km}km a {Z3}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-last_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {last_km}km a ritmo tempo","detail":f"{last_km}km a {Z3}/km · FC 150-163"},
            ],
            "detail":f"Introduciendo progresivamente trabajo a ritmo más exigente en el long run, preparando el cuerpo para el ritmo de maratón (se calibrará tras Getafe). {total_line(lr)}"})

    # clean up None fields
    for d in days:
        if d.get("pace") is None: d.pop("pace", None)
        if d.get("dist") is None: d.pop("dist", None)
        if d.get("total") is None: d.pop("total", None)

    weeks.append({
        "num": w, "block": 2, "phase": 2, "phase_name": "Transición · Construcción específica" if not is_pretaper else "Transición · Mini-taper pre-Getafe",
        "weekly_km": vol_build[i], "long_run": lr,
        "focus": "Construir resistencia específica para el maratón, usando Getafe como punto de control." if not is_pretaper else "Reducir carga para llegar fresco a la media maratón de Getafe (31 ene).",
        "deload": is_pretaper, "days": days
    })

print(f"Semanas 28-32 añadidas, total: {len(weeks)} semanas")

# ---- Semana 33: GETAFE media maratón (31 ene 2027) ----
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
days.append(rest_day("SÁB", "Descanso total. Hidratación, pasta/arroz en la cena, acostarse pronto. Prepara dorsal y ropa."))
days.append({"d":"DOM","title":"🎯 GETAFE Media Maratón (como Long Run)","type":"long","pace":f"Progresivo: {Z2_LR} → {Z3} → {RACE_BEHOBIA}","dist":"21,1 km",
    "steps":[
        {"label":"Km 0-8","detail":f"A ritmo {Z2_LR}/km — acompañando a tu amigo, conversacional, sin prisa"},
        {"label":"Km 8-16","detail":f"Sube a {Z3}/km si el cuerpo lo pide — sigue siendo controlado"},
        {"label":"Km 16-21","detail":f"Opcional: cierra a ritmo {RACE_BEHOBIA}/km si te sientes bien, o mantén {Z3}/km"},
    ],
    "detail":"⭐ Esta carrera NO es un objetivo de tiempo — es tu long run de 21km con compañía y ambiente de carrera. Aprovecha para practicar nutrición/hidratación de carrera real. Sirve como excelente termómetro de cómo está tu resistencia de cara al maratón."})

weeks.append({
    "num": w, "block": 2, "phase": 3, "phase_name": "🎯 GETAFE · Media Maratón (long run de control)",
    "weekly_km": 47, "long_run": 21.1,
    "focus": "Media maratón de Getafe usada como long run largo con buen ambiente — sin presión de marca, gran oportunidad para practicar el ritmo y la nutrición de cara al maratón de Madrid.",
    "deload": False, "days": days, "milestone": "Getafe Media Maratón (control)"
})

print(f"Semana 33 (Getafe) añadida, total: {len(weeks)} semanas")


# ================================================================
# BLOQUE 3: MARATÓN DE MADRID — semanas 34-45 (12 semanas, 25 abr 2027)
# ================================================================

# ---- Fase A: semanas 34-38, pico de volumen (5 semanas) ----
# Long run: 18 -> 28km. Week 38 = deload
lr_A = [18, 20, 22, 24, 19]
vol_A = [55, 60, 64, 68, 50]

for i in range(5):
    w = i+34
    lr = lr_A[i]
    deload = (i == 4)

    days = []
    days.append(rest_day("LUN", "Recuperación post-Getafe en semana 34. Movilidad + foam roller."))
    days.append(strength_day("MAR", "A"))

    days.append({"d":"MIÉ","title":f"Tempo continuo {25 + i*2 if not deload else 20}'","type":"tempo","pace":Z3,"dist":km(11 if not deload else 8),
        "steps":[
            warm(2.5, Z2, "Calentamiento"),
            {"label":"Cuerpo principal","detail":f"{25+i*2 if not deload else 20}' continuos a {Z3}/km · FC 152-164"},
            cool(2, Z1, "Enfriamiento"),
        ],
        "detail":f"Construyendo el umbral aeróbico para sostener el ritmo de maratón. {total_line(11 if not deload else 8)}"})

    days.append({"d":"JUE","title":"Fuerza A + Z2 corto","type":"strength","pace":"Sesión A","dist":"35' + 7km Z2",
        "steps":[
            {"label":"1. Fuerza (35')","detail":"Mismas cargas Sesión A — mantenimiento"},
            {"label":"2. Z2 corto (7km)","detail":f"Rodaje muy suave a {Z2}/km, FC<140"},
        ],
        "detail":"Fuerza primero, luego rodaje de mantenimiento."})

    if deload:
        days.append({"d":"VIE","title":"Z2 suave + strides","type":"ez","pace":Z2,"dist":km(7),
            "steps":[warm(2, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), main_reps(4, "20\"", "<4:27", "40\" trote", "Strides finales")],
            "detail":"Semana de descarga: reduce volumen e intensidad. " + total_line(7)})
    else:
        if i % 2 == 0:
            days.append({"d":"VIE","title":"6×1000m a ritmo maratón+","type":"interval","pace":Z4,"dist":km(12),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(6, "1000m", Z4, "75\" trote suave", "Serie: 6 × 1000m"), cool(2.5, Z1, "Enfriamiento")],
                "detail":f"1000m a {Z4}/km, FC 160-175. Sesión de calidad clave para el maratón. {total_line(12)}"})
        else:
            days.append({"d":"VIE","title":"Fartlek 8×(3'/2')","type":"interval","pace":Z4,"dist":km(13),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(8, "3' fuerte", Z4, "2' trote suave", "Fartlek: 8 × (3'/2')"), cool(2.5, Z1, "Enfriamiento")],
                "detail":f"3' a {Z4}/km seguido de 2' recuperación, 8 repeticiones. {total_line(13)}"})

    days.append({"d":"SÁB","title":"Recovery Z1","type":"ez","pace":Z1,"dist":km(5 if not deload else 4),
        "steps":[{"label":"Recorrido completo","detail":f"{5 if not deload else 4}km a {Z1}/km · FC<130"}],
        "detail":"Regeneración activa para el long run. " + total_line(5 if not deload else 4)})

    if deload:
        days.append({"d":"DOM","title":"Long Run de descarga","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[warm(2, Z2_LR, "Inicio"), main_continuous(lr-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":f"Semana de descarga: todo suave, sin ritmo. FC<150. {total_line(lr)}"})
    else:
        # Introduce MP (marathon pace) segments progressively
        mp_km = 4 + i*2  # 4, 6, 8, 10
        days.append({"d":"DOM","title":f"Long Run + {mp_km}km a Ritmo Maratón","type":"long","pace":f"{Z2_LR} → {mp_km}km a {MP}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-mp_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {mp_km}km a Ritmo Maratón (MP)","detail":f"{mp_km}km a {MP}/km · FC objetivo según sensaciones, debe sentirse 'sostenible'"},
            ],
            "detail":f"⭐ El ritmo de maratón (MP={MP}/km) es una primera estimación — se recalibrará tras Getafe con tu tiempo real. La sensación debe ser 'podría mantener esto durante horas'. {total_line(lr)}"})

    weeks.append({
        "num": w, "block": 3, "phase": 1, "phase_name": "Maratón Madrid · Fase A — Pico de volumen",
        "weekly_km": vol_A[i], "long_run": lr,
        "focus": "Construir el pico de volumen de la temporada e introducir progresivamente el Ritmo Maratón (MP) en los long runs.",
        "deload": deload, "days": days
    })

print(f"Fase A añadida, total: {len(weeks)} semanas")


# ---- Fase B: semanas 39-42, específico maratón (4 semanas) ----
# Long run: 26 -> 32km. Week 42 = the longest long run (32km), week before begins taper transition
lr_B = [26, 28, 30, 32]
vol_B = [66, 68, 70, 62]
mp_km_B = [12, 14, 16, 18]

for i in range(4):
    w = i+39
    lr = lr_B[i]
    mp_km = mp_km_B[i]
    is_peak = (i == 3)  # week 42 - the big one

    days = []
    days.append(rest_day("LUN", "Movilidad + foam roller. Cuidado extra con la recuperación en este bloque de máxima carga."))
    days.append(strength_day("MAR", "C"))  # switch to eccentric/prevention work given high volume

    days.append({"d":"MIÉ","title":f"Tempo continuo {30 if not is_peak else 25}'","type":"tempo","pace":Z3,"dist":km(12 if not is_peak else 10),
        "steps":[
            warm(2.5, Z2, "Calentamiento"),
            {"label":"Cuerpo principal","detail":f"{30 if not is_peak else 25}' continuos a {Z3}/km · FC 152-164"},
            cool(2, Z1, "Enfriamiento"),
        ],
        "detail":("Semana del long run más largo — reduce ligeramente la intensidad del tempo. " if is_peak else "") + f"{total_line(12 if not is_peak else 10)}"})

    days.append({"d":"JUE","title":"Z2 + MP corto","type":"ez","pace":f"{Z2} + {MP}","dist":km(9),
        "steps":[
            warm(2, Z2, "Calentamiento"),
            main_continuous(4, Z2, "Cuerpo suave"),
            {"label":"Tramo a Ritmo Maratón","detail":f"3km a {MP}/km · práctica de sensación de carrera"},
        ],
        "detail":f"Día de mantenimiento con un toque de ritmo específico. {total_line(9)}"})

    if is_peak:
        days.append({"d":"VIE","title":"Descanso","type":"rest","steps":[],"total":"0 km",
            "detail":"Descanso extra antes del long run de 32km — el más importante del plan. Hidrátate bien hoy."})
    else:
        if i % 2 == 0:
            days.append({"d":"VIE","title":"5×1200m a ritmo maratón+","type":"interval","pace":Z4,"dist":km(12),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(5, "1200m", Z4, "90\" trote suave", "Serie: 5 × 1200m"), cool(2, Z1, "Enfriamiento")],
                "detail":f"1200m a {Z4}/km, FC 160-175. {total_line(12)}"})
        else:
            days.append({"d":"VIE","title":"4×2000m a ritmo umbral","type":"interval","pace":Z3,"dist":km(13),
                "steps":[warm(2.5, Z2, "Calentamiento"), main_reps(4, "2000m", Z3, "2' trote suave", "Serie: 4 × 2000m"), cool(2.5, Z1, "Enfriamiento")],
                "detail":f"2000m a {Z3}/km — desarrollo de umbral para sostener el ritmo de maratón más tiempo. {total_line(13)}"})

    days.append({"d":"SÁB","title":"Recovery Z1" if not is_peak else "Z1 muy corto + nutrición","type":"ez","pace":Z1,"dist":km(5 if not is_peak else 4),
        "steps":[{"label":"Recorrido completo","detail":f"{5 if not is_peak else 4}km a {Z1}/km · FC<130"}],
        "detail":("Carga de carbohidratos esta tarde/noche — practica la estrategia de nutrición pre-carrera para el long run de mañana. " if is_peak else "Regeneración activa para el long run. ") + total_line(5 if not is_peak else 4)})

    if is_peak:
        days.append({"d":"DOM","title":f"🏆 Long Run más largo: {lr}km + {mp_km}km a MP","type":"long","pace":f"{Z2_LR} → {mp_km}km a {MP}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-mp_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {mp_km}km a Ritmo Maratón (MP)","detail":f"{mp_km}km a {MP}/km · simula la segunda mitad del maratón"},
            ],
            "detail":f"⭐⭐ LA SESIÓN CLAVE DE TODO EL PLAN. Practica aquí TODO lo de carrera: ropa, calzado, geles cada 45', hidratación. {total_line(lr)} · Si llega a costar mucho, no pasa nada — es la sesión más exigente y es normal sufrir."})
    else:
        days.append({"d":"DOM","title":f"Long Run + {mp_km}km a Ritmo Maratón","type":"long","pace":f"{Z2_LR} → {mp_km}km a {MP}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-mp_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {mp_km}km a Ritmo Maratón (MP)","detail":f"{mp_km}km a {MP}/km · FC objetivo según sensaciones"},
            ],
            "detail":f"Practica nutrición: gel cada 45'-50' desde el inicio del tramo a MP. {total_line(lr)}"})

    weeks.append({
        "num": w, "block": 3, "phase": 2, "phase_name": "Maratón Madrid · Fase B — Específico maratón" if not is_peak else "Maratón Madrid · Fase B — ⭐ Pico del plan",
        "weekly_km": vol_B[i], "long_run": lr,
        "focus": "Maximizar el tiempo a Ritmo Maratón en el long run. Practicar toda la logística de carrera (nutrición, equipo, calzado)." if not is_peak else "El long run de 32km con 18km a MP es la sesión más importante de toda la temporada — simula la segunda mitad del maratón con fatiga real.",
        "deload": False, "days": days
    })

print(f"Fase B añadida, total: {len(weeks)} semanas")

# ---- Fase C: semanas 43-45, taper + carrera (3 semanas) ----
# Volume reduction: peak was 70 (week 41) -> taper to ~70%, 50%, then race week ~30%
taper3_data = [
    {"vol":48,"lr":18,"mp":6},   # week 43: ~70% of peak
    {"vol":35,"lr":12,"mp":4},   # week 44: ~50%
    {"vol":22,"lr":None,"mp":0}, # week 45: race week
]

for i in range(3):
    w = i+43
    data = taper3_data[i]
    days = []
    days.append(rest_day("LUN", "Movilidad + foam roller."))

    if w == 45:
        # Race week
        days.append({"d":"MAR","title":"Z2 muy suave","type":"ez","pace":Z2,"dist":km(6),
            "steps":[warm(1.5, Z2, "Inicio"), main_continuous(3, Z2, "Cuerpo"), cool(1.5, Z1, "Final")],
            "detail":"FC<145. Mantener soltura. " + total_line(6)})
        days.append({"d":"MIÉ","title":"Activación 3×1km a MP","type":"tempo","pace":MP,"dist":km(7),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(3, "1km", MP, "90\" trote suave", "Serie: 3 × 1km a ritmo maratón"), cool(1, Z1, "Enfriamiento")],
            "detail":"Última activación a ritmo objetivo — recordar la sensación sin generar fatiga. " + total_line(7)})
        days.append(rest_day("JUE", "Descanso total. Empieza a organizar: dorsal, equipo, geles, plan de carrera escrito."))
        days.append({"d":"VIE","title":"3km muy suave + estiramientos","type":"ez","pace":"5:50/km","dist":km(3),
            "steps":[{"label":"Recorrido","detail":"3km a 5:50/km muy relajado"},{"label":"Después","detail":"Estiramientos suaves + foam roller"}],
            "detail":"Activación ligera. " + total_line(3)})
        days.append(rest_day("SÁB", "Descanso total. Carga de carbohidratos, hidratación. Repasa el plan de ritmos y nutrición. Acuéstate pronto — la maratón es domingo por la mañana."))
        days.append({"d":"DOM","title":"🏆 MARATÓN DE MADRID","type":"race","pace":MP,"dist":"42,2 km",
            "steps":[
                {"label":"Km 0-5","detail":f"MUY CONSERVADOR — 10-15\"/km más lento que {MP}. El error más común es salir rápido."},
                {"label":"Km 5-30","detail":f"Asienta {MP}/km. Gel cada 45'. Hidratación en cada avituallamiento (pequeños sorbos)."},
                {"label":"Km 30-38","detail":"La parte dura. Si el ritmo se resiente, prioriza mantener el esfuerzo constante sobre el ritmo exacto. Aquí se decide la carrera."},
                {"label":"Km 38-42","detail":"Si quedan piernas, exprime. Si no, mantén la cadencia y cuenta los metros. Esto es lo que llevas meses entrenando."},
            ],
            "detail":"🎉 21 + 12 + 12 = 45 semanas de trabajo. Disfrútalo — cada km duro de este plan está aquí para este momento."})
    else:
        days.append({"d":"MAR","title":"Z2 suave","type":"ez","pace":Z2,"dist":km(8 if w==43 else 6),
            "steps":[warm(1.5, Z2, "Inicio"), main_continuous((8 if w==43 else 6)-3, Z2, "Cuerpo"), cool(1.5, Z1, "Final")],
            "detail":"FC<145. Reducir volumen, mantener frescura. " + total_line(8 if w==43 else 6)})

        mp_reps = 2
        rep_dist = "2km" if w==43 else "1.5km"
        days.append({"d":"MIÉ","title":f"Activación: {mp_reps}×{rep_dist} a MP","type":"tempo","pace":MP,"dist":km(8 if w==43 else 6),
            "steps":[warm(2, Z2, "Calentamiento"), main_reps(mp_reps, rep_dist, MP, "2' trote suave", f"Serie: {mp_reps} × {rep_dist} a ritmo maratón"), cool(1.5, Z1, "Enfriamiento")],
            "detail":"Mantener la sensación del ritmo objetivo. " + total_line(8 if w==43 else 6)})

        days.append(rest_day("JUE", "Movilidad suave, foam roller."))

        days.append({"d":"VIE","title":"Activación piernas","type":"ez","pace":"5:50/km + 3 strides","dist":km(5 if w==43 else 4),
            "steps":[{"label":"Rodaje","detail":f"{5 if w==43 else 4}km a 5:50/km muy relajado"}, main_reps(3, "20\"", "<4:27", "40\" caminar", "Strides finales")],
            "detail":"Activación neuromuscular ligera. " + total_line(5 if w==43 else 4)})

        days.append(rest_day("SÁB", "Nada de carrera. Hidratación y buena cena (carbohidratos)."))

        days.append({"d":"DOM","title":f"Long Run de tapering + {data['mp']}km a MP","type":"long","pace":f"{Z2_LR} → {data['mp']}km a {MP}","dist":km(data["lr"]),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(data["lr"]-2-data["mp"], Z2_LR, "Cuerpo"),
                {"label":f"Últimos {data['mp']}km a Ritmo Maratón","detail":f"{data['mp']}km a {MP}/km · recordar la sensación, sin fatiga"},
            ],
            "detail":"Ritmo cómodo, reducción de volumen progresiva. " + total_line(data["lr"])})

    weeks.append({
        "num": w, "block": 3, "phase": 3, "phase_name": "Maratón Madrid · Fase C — Tapering" if w<45 else "🏆 SEMANA DE LA MARATÓN",
        "weekly_km": data["vol"], "long_run": data["lr"] if data["lr"] else 30,
        "focus": "Reducir volumen progresivamente mientras se mantiene la sensación del ritmo objetivo. Llegar fresco, descansado y mentalmente preparado." if w<45 else "Descansar, cargar carbohidratos, organizar logística y disfrutar de la culminación de la temporada: la Maratón de Madrid.",
        "deload": False, "days": days, "milestone": "🏆 MARATÓN DE MADRID" if w==45 else None
    })

print(f"Fase C añadida, total: {len(weeks)} semanas")

# Cleanup None milestone fields for non-milestone weeks (keep consistent)
for ww in weeks:
    if "milestone" not in ww:
        ww["milestone"] = None

# Fix week 45 long_run display to represent the marathon distance (42.2km)
for ww in weeks:
    if ww["num"] == 45:
        ww["long_run"] = 42.2


if __name__ == "__main__":
    import json
    print("TOTAL WEEKS:", len(weeks))
    with open("weeks_full.json", "w") as f:
        json.dump(weeks, f, ensure_ascii=False, indent=1)
