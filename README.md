# Plan Behobia–San Sebastián 🏁

Plan de entrenamiento de 21 semanas, generado automáticamente, para la carrera Behobia–San Sebastián del 8 de noviembre de 2026.

## 🌐 Ver la web

Una vez configurado GitHub Pages (ver abajo), la web estará disponible en:

```
https://TU-USUARIO.github.io/NOMBRE-REPO/
```

## ⚙️ Configuración inicial (una sola vez)

1. **Crea el repositorio** en GitHub (público, para que GitHub Pages gratuito funcione).
2. **Sube todo el contenido** de esta carpeta al repo (estructura incluida: `.github/`, `scripts/`, `index.html`).
3. Ve a **Settings → Pages**:
   - Source: **GitHub Actions**
4. Ve a **Settings → Actions → General → Workflow permissions**:
   - Selecciona **"Read and write permissions"** (necesario para que el workflow pueda hacer commit del `index.html` actualizado).
5. ¡Listo! El workflow se ejecutará:
   - Automáticamente **cada domingo a las 19:00 UTC**
   - Manualmente desde la pestaña **Actions → Update Training Plan → Run workflow**

## 📁 Estructura

```
.
├── index.html                 # Web generada (no editar a mano, se regenera sola)
├── scripts/
│   ├── build.py               # Orquestador: genera todo el sitio
│   ├── gen_plan_v2.py         # Genera los datos del plan de 21 semanas
│   ├── render_v2.py           # Renderiza las semanas a HTML
│   ├── part1_head.html        # CSS + head del sitio
│   ├── part2_body.html        # Hero, tabs, zonas de ritmo
│   └── part3_strength_script.html  # Tablas de fuerza + JS
└── .github/workflows/update.yml    # Automatización semanal
```

## 🔄 Cómo se actualiza

Cada semana, tras la revisión con Claude de los datos de Strava, los cambios al plan (ajustes de ritmo, volumen, fechas, etc.) se hacen editando `scripts/gen_plan_v2.py`. Al hacer push a `main`, o automáticamente cada domingo, el workflow:

1. Ejecuta `python3 scripts/build.py`
2. Regenera `index.html` con los datos actualizados
3. Hace commit del cambio
4. Publica en GitHub Pages

## 🛠️ Build local

```bash
python3 scripts/build.py
# genera/actualiza index.html en la raíz del repo
```

## 📅 Calendario del plan

- **Inicio:** Lunes 15 de junio de 2026 (Semana 1)
- **Carrera:** Domingo 8 de noviembre de 2026 (Semana 21)
- **Distancia:** 20 km
- **Ritmo objetivo:** 5:05–5:10/km (~1h41'–1h44')
