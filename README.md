# Plan de Temporada: Behobia → Getafe → Maratón de Madrid 🏁🎯🏆

Plan de entrenamiento de **45 semanas**, generado automáticamente, cubriendo toda la temporada 2026-27:

- **🏁 Behobia–San Sebastián (20km)** — 8 nov 2026
- **🎯 Media Maratón de Getafe (21km, como long run de control)** — 31 ene 2027
- **🏆 Maratón de Madrid (42,2km)** — 25 abr 2027

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

## 📅 Estructura de la temporada

| Bloque | Semanas | Fechas | Hito |
|---|---|---|---|
| 1 — Behobia | 1-21 | 15 jun – 8 nov 2026 | 🏁 Behobia-San Sebastián (20km) |
| 2 — Transición + Base Maratón | 22-33 | 9 nov 2026 – 31 ene 2027 | 🎯 Getafe Media Maratón (21km, control) |
| 3 — Maratón Madrid | 34-45 | 1 feb – 25 abr 2027 | 🏆 Maratón de Madrid (42,2km) |

**Notas clave:**
- El long run progresa de forma gradual: 14km (semana 1) → 22km (Behobia) → 21km (Getafe) → 32km (semana 42, sesión clave) → 42,2km (maratón)
- Semana 27 (14-20 dic) es semana de descarga, coincidiendo con Navidad
- El Ritmo de Maratón (MP, actualmente 5:25-5:35/km) es provisional — se recalibrará con datos reales tras Behobia y Getafe
