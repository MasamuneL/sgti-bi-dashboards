# PLAN — Iteración v2 del panel (reportes BI)

Fecha: 2026-09-11 · Alcance: **solo lectura / reportes de BI** (sin gestión, aprobación ni flujos operativos).

## Objetivo de esta iteración

Crear versiones alternativas de los dashboards (`v2`) que **no tocan** las versiones
actuales en producción, e implementar ahí dos features nuevas alineadas con la visión
de reportes:

1. **Pestaña "Calidad de datos"** (reporte meta-BI): expone como tablero vivo los
   problemas de calidad detectados en DATA_AUDIT.md, para que el hospital vea qué tan
   confiable es cada métrica.
2. **Modo "Acumulado (YTD)"**: alternar las series mensuales entre valor por mes y
   acumulado corrido, para lectura de tendencia.

Se descartan deliberadamente (fuera de alcance): semáforos con recordatorios, flujos de
aprobación, gestión de stock, notificaciones, edición de datos.

## Arquitectura de archivos (v1 intacta / v2 nueva)

```
scripts/
  data_quality.py          # NUEVO — métricas de calidad (compartido HTML + Streamlit)
  build_dashboard_v2.py    # NUEVO — genera dashboard_v2/index.html (lee template v2)
  dashboard_template_v2.html  # NUEVO — plantilla HTML con las 2 features
streamlit_dashboard_v2.py  # NUEVO — app Streamlit con las 2 features
dashboard_v2/
  index.html               # salida (auto-generado)
  vendor/chart.umd.min.js  # copia de dashboard/vendor (Chart.js local)
docs/
  PLAN_V2.md               # este archivo
  FEATURES_V2.md           # documentación post-implementación
```

La v1 (`dashboard/index.html`, `streamlit_dashboard.py`, `scripts/build_dashboard.py`,
`scripts/dashboard_template.html`) **queda sin cambios**.

## Contrato de datos compartido

`scripts/data_quality.py` expone `compute() -> dict`:

```json
{
  "fk_coverage":          [ {"tabla","columna","total","mapeadas","pct"}, ... ],
  "fechas_invalidas":     { "total": int, "detalle": [ {"tabla","columna","n","ejemplos"}, ... ] },
  "estatus_sucios":       { "distintos": int, "formulas_excel": int,
                            "valores": [ {"valor","n"}, ... ] },
  "areas_inconsistentes": { "grupos": int, "ejemplos": [ {"normalizado","variantes"}, ... ] },
  "dias_transcurridos":   { "ceros": int, "nulos": int, "total": int },
  "hallazgos":            [ {"severidad":"alta|media|baja","titulo","descripcion"}, ... ]
}
```

Reutiliza los chequeos de `generate_audit.py` (check_fk, check_dates, check_estatus,
check_areas, check_dias). El HTML lo recibe como `DATA.quality` (embebido por
`build_dashboard_v2.py`); Streamlit llama `data_quality.compute()` directamente.

## Feature 1 — Pestaña "Calidad de datos"

Contenido (idéntico en HTML y Streamlit):

- 5 KPIs:
  1. Claves de área < 90 %  → nº de tablas en `fk_coverage` con `pct < 90`.
  2. Fechas inválidas       → `fechas_invalidas.total`.
  3. Estatus sucios         → `estatus_sucios.distintos` (sub: "X fórmulas de Excel").
  4. Áreas duplicadas       → `areas_inconsistentes.grupos`.
  5. Días sin calcular      → `dias_transcurridos.ceros + nulos` (sub: "de 373 oficios").
- Gráfica 1: "Cobertura de clave de área por tabla" (barra horizontal, `pct` por tabla;
  color por severidad: verde ≥90, ámbar 50–89, rojo <50).
- Gráfica 2: "Valores crudos de cuentas_usuario.estatus" (barra horizontal de `valores`, top 8).
- Lista de hallazgos con badge de severidad (alta=rojo, media=ámbar, baja=gris).

## Feature 2 — Modo "Acumulado (YTD)"

- Un control booleano global: HTML = checkbox en la barra fija; Streamlit = checkbox en sidebar.
- Semántica: suma corrida desde el primer mes del rango visible hasta el mes actual.
- Implementación mínima: la función que construye conteos mensuales devuelve la suma
  corrida cuando el flag está activo (así NO hay que tocar cada render).
- Al alternar, se re-renderizan las gráficas (HTML: `refresh()`; Streamlit: `st.rerun()`).

## Reparto de trabajo (subagentes)

- **Base (yo):** `docs/PLAN_V2.md`, `scripts/data_quality.py`, `scripts/build_dashboard_v2.py`,
  copiar `vendor/` a `dashboard_v2/vendor/`.
- **Subagente A (HTML v2):** crear `scripts/dashboard_template_v2.html` copiando la plantilla
  actual y añadiendo las 2 features. Verificar que `build_dashboard_v2.py` genera el HTML.
- **Subagente B (Streamlit v2):** crear `streamlit_dashboard_v2.py` copiando la app actual y
  añadiendo las 2 features. Verificar con `AppTest` (0 excepciones).
- **Verificación final (yo):** HTML en navegador (pestañas, calidad, acumulado, modo oscuro) y
  Streamlit en navegador + AppTest. Corregir si algo falla.
- **Documentación (yo):** `docs/FEATURES_V2.md` + actualizar AGENTS.md.

## Criterios de verificación

1. La v1 sigue intacta y funcionando.
2. `build_dashboard_v2.py` genera `dashboard_v2/index.html` sin error.
3. HTML v2: 9 pestañas (8 + "Calidad de datos"), toggle "Acumulado" cambia las series,
   modo oscuro sigue operando, sin errores JS.
4. Streamlit v2: `AppTest` sin excepciones; pestaña "Calidad de datos" renderiza; toggle
   "Acumulado" funciona; el resto de pestañas sigue igual.
5. `docs/FEATURES_V2.md` documenta uso, archivos y cómo regenerar.
