# PLAN — Iteración v3 del panel (exportación + RLS + features BI)

Fecha: 2026-09-12 · Alcance: **solo lectura / reportes de BI** (sin gestión, aprobación ni flujos).

## Objetivo de esta iteración

Tres frentes, todos dentro del alcance de reportes:

1. **Exportación**: descargar en CSV los datos ya filtrados de cada pestaña/tabla.
2. **RLS corregido**: el `powerbi/SGTI_RLS.md` actual tiene DAX inválido
   (`RELATE()` no es función DAX; compara `coordinaciones.nombre_coordinador` —
   que son **nombres de personas**, no correos — contra `USERPRINCIPALNAME()`).
   Se reescribe contra el esquema real.
3. **Features BI pendientes** (todas factibles como solo lectura):
   ranking paramétrico top-N, heatmap de actividad semanal, búsqueda global y
   medidas derivadas en DAX.

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
powerbi/
  SGTI_RLS.md                  # REESCRITO — DAX válido contra esquema real
  SGTI_Measures_v2.dax         # NUEVO — medidas derivadas (no toca SGTI_Measures.dax)
docs/
  PLAN_V3.md                   # este archivo
  FEATURES_V3.md               # documentación post-implementación
```

La v1 (`dashboard/`, `streamlit_dashboard.py`, `scripts/build_dashboard.py`,
`scripts/dashboard_template.html`) y la v2 (`dashboard_v2/`,
`streamlit_dashboard_v2.py`, `scripts/build_dashboard_v2.py`,
`scripts/dashboard_template_v2.html`, `scripts/data_quality.py`) **quedan sin cambios**.

## Esquema real relevante (fuente de verdad para RLS)

- `personal_ti` (27 filas): `id`, `nombre`, `puesto`, `departamento`, **`correo`**
  (15/27 poblados, institucionales `...@hospital.gob.mx`), `extension`, `activo`.
- `usuarios_sistema` (23): `id`, `personal_ti_id` (→ personal_ti.id), `username`,
  **`rol`** (ADMIN=1, COORDINADOR=3, TECNICO=19), `activo`, `ultimo_acceso`.
- `coordinaciones` (39): `id`, `nombre`, **`nombre_coordinador` = nombres de persona**
  (NO correos), `activo`.
- `personal_hospital` (1663): `id`, `numero_empleado`, `coordinacion_id`,
  `coordinacion_nombre`, `activo`. **Sin correo.**
- `audit_log`: `usuario_id` (→ usuarios_sistema.id), `accion`, `modulo`, `timestamp`.

Conclusión de diseño: la única columna que coincide con `USERPRINCIPALNAME()` es
`personal_ti.correo`. El rol "Coordinador ve su coordinación" no es derivable de
los datos porque `coordinaciones` guarda nombres, no correos → se resuelve con una
tabla de mapeo manual `Seguridad` (correo → coordinacion_id), que es el patrón
estándar de Power BI para RLS.

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
- **Subagente C (RLS + DAX):** reescribir `powerbi/SGTI_RLS.md` con DAX válido y
  crear `powerbi/SGTI_Measures_v2.dax` con medidas derivadas.
- **Verificación final (yo):** navegador HTML v3 + Streamlit v3 + revisión de DAX.
- **Documentación (yo):** `docs/FEATURES_V3.md` + actualizar AGENTS.md.

## Criterios de verificación

1. v1 y v2 intactas.
2. `build_dashboard_v3.py` genera `dashboard_v3/index.html` sin error.
3. HTML v3: 9 pestañas; botones CSV descargan las filas filtradas (no solo 200);
   slider top-N cambia las barras; heatmap semanal renderiza; búsqueda global filtra;
   modo oscuro sigue operando; sin `NaN`/`undefined` en el DOM.
4. Streamlit v3: `AppTest` sin excepciones; `st.download_button` presente;
   slider top-N; heatmap Altair; búsqueda global; 0 excepciones.
5. RLS: DAX sintácticamente válido, solo columnas existentes, con tabla `Seguridad`
   de mapeo documentada. Medidas derivadas compilables en DAX.
6. `docs/FEATURES_V3.md` documenta uso, archivos y cómo regenerar.
