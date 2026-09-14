# FEATURES_V3 — Documentación de la iteración v3 de los paneles

Fecha: 2026-09-12 · Alcance: **solo lectura / reportes de BI** (sin gestión, aprobación ni flujos).

## Qué es esto

Tercera versión (`v3`) de los dos paneles, que **no toca** v1 ni v2, y añade cuatro
features de reporte más la corrección del RLS de Power BI:

1. **Exportación CSV**: descargar en CSV los datos ya filtrados de cada tabla de detalle.
2. **Ranking paramétrico top-N**: un slider global (3–20, default 10) que controla el
   número de categorías en todas las barras horizontales (área, módulo, aplicativo…).
3. **Heatmap de actividad semanal**: matriz semanas-ISO × días (Lun–Dom) con la densidad
   de oficios emitidos + recibidos por día, en la pestaña Resumen.
4. **Búsqueda global**: campo de texto que filtra por subcadena en cualquier campo de
   texto del dataset activo, antes de graficar y de poblar las tablas.

Además, se **reescribió** el RLS (`powerbi/SGTI_RLS.md`), que tenía DAX inválido, y se
añadieron **medidas derivadas** en un archivo nuevo (`powerbi/SGTI_Measures_v2.dax`).

## Archivos (v1 y v2 intactas / v3 nueva)

| Versión | HTML | Streamlit |
|---------|------|-----------|
| v1 (estable) | `dashboard/` · `scripts/build_dashboard.py` · `scripts/dashboard_template.html` | `streamlit_dashboard.py` |
| v2 | `dashboard_v2/` · `scripts/build_dashboard_v2.py` · `scripts/dashboard_template_v2.html` | `streamlit_dashboard_v2.py` |
| **v3 (nueva)** | `dashboard_v3/` · `scripts/build_dashboard_v3.py` · `scripts/dashboard_template_v3.html` | `streamlit_dashboard_v3.py` |

Compartido (v3): `scripts/data_quality.py` (pestaña de calidad, sin cambios) y
`scripts/build_dashboard.py` (datasets normalizados, sin cambios).

Power BI: `powerbi/SGTI_RLS.md` (reescrito), `powerbi/SGTI_Measures_v2.dax` (nuevo).
`SGTI_Measures.dax` queda intacto.

Documentación: `docs/PLAN_V3.md` (plan), este archivo (`docs/FEATURES_V3.md`).

## Cómo ejecutar / regenerar

```
# HTML v3 (regenera dashboard_v3/index.html)
.venv/bin/python scripts/build_dashboard_v3.py

# Streamlit v3 (lee Data/parquet en vivo)
.venv/bin/streamlit run streamlit_dashboard_v3.py
```

El HTML v3 se abre con doble clic (Chart.js vendored en `dashboard_v3/vendor/`).

## Detalle de implementación (por si se retoma)

### HTML v3 (`scripts/dashboard_template_v3.html`)
- **F1 CSV**: funciones `csvCell(v)` (escapa comas/comillas/CRLF) y
  `downloadCSV(rows, cols, filename)`. Genera `Blob(["\ufeff" + lineas], {type:"text/csv"})`
  (BOM UTF-8 para que Excel abra los acentos bien) y descarga vía `<a download>`.
  Cada tabla de detalle añade un botón "Descargar CSV" que exporta **las filas
  filtradas completas** (usa `filterRows`, no el `slice(0,200)` que solo pinta la vista).
- **F2 top-N**: variable global `TOP_N` (default 10) + `input[type=range]` `#topNSlider`
  (3–20) en la stickybar. Las llamadas `topN(countBy(...), TOP_N)` leen el valor global;
  el cambio hace `refresh()`.
- **F3 heatmap**: `parseDateStr(s)` usa `new Date(s+"T00:00:00")` (evita desfase de
  zona horaria de parsear `YYYY-MM-DD` como UTC) y `isoWeekInfo(d)` calcula la semana ISO
  (jueves de la semana). Renderiza una tabla CSS (`grid` Lun–Dom) con 5 tonos del acento
  según densidad. Se muestra en Resumen combinando `oficiosRealizados` + `oficiosRecibidos`.
- **F4 búsqueda global**: input `#globalSearch` en la stickybar; `filterRows` conserva
  solo filas cuyo `Object.values(r).join(" ").toLowerCase()` incluye el término.

### Streamlit v3 (`streamlit_dashboard_v3.py`)
- **F1 CSV**: `st.download_button` por pestaña con detalle (8 botones: or, rr, nt, cu,
  entregas, ingresos, reubicaciones, licencias), cada uno con `df.to_csv(index=False)
  .encode("utf-8-sig")` y `key` única (`dl_or`, `dl_rr`, …).
- **F2 top-N**: `st.slider("Top N", 3, 20, 10)` en el sidebar; `hbar_top` recibe `n` y
  todas las llamadas (incluidas las que usaban `n=6`/`n=8`) usan el valor del slider.
- **F3 heatmap**: Altair `mark_rect` en Resumen; deriva día de semana
  (`dt.dayofweek`, Lun=0) y semana ISO (`dt.isocalendar().week`) con pandas, concatena
  OR+RR, y pasa por `_theme()` para respetar el modo oscuro.
- **F4 búsqueda global**: `st.text_input("Buscar…")` en el sidebar; `filtro_global(df)`
  conserva filas cuya concatenación de celdas (str, minúsculas) contiene el término; se
  aplica junto a `filtro_fecha` en cada pestaña.

### RLS (`powerbi/SGTI_RLS.md`) — corrección
Errores del RLS anterior, corregidos:
- Usaba `RELATE()` que **no existe** en RLS (solo `RELATED`, en columnas calculadas).
- Comparaba `coordinaciones.nombre_coordinador` — que son **nombres de persona**, no
  correos — contra `USERPRINCIPALNAME()`.
- Usaba `LOOKUPVALUE` mal formado.

Corrección (esquema real verificado de los Parquet): la única columna con correo es
`personal_ti.correo`. Roles:
- `Admin_TI`: sin restricción (`TRUE()`).
- `Coordinador`: tabla manual `Seguridad[correo, coordinacion_id]` (Power Query `Enter
  Data`); Opción A = regla sobre `Seguridad` con relación "Ambas"; Opción B (recomendada)
  = `coordinaciones[id] = LOOKUPVALUE(Seguridad[coordinacion_id], Seguridad[correo],
  USERPRINCIPALNAME())` con dirección única.
- `Tecnico`: `personal_ti[correo] = USERPRINCIPALNAME()` (propaga vía las relaciones
  `personal_ti.id → <fact>.<fk>`).
- `Auditor`: `TRUE()` + desmarcar las facts sensibles (`cuentas_usuario`,
  `asignaciones_licenciamiento`, `entregas_suministro`, `ingresos_suministro`).

### Medidas derivadas (`powerbi/SGTI_Measures_v2.dax`)
13 medidas nuevas (no duplican `SGTI_Measures.dax`): per-cápita (Oficios/Empleado TI,
Entregas per cápita, Reubicaciones/Técnico, Licencias/Empleado TI, Promedio unidades por
entrega, Promedio contador impresoras), ratios (Ratio contestación, % entregados,
% cancelados, Cuentas entregadas, % cuentas con negativa) y variación MoM (oficios
recibidos, ingresos).

**Hallazgo de calidad documentado en el DAX**: `cuentas_usuario.estatus` está sucio
("Entregado" 486, "Pendiente" 112, "Se realizo entrega de la solicitud" 42, "Se genero
negativa a solicitud" 5, objeto Excel 1). El valor literal `"Entregada"` **no existe**;
por eso `Cuentas Entregadas Ratio` usa `SEARCH("ENTREG", UPPER(...))` en vez de igualdad.

## Verificación realizada (esta iteración, por el padre — no auto-reporte)

- `build_dashboard_v3.py` genera `dashboard_v3/index.html` (605 KB) sin error; vendor
  Chart.js copiado (205 KB).
- HTML v3 en navegador: 9 pestañas; botón "Descargar CSV" presente y exporta **245 filas**
  de oficiosRealizados (no las 200 visibles), encabezados = etiquetas, acentos correctos;
  heatmap 254 celdas; búsqueda global filtra ("Informática" reduce 245→5); slider top-N
  (3–20, default 10); modo oscuro cambia fondo y las gráficas siguen renderizando; sin
  `NaN`/`undefined` en el DOM.
- Streamlit v3: `AppTest` → `EXCEPTIONS: []`, `TABS: 9`, `SLIDER: 1`, `TEXT_INPUT: 1`,
  `DOWNLOAD_BTN: 8`.
- RLS y medidas: columnas referenciadas verificadas contra los esquemas reales de
  `Data/parquet` (todas existen); DAX sintácticamente válido.

## Notas para futuras sesiones

- No modificar v1 ni v2; toda iteración nueva va en v3/v4.
- Los números de los CSV dependen del payload embebido: si cambian los Parquet, hay que
  regenerar el HTML (`build_dashboard_v3.py`); Streamlit los lee en vivo.
- El RLS no se puede probar sin Power BI Desktop; los artefactos son definiciones para
  pegar. Probar con `Modelo > Ver como roles` usando un UPN real (ej.
  `usuario.ejemplo@hospital.gob.mx` para Técnico).
- `st.download_button` de Streamlit descarga por cada pestaña; las claves deben seguir
  siendo únicas si se añaden más botones (`dl_*`).
