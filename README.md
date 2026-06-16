# Plan de Temporada: Behobia → Getafe → Maratón de Madrid 🏁🎯🏆

Plan de entrenamiento de **45 semanas**, generado automáticamente, cubriendo toda la temporada 2026-27:

- **🏁 Behobia–San Sebastián (20km)** — 8 nov 2026
- **🎯 Media Maratón de Getafe (21km, como long run de control)** — 31 ene 2027
- **🏆 Maratón de Madrid (42,2km)** — 25 abr 2027 · Objetivo: **sub-4h** (ambicioso: ~3h45)

## 🌐 Ver la web

```
https://TU-USUARIO.github.io/NOMBRE-REPO/
```

## ⚙️ Configuración inicial (una sola vez)

1. **Crea el repositorio** en GitHub (público).
2. **Sube todo el contenido** de esta carpeta (estructura incluida: `.github/`, `scripts/`, `index.html`).
3. **Settings → Pages** → Source: **GitHub Actions**
4. **Settings → Actions → General → Workflow permissions** → **"Read and write permissions"**
5. Lánzalo manualmente: **Actions → Update Training Plan → Run workflow**

A partir de ahí: se ejecuta automáticamente **cada domingo a las 19:00 UTC**, o manualmente cuando quieras.

## 📁 Estructura

```
.
├── index.html                          # Web generada (no editar a mano)
├── scripts/
│   ├── build.py                        # Orquestador: genera todo el sitio
│   ├── gen_plan.py                     # Genera los datos del plan de 45 semanas
│   ├── render.py                       # Renderiza las semanas a HTML
│   ├── part1_head.html                 # CSS + head del sitio
│   ├── part2_body.html                 # Hero, tabs, zonas de ritmo
│   └── part3_strength_script.html      # Tablas de fuerza + JS
└── .github/workflows/update.yml        # Automatización semanal
```

## 🔄 Cómo se actualiza

Cada semana, tras la revisión con Claude de los datos de Strava, los ajustes al plan (ritmos, volumen, fechas, recalibración del ritmo de maratón tras Behobia/Getafe, etc.) se hacen editando `scripts/gen_plan.py`. Al hacer push a `main`, o automáticamente cada domingo, el workflow:

1. Ejecuta `python3 scripts/build.py`
2. Regenera `index.html`
3. Hace commit del cambio
4. Publica en GitHub Pages

## 🛠️ Build local

```bash
python3 scripts/build.py
```

## 📅 Estructura semanal estándar

| Día | Contenido |
|---|---|
| Lunes | Descanso total |
| Martes | Trote activación (3-4km) + Fuerza A/B/C |
| Miércoles | Intervalos / Cuestas |
| Jueves | Trote activación (3-4km) + Fuerza A/B/C (otra sesión) |
| Viernes | Recovery / Z2 suave |
| **Sábado** | **Long Run** (con tramos a ritmo cuando toca) |
| Domingo | Z2 opcional o descanso |

En semanas con carrera (Behobia, Getafe, Maratón) la carrera ocupa el domingo y el resto de la semana se adapta (taper).

**Nota sobre activación pre-fuerza:** siguiendo recomendaciones de entrenadores especializados (Luis del Águila), el trote corto va ANTES de la fuerza (activación, sin fatiga) en vez de después (que acumula fatiga residual con poco beneficio aeróbico).

## 📊 Estructura de la temporada

| Bloque | Semanas | Fechas | Hito | Pico volumen | Long run máx |
|---|---|---|---|---|---|
| 1 — Behobia | 1-21 | 15 jun – 8 nov 2026 | 🏁 Behobia (20km) | 55 km | 21 km |
| 2 — Transición + Base Maratón | 22-33 | 9 nov 2026 – 31 ene 2027 | 🎯 Getafe (21km, control) | 47 km | 21,1 km (Getafe) |
| 3 — Maratón Madrid | 34-45 | 1 feb – 25 abr 2027 | 🏆 Maratón (42,2km) | 56 km | 27 km (sem. 42, sesión clave) + 24km (sem. 37, gran sesión previa) |

## 🎯 Sobre el Ritmo de Maratón (MP) y objetivos

- **MP actual: 5:40-5:50/km** → objetivo sub-4h (~3h58-4h05), prioridad principal
- **Predicción desde 5K (23:58)**: ~3h45-3h50 si la resistencia de fondo responde bien
- **Recalibración**: tras Behobia (8 nov) y especialmente Getafe (31 ene), se ajustará el MP con datos reales. Si Getafe sale por debajo de ~1h50, valorar apuntar a 3h45 con MP≈5:20/km
- El bloque 3 incluye **dos long runs grandes**: semana 37 (24km, primera "gran sesión") y semana 42 (27km + 13km a MP, la sesión clave de toda la temporada)

**Notas clave:**
- Todas las progresiones de volumen y long run siguen incrementos de ~5-10% por semana (regla del 10%), con descargas moderadas
- Semana 27 (14-20 dic) es semana de descarga, coincidiendo con Navidad
