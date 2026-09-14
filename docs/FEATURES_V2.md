# FEATURES_V2 — Documentación de la iteración v2 de los paneles

Fecha: 2026-09-11 · Alcance: **solo lectura / reportes de BI** (sin gestión, aprobación ni flujos).

## Qué es esto

Versión alternativa (`v2`) de los dos paneles, que **no toca** la versión estable (`v1`)
y añade dos features de reporte:

1. **Pestaña "Calidad de datos"** (reporte meta-BI): expone en un tablero vivo los
   problemas de calidad detectados en `DATA_AUDIT.md`.
2. **Toggle "Acumulado (YTD)"**: alterna las series mensuales entre valor por mes y
   suma corrida, para leer tendencias.

## Archivos (v1 intacta / v2 nueva)

| Versión | HTML | Streamlit |
|---------|------|-----------|
| v1 (estable) | `dashboard/index.html` · plantilla `scripts/dashboard_template.html` · generador `scripts/build_dashboard.py` | `streamlit_dashboard.py` |
| v2 (nueva) | `dashboard_v2/index.html` · plantilla `scripts/dashboard_template_v2.html` · generador `scripts/build_dashboard_v2.py` | `streamlit_dashboard_v2.py` |

Compartido (v2): `scripts/data_quality.py` — métricas de calidad (`compute() -> dict`),
reutiliza los chequeos de `scripts/generate_audit.py`.

Documentación: `docs/PLAN_V2.md` (plan), este archivo (`docs/FEATURES_V2.md`).

## Cómo ejecutar / regenerar

```
# HTML v2 (regenera dashboard_v2/index.html)
.venv/bin/python scripts/build_dashboard_v2.py

# Streamlit v2 (lee Data/parquet en vivo)
.venv/bin/streamlit run streamlit_dashboard_v2.py
```

El HTML v2 se abre con doble clic (Chart.js va vendored en `dashboard_v2/vendor/`).
Requiere el payload `quality` que inyecta `build_dashboard_v2.py` vía `DATA.quality`.

## Contrato de `data_quality.compute()`

```json
{
  "fk_coverage":          [ {"tabla","columna","total","mapeadas","pct"}, ...9 ],
  "fechas_invalidas":     { "total": 4, "detalle": [ {"tabla","columna","n","ejemplos"} ] },
  "estatus_sucios":       { "distintos": 5, "formulas_excel": 1, "valores": [ {"valor","n"} ] },
  "areas_inconsistentes": { "grupos": 5, "ejemplos": [ {"normalizado","variantes"} ] },
  "dias_transcurridos":   { "ceros": 186, "nulos": 187, "total": 373 },
  "hallazgos":            [ {"severidad":"alta|media|baja","titulo","descripcion"}, ...7 ]
}
```

## Detalle de implementación (por si se retoma)

### HTML v2 (`dashboard_template_v2.html`)
- Nueva pestaña en `TABS`: `{id:"calidad", label:"Calidad de datos", ds:[], filters:[]}`,
  con `RENDERERS.calidad = renderCalidad`.
- `renderCalidad()`: 5 KPIs (`.kpi`) + barra horizontal de cobertura FK con array de
  colores por barra (verde ≥90, ámbar 50–89, rojo <50) + barra de estatus sucios + lista
  de hallazgos (`.finding` con `--red/--amber/--gray` por severidad; añadida `.finding.low`).
- Acumulado: `let ACUM = false;` y `monthCounts()` devuelve suma corrida cuando `ACUM`;
  checkbox `#acumChk` en `.stickybar > .controls` hace `refresh()` al cambiar.
- Todo el CSS nuevo usa variables de tema (`--card`, `--line`, `--red`, etc.), así que el
  modo oscuro sigue funcionando.

### Streamlit v2 (`streamlit_dashboard_v2.py`)
- `import data_quality as dq`; pestaña `tabs[8]` con `q = dq.compute()`.
- 5 `st.metric` + 2 gráficas Altair (cobertura FK con columna `color` derivada por severidad
  y `alt.Color(...).scale(None)`; estatus con `hbar_top`/`shorten`) + hallazgos con `st.markdown`.
- Acumulado: `ACUM = st.sidebar.checkbox("Ver acumulado (YTD)", value=False)` como variable
  de módulo; `monthly()` y `monthly_grouped()` aplican `cumsum` (por categoría en el segundo)
  cuando `ACUM` es True. Las claves `mes` son `YYYY-MM`, orden lexicográfico = cronológico.

## Verificación realizada (esta iteración)

- HTML v2 en navegador: 9 pestañas; "Calidad de datos" renderiza 5 KPIs + 2 gráficas + 7
  hallazgos; toggle "Acumulado" convierte la serie mensual `[33,30,41,...]` en corrida
  no-decreciente que termina en 245 (el total); modo oscuro opera; sin errores JS.
- Streamlit v2: `AppTest` → `EXCEPTIONS: []`, `TABS: 9`, 11 métricas, 1 checkbox; en navegador
  9 pestañas, etiqueta "Ver acumulado (YTD)" en sidebar, hallazgos presentes, sin `NaN/undefined`.

## Notas para futuras sesiones

- No modificar `v1` (`dashboard/index.html`, `streamlit_dashboard.py`, `build_dashboard.py`,
  `dashboard_template.html`); toda iteración nueva va en `v2` o `v3`.
- La pestaña "Calidad de datos" es *meta-BI*: mide la confiabilidad del propio dato. Si los
  números cambian tras un refresco, se actualizan solos (lee Parquet en vivo / payload).
- El bug de `build_dashboard_v2.py` (genexpr con `d` en vez de `r.get("fecha")`) ya está
  corregido; no reintroducir al editar.
- Servidores: `streamlit_dashboard.py` corre en :8501 y `streamlit_dashboard_v2.py` en :8502
  (lanzados con `--server.headless true`); el tema de marca vive en `.streamlit/config.toml`.

## Modo oscuro en Streamlit (cómo se implementó)

Streamlit **no permite cambiar el tema por API en runtime** (`st.set_option` solo acepta
opciones `client.*`), y el truco de escribir `localStorage["stActiveTheme-*"]` + recarga **no
se aplica** en esta versión (revertió a "System"). Por eso el modo oscuro se implementó con:

1. `DARK = st.sidebar.toggle("Modo oscuro", value=False)` (visible en el sidebar, v1 y v2).
2. `DARK_CSS`: override por CSS (`html/body/.stApp`, sidebar, métricas, dataframe, tabs,
   widgets) inyectado solo cuando `DARK` es True.
3. Colores explícitos en Altair: `_theme(chart)` aplica `configure_axis/legend/title` con
   `_TXT`/`_GRID` según `DARK`, para que las gráficas también se re-tematicen (el texto de
   ejes no sigue el tema de Streamlit automáticamente).

Límite conocido: los *popups* de los widgets (lista desplegable del multiselect, calendario
del date_input) se renderizan en un portal y pueden verse claros; los widgets cerrados y el
resto del panel sí quedan oscuros. Si Streamlit expone un API de tema en runtime, sustituir
este enfoque por ese.
