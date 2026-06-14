import datetime, json

START = datetime.date(2026, 6, 15)

Z1 = "6:10-6:50"
Z2 = "5:40-6:15"
Z2_LR = "5:45-6:20"
Z3 = "5:04-5:30"
Z4 = "4:44-5:03"
Z5 = "4:27-4:43"
RACE = "5:05-5:10"

def km(v):
    return f"{v} km"

# ---- Helper builders for "steps" lists ----
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

weeks = []

# ================= FASE 1: weeks 1-6 =================
lr_phase1 = [16, 16, 17, 18, 17, 18]
vol_phase1 = [42, 44, 46, 48, 44, 50]

for i in range(6):
    w = i+1
    lr = lr_phase1[i]
    deload = (i == 4)
    days = []

    days.append({"d":"LUN","title":"Descanso total","type":"rest","steps":[],"total":"0 km","detail":"Estiramientos suaves opcionales 10 min. Foam roller si tienes."})

    days.append({"d":"MAR","title":"Fuerza A · Piernas + Core","type":"strength","pace":"Sesión A","dist":"35-40 min",
        "steps":[
            {"label":"1. Goblet Squat","detail":"3×15 · 10kg · descanso 60\""},
            {"label":"2. Staggered RDL","detail":"3×12 c/lado · 17.5kg · descanso 75\""},
            {"label":"3. Búlgara","detail":"3×10 c/lado · peso corporal · descanso 90\""},
            {"label":"4. Puente glúteo c/pausa","detail":"3×12 · +10kg · descanso 60\""},
            {"label":"5. Gemelo excéntrico","detail":"3×15 · bilateral · descanso 60\""},
            {"label":"6. Plancha + Pallof","detail":"3×40\" plancha + 3×10 Pallof c/lado"},
        ],
        "detail":"Ver tabla completa de 'Sesión A' en la pestaña Fuerza."})

    days.append({"d":"MIÉ","title":"Z2 Rodaje suave","type":"ez","pace":Z2,"dist":km(8 if not deload else 6),
        "steps":[
            warm(2, Z2, "Primeros 2km"),
            main_continuous(4 if not deload else 2, Z2, "Resto del rodaje"),
            cool(2, Z1, "Últimos 2km"),
        ],
        "detail":"FC <145 bpm todo el rodaje. Conversacional, sin esfuerzo. " + total_line(8 if not deload else 6)})

    # Thursday: alternating cuestas / 400m
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

    days.append({"d":"VIE","title":"Fuerza B · Cuerpo Completo","type":"strength","pace":"Sesión B","dist":"35-40 min",
        "steps":[
            {"label":"1. Press banca/flexiones","detail":"3×12 · 50% RM · descanso 75\""},
            {"label":"2. Remo mancuerna","detail":"3×12 c/lado · 20-22kg · descanso 60\""},
            {"label":"3. Hurdle hops","detail":"4×8 · peso corporal · descanso 90\""},
            {"label":"4. Hip thrust","detail":"4×10 · 30-40kg · descanso 75\""},
            {"label":"5. Elevación piernas rectas","detail":"3×12 · peso corporal"},
            {"label":"6. Zancada caminada","detail":"3×10 c/lado · 10kg/mano"},
        ],
        "detail":"Ver tabla completa de 'Sesión B' en la pestaña Fuerza."})

    if deload:
        days.append({"d":"SÁB","title":"Descanso","type":"rest","steps":[],"total":"0 km","detail":"Semana de descarga: recupera bien antes del bloque final de Fase 1."})
    else:
        days.append({"d":"SÁB","title":"Z2 muy suave (opcional)","type":"ez","pace":"5:50-6:20","dist":km(6),
            "steps":[
                warm(1, Z2, "Inicio"),
                main_continuous(4, "5:50-6:20", "Cuerpo del rodaje"),
                cool(1, Z1, "Final"),
            ],
            "detail":"Solo si llegas fresco. Si hay fatiga, descansa. " + total_line(6)})

    # Long run
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
        "num": w, "phase": 1, "phase_name": "Construcción de base aeróbica",
        "weekly_km": vol_phase1[i], "long_run": lr,
        "focus": "Adaptación de tendones y articulaciones al volumen. Construir hábito de fuerza 2x/semana.",
        "deload": deload, "days": days
    })

# ================= FASE 2: weeks 7-14 =================
lr_phase2 = [18, 19, 20, 18, 19, 20, 20, 17]
vol_phase2 = [52, 54, 56, 50, 58, 60, 62, 48]
deload_p2 = [3, 7]

for i in range(8):
    w = i+7
    lr = lr_phase2[i]
    deload = i in deload_p2

    days = []
    days.append({"d":"LUN","title":"Descanso total","type":"rest","steps":[],"total":"0 km","detail":"O paseo/walk muy suave 20-30 min. Movilidad de cadera y tobillo."})

    days.append({"d":"MAR","title":"Z2 + Strides","type":"ez","pace":Z2,"dist":km(9 if not deload else 7),
        "steps":[
            warm(2, Z2, "Calentamiento"),
            main_continuous((9 if not deload else 7)-3, Z2, "Cuerpo del rodaje"),
            main_reps(4, "20\"", "<4:27", "40\" trote suave", "Strides finales"),
            {"label":"Enfriamiento","detail":"1 km muy suave + caminar"},
        ],
        "detail":f"Los strides son progresiones controladas, no sprints máximos. Activación neuromuscular sin generar fatiga. {total_line(9 if not deload else 7)}"})

    tempo_min = 20 + min(10, (w-7)*2)
    tempo_km = round(tempo_min / 5.2, 1)  # approx km at ~5:12/km pace
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
            "steps":[
                warm(1.5, Z2, "Inicio"),
                main_continuous(3, Z2, "Cuerpo"),
                cool(1.5, Z1, "Final"),
            ],
            "detail":"Semana de descarga: sin series esta semana. " + total_line(6)})
    else:
        if w % 2 == 1:
            days.append({"d":"VIE","title":"5×1000m","type":"interval","pace":Z4,"dist":km(11),
                "steps":[
                    warm(2.5, Z2, "Calentamiento"),
                    main_reps(5, "1000m", Z4, "90\" trote suave", "Serie: 5 × 1000m"),
                    cool(2, Z1, "Enfriamiento"),
                ],
                "detail":f"1000m a {Z4}/km (~4:44-5:03 cada km), FC 160-175. Recuperación trotando, no parado. {total_line(11)}"})
        else:
            days.append({"d":"VIE","title":"Fartlek 6×(3'/2')","type":"interval","pace":Z4,"dist":km(11),
                "steps":[
                    warm(2.5, Z2, "Calentamiento"),
                    main_reps(6, "3' fuerte", Z4, "2' trote suave (Z1-Z2)", "Fartlek: 6 × (3' fuerte / 2' suave)"),
                    cool(2, Z1, "Enfriamiento"),
                ],
                "detail":f"3' a {Z4}/km, FC 160-175, seguido de 2' de trote de recuperación. {total_line(11)}"})

    days.append({"d":"SÁB","title":"Recovery Z1","type":"ez","pace":Z1,"dist":km(5),
        "steps":[
            {"label":"Recorrido completo","detail":f"5km continuos a {Z1}/km · FC <130"},
        ],
        "detail":"Solo regeneración activa, deja las piernas listas para el long run del domingo. " + total_line(5)})

    last_km = min(5, 3 + (w-7)//2)
    if deload:
        days.append({"d":"DOM","title":"Long Run de descarga","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-4, Z2_LR, "Cuerpo"),
                cool(2, Z1, "Final"),
            ],
            "detail":f"Semana de descarga: todo suave, sin ritmo final. FC<150. {total_line(lr)}"})
    else:
        days.append({"d":"DOM","title":"Long Run + ritmo final","type":"long","pace":f"{Z2_LR} → {last_km}km a {RACE}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-last_km, Z2_LR, "Cuerpo suave"),
                {"label":f"Últimos {last_km}km a ritmo Behobia","detail":f"{last_km} km a {RACE}/km · FC 150-163 · simula final de carrera"},
            ],
            "detail":f"Primeros {lr-last_km}km a FC<150. Los últimos {last_km}km suben a ritmo objetivo — sin recuperación entre tramos. {total_line(lr)}"})

    weeks.append({
        "num": w, "phase": 2, "phase_name": "Desarrollo de ritmo y volumen",
        "weekly_km": vol_phase2[i], "long_run": lr,
        "focus": "Subir volumen progresivamente + introducir ritmo específico en el long run.",
        "deload": deload, "days": days
    })

# ================= FASE 3: weeks 15-18 =================
lr_phase3 = [20, 21, 22, 18]
vol_phase3 = [58, 62, 64, 45]

for i in range(4):
    w = i+15
    lr = lr_phase3[i]
    deload = i == 3

    days = []
    days.append({"d":"LUN","title":"Descanso total","type":"rest","steps":[],"total":"0 km","detail":"Movilidad + foam roller. Empieza a pensar en logística de carrera si estamos cerca del taper."})

    days.append({"d":"MAR","title":"Z2 con desnivel","type":"ez","pace":Z2,"dist":km(10 if not deload else 7),
        "steps":[
            warm(2, Z2, "Llano inicial"),
            main_continuous((10 if not deload else 7)-4, Z2, "Tramo con cuestas"),
            cool(2, Z1, "Llano final"),
        ],
        "detail":f"Busca rutas con desnivel acumulado (Casa de Campo / Monte de El Pardo). FC más alta en subidas — normal, no fuerces el ritmo, deja que suba la FC. {total_line(10 if not deload else 7)}"})

    reps = 3 if not deload else 2
    main_total = reps*3
    days.append({"d":"MIÉ","title":f"{reps}×3km a ritmo Behobia","type":"tempo","pace":RACE,"dist":km(main_total+3),
        "steps":[
            warm(2, Z2, "Calentamiento"),
            main_reps(reps, "3km", RACE, "3' caminando + trote suave", f"Serie: {reps} × 3km a ritmo Behobia"),
            cool(1, Z1, "Enfriamiento"),
        ],
        "detail":f"FC 150-163 durante las series. Esto ES tu ritmo de carrera — memorízalo. {total_line(main_total+3)}"})

    days.append({"d":"JUE","title":"Fuerza C · Excéntrica","type":"strength","pace":"Sesión C","dist":"25-30 min",
        "steps":[
            {"label":"1. Nórdico isquio","detail":"3×5-8 · bajada 4-5\" · descanso 120\""},
            {"label":"2. Excéntrico gemelo","detail":"3×12 c/lado · bajada 3\" · descanso 60\""},
            {"label":"3. Búlgara excéntrica","detail":"3×8 c/lado · bajada 4\" · descanso 90\""},
            {"label":"4. Step-down excéntrico","detail":"3×10 c/lado · bajada 3\" · descanso 60\""},
            {"label":"5. Plancha lateral dinámica","detail":"3×12 c/lado · descanso 45\""},
        ],
        "detail":"Ver tabla completa de 'Sesión C' en la pestaña Fuerza. Foco en control, no en velocidad."})

    if deload:
        days.append({"d":"VIE","title":"Z2 suave","type":"ez","pace":Z2,"dist":km(6),
            "steps":[
                warm(1.5, Z2, "Inicio"),
                main_continuous(3, Z2, "Cuerpo"),
                cool(1.5, Z1, "Final"),
            ],
            "detail":"Última semana antes del taper: reduce intensidad. " + total_line(6)})
    else:
        days.append({"d":"VIE","title":"6×800m race pace+","type":"interval","pace":"4:44-4:58","dist":km(11),
            "steps":[
                warm(2.5, Z2, "Calentamiento"),
                main_reps(6, "800m", "4:44-4:58", "2' trote suave", "Serie: 6 × 800m"),
                cool(2, Z1, "Enfriamiento"),
            ],
            "detail":f"Ligeramente más rápido que ritmo carrera, FC 165-175. {total_line(11)}"})

    days.append({"d":"SÁB","title":"Z1 muy suave","type":"ez","pace":Z1,"dist":km(5),
        "steps":[{"label":"Recorrido completo","detail":f"5km a {Z1}/km · FC <125"}],
        "detail":"Solo mover las piernas, piensa en el domingo. " + total_line(5)})

    if deload:
        days.append({"d":"DOM","title":"Long Run suave (descarga)","type":"long","pace":Z2_LR,"dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-4, Z2_LR, "Cuerpo"),
                cool(2, Z1, "Final"),
            ],
            "detail":f"Todo suave, sin ritmo. Última semana de carga alta — recupera antes del taper. {total_line(lr)}"})
    else:
        days.append({"d":"DOM","title":"Long Run mixto (clave)","type":"long","pace":f"{Z2_LR} → 8km a {RACE}","dist":km(lr),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(lr-2-8, Z2_LR, "Cuerpo suave"),
                {"label":"Últimos 8km a ritmo Behobia","detail":f"8 km a {RACE}/km · FC 150-163 · sin pausa entre tramos"},
            ],
            "detail":f"⭐ Esta es tu sesión más dura del plan — simula la carrera real con fatiga acumulada. {total_line(lr)}"})

    weeks.append({
        "num": w, "phase": 3, "phase_name": "Específico Behobia (carrera + desnivel)",
        "weekly_km": vol_phase3[i], "long_run": lr,
        "focus": "Trabajo directo a ritmo de carrera, desnivel y prevención con fuerza excéntrica.",
        "deload": deload, "days": days
    })

# ================= FASE 4: weeks 19-21 =================
taper_data = [
    {"vol":40,"lr":14,"last":3},
    {"vol":25,"lr":10,"last":2},
    {"vol":15,"lr":None,"last":0},
]

for i in range(3):
    w = i+19
    data = taper_data[i]
    days = []
    days.append({"d":"LUN","title":"Descanso total","type":"rest","steps":[],"total":"0 km","detail":"Movilidad suave."})

    if w == 21:
        days.append({"d":"MAR","title":"Z2 muy suave","type":"ez","pace":Z2,"dist":km(5),
            "steps":[
                warm(1, Z2, "Inicio"),
                main_continuous(3, Z2, "Cuerpo"),
                cool(1, Z1, "Final"),
            ],
            "detail":"Activación ligera. FC<145. " + total_line(5)})
        days.append({"d":"MIÉ","title":"Activación 1km a ritmo carrera","type":"tempo","pace":RACE,"dist":km(4),
            "steps":[
                warm(1.5, Z2, "Calentamiento"),
                {"label":"Serie","detail":f"1km a {RACE}/km · solo recordar la sensación"},
                cool(1.5, Z1, "Enfriamiento"),
            ],
            "detail":"Nada de fatiga, esto es solo activación neuromuscular. " + total_line(4)})
        days.append({"d":"JUE","title":"Descanso total","type":"rest","steps":[],"total":"0 km","detail":"Empieza a pensar en la logística: bolsa, dorsal, transporte a Donosti."})
        days.append({"d":"VIE","title":"3km muy suave + estiramientos","type":"ez","pace":"5:50/km","dist":km(3),
            "steps":[{"label":"Recorrido","detail":"3km a 5:50/km muy relajado"},{"label":"Después","detail":"Estiramientos suaves 10' + foam roller"}],
            "detail":"Solo piernas activas. " + total_line(3)})
        days.append({"d":"SÁB","title":"Descanso · Viaje a Donosti","type":"rest","steps":[],"total":"0 km",
            "detail":"Hidratación, pasta/arroz en la cena, acostarse pronto. Prepara ropa, dorsal, geles, alfileres, vaselina."})
        days.append({"d":"DOM","title":"🏁 BEHOBIA-SAN SEBASTIÁN","type":"race","pace":RACE,"dist":"20 km · Meta 1h41-1h44",
            "steps":[
                {"label":"Km 0-5","detail":f"Sal CONSERVADOR — incluso 5-10\"/km más lento que {RACE}. No te dejes llevar por la multitud."},
                {"label":"Km 5-15","detail":f"Asienta el ritmo objetivo {RACE}/km. Tramo Behobia→Rentería es el más exigente — controla esfuerzo, no ritmo."},
                {"label":"Km 15-20","detail":"Si llegas bien, exprime lo que tengas. Si no, mantén ritmo y no pares — el aliento de meta en San Sebastián merece la pena."},
                {"label":"Nutrición","detail":"Gel o dátiles en km 8-10 y km 14-15 (lo que hayas probado en los long runs)."},
            ],
            "detail":"¡A disfrutarlo, te lo has ganado! 21 semanas de trabajo te respaldan."})
    else:
        days.append({"d":"MAR","title":"Z2 suave","type":"ez","pace":Z2,"dist":km(8 if w==19 else 6),
            "steps":[
                warm(1.5, Z2, "Inicio"),
                main_continuous((8 if w==19 else 6)-3, Z2, "Cuerpo"),
                cool(1.5, Z1, "Final"),
            ],
            "detail":"FC<145. Reducir volumen, mantener frescura de piernas. " + total_line(8 if w==19 else 6)})

        reps_taper = 2
        rep_dist = "2km" if w==19 else "1km"
        rep_total = 4 if w==19 else 2
        days.append({"d":"MIÉ","title":f"Activación: {reps_taper}×{rep_dist} a ritmo carrera","type":"tempo","pace":RACE,"dist":km(rep_total + (2 if w==19 else 3)),
            "steps":[
                warm(2 if w==19 else 1.5, Z2, "Calentamiento"),
                main_reps(reps_taper, rep_dist, RACE, "2' trote suave", f"Serie: {reps_taper} × {rep_dist}"),
                cool(1, Z1, "Enfriamiento"),
            ],
            "detail":"Recordar al cuerpo el ritmo objetivo sin generar fatiga. " + total_line(rep_total + (2 if w==19 else 3))})

        days.append({"d":"JUE","title":"Descanso / walk","type":"rest","steps":[],"total":"0 km","detail":"Movilidad suave, foam roller."})

        days.append({"d":"VIE","title":"Activación piernas","type":"ez","pace":"5:50/km + 3 strides","dist":km(4),
            "steps":[
                {"label":"Rodaje","detail":"4km a 5:50/km muy relajado"},
                main_reps(3, "20\"", "<4:27", "40\" caminar", "Strides finales"),
            ],
            "detail":"Activación neuromuscular ligera. " + total_line(4)})

        days.append({"d":"SÁB","title":"Descanso total","type":"rest","steps":[],"total":"0 km","detail":"Nada de carrera. Hidratación y buena cena (carbohidratos)."})

        days.append({"d":"DOM","title":"Long Run de tapering","type":"long","pace":f"{Z2_LR}" + (f" → {data['last']}km a {RACE}" if data['last'] else ""),"dist":km(data["lr"]),
            "steps":[
                warm(2, Z2_LR, "Inicio"),
                main_continuous(data["lr"]-2-data["last"], Z2_LR, "Cuerpo"),
                {"label":f"Últimos {data['last']}km a ritmo Behobia","detail":f"{data['last']}km a {RACE}/km · solo para recordar la sensación, sin fatiga"} if data["last"] else cool(0,Z1,""),
            ] if data["last"] else [warm(2, Z2_LR, "Inicio"), main_continuous(data["lr"]-4, Z2_LR, "Cuerpo"), cool(2, Z1, "Final")],
            "detail":"Ritmo cómodo, sin buscar sensaciones fuertes. " + total_line(data["lr"])})

    weeks.append({
        "num": w, "phase": 4, "phase_name": "Tapering" if w<21 else "🏁 SEMANA DE CARRERA",
        "weekly_km": data["vol"], "long_run": data["lr"] if data["lr"] else 20,
        "focus": "Reducir carga progresivamente, mantener frescura, llegar fuerte y descansado al 8N." if w<21 else "Descansar, viajar, y disfrutar de la carrera. El trabajo ya está hecho.",
        "deload": False, "days": days
    })

print(len(weeks), "weeks generated")
with open("weeks_v2.json","w") as f:
    json.dump(weeks, f, ensure_ascii=False, indent=1)
