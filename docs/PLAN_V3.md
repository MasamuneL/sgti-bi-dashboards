# PLAN — Iteración v3 del panel (reportes BI)

Fecha: 2026-09-12 · Alcance: **solo lectura / reportes de BI** (sin gestión, aprobación ni flujos).

## Objetivo de esta iteración

Dos frentes, ambos dentro del alcance de reportes:

1. **Exportación**: descargar en CSV los datos ya filtrados de cada pestaña/tabla.
2. **Features BI pendientes** (todas factibles como solo lectura):
   ranking paramétrico top-N, heatmap de actividad semanal y búsqueda global.

Se descartan (fuera de alcance): flujos de aprobación, gestión de stock,
notificaciones, edición de datos.

## Arquitectura de archivos (v1 y v2 intactas / v3 nueva)

```
scripts/
  dashboard_template_v3.html   # NUEVO — copia de v2 + exportación + ranking + heatmap + búsqueda
  build_dashboard_v3.py        # NUEVO — genera dashboard_v3/index.html (lee template v3)
streamlit_dashboard_v3.py      # NUEVO — copia de v2 + las mismas features
dashboard_v3/
  index.html                   # salida (auto-generado)
  vendor/chart.umd.min.js      # copia de dashboard_v2/vendor
docs/
  PLAN_V3.md                   # este archivo
  FEATURES_V3.md               # documentación post-implementación
```

La v1 (`dashboard/`, `streamlit_dashboard.py`, `scripts/build_dashboard.py`,
`scripts/dashboard_template.html`) y la v2 (`dashboard_v2/`,
`streamlit_dashboard_v2.py`, `scripts/build_dashboard_v2.py`,
`scripts/dashboard_template_v2.html`, `scripts/data_quality.py`) **quedan sin cambios**.

## Contrato de features (idéntico en HTML v3 y Streamlit v3)

### F1 — Exportación CSV
- Cada tabla de detalle (drill-down) expone un botón "Descargar CSV".
- Exporta TODAS las filas filtradas (fecha global + filtros de pestaña + búsqueda
  de tabla + búsqueda global), no solo las 200 visibles en pantalla.
- CSV con encabezados = etiquetas de las columnas mostradas, separador coma,
  UTF-8 con BOM (para abrir en Excel sin mojibake).
- HTML: Blob + `URL.createObjectURL` + `<a download>`.
- Streamlit: `st.download_button` con `df.to_csv(index=False).encode("utf-8-sig")`.

### F2 — Ranking paramétrico top-N
- Un control global N (rango 3–20, valor por defecto 10).
- Sustituye todos los "top 10" hardcodeados por top-N (barras horizontales de área,
  módulo, aplicativo, etc.).
- HTML: `input[type=range]` + etiqueta "Top N" en la stickybar.
- Streamlit: `st.slider` en el sidebar.

### F3 — Heatmap de actividad (calendario semanal)
- Una matriz en la pestaña "Resumen": filas = semanas ISO del rango, columnas =
  Lun..Dom, celda = conteo de registros (oficios realizados + recibidos combinados),
  color = intensidad.
- HTML: grid/tabla CSS con 5 tonos del color de acento según intensidad (sin plugin
  de heatmap de Chart.js); `title` attr con "dd/mm · n registros".
- Streamlit: Altair `mark_rect` con escala de color; x = día de la semana ordenado
  Lun..Dom, y = semana ISO descendente.
- Se deriva de `fecha` (string "YYYY-MM-DD") parseando a fecha real.

### F4 — Búsqueda global
- Un campo de texto global ("Buscar…") en stickybar (HTML) / sidebar (Streamlit).
- Filtra los registros del dataset activo por subcadena (case-insensitive) en
  cualquiera de sus campos de texto, antes de graficar y de poblar las tablas.
- HTML: en `filterRows`, si el término no está vacío, conservar solo las filas cuyo
  `Object.values(r).join(" ")` en minúsculas contenga el término.
- Streamlit: función `filtro_global(df)` aplicada junto a `filtro_fecha`.

## Reparto de trabajo (subagentes)

- **Base (yo):** `docs/PLAN_V3.md` (este archivo).
- **Subagente A (HTML v3):** crear `scripts/dashboard_template_v3.html` y
  `scripts/build_dashboard_v3.py`, copiar `dashboard_v2/vendor` → `dashboard_v3/vendor`,
  generar `dashboard_v3/index.html`, verificar en navegador.
- **Subagente B (Streamlit v3):** crear `streamlit_dashboard_v3.py`, verificar con
  `AppTest` y en navegador.
- **Verificación final (yo):** navegador HTML v3 + Streamlit v3.
- **Documentación (yo):** `docs/FEATURES_V3.md` + actualizar AGENTS.md.

## Criterios de verificación

1. v1 y v2 intactas.
2. `build_dashboard_v3.py` genera `dashboard_v3/index.html` sin error.
3. HTML v3: 9 pestañas; botones CSV descargan las filas filtradas (no solo 200);
   slider top-N cambia las barras; heatmap semanal renderiza; búsqueda global filtra;
   modo oscuro sigue operando; sin `NaN`/`undefined` en el DOM.
4. Streamlit v3: `AppTest` sin excepciones; `st.download_button` presente;
   slider top-N; heatmap Altair; búsqueda global; 0 excepciones.
5. `docs/FEATURES_V3.md` documenta uso, archivos y cómo regenerar.
