# AGENTS.md

Contexto del proyecto **Análisis de SGTI** para futuras operaciones.

## Objetivo
Convertir las exportaciones CSV del SGTI (sistema de gestión de TI del hospital) en
Parquet normalizado y alimentar paneles de reportes de BI (HTML autónomo y Streamlit).

## Alcance
El SGTI es **solo lectura** para reportes de BI. No se proponen features de gestión,
aprobación, edición operativa ni flujos de trabajo; las propuestas deben limitarse a
visualización, análisis, exportación, distribución y calidad de datos.

## Estructura del proyecto
```
Analisis_de_SGTI/
├── Data/
│   ├── hraelocal1-csv-2026-09-07T19-58-04/   # exportación CSV + manifest.json (fuente)
│   ├── hraelocal1-csv-*.zip                  # mismo export comprimido (ignorar en path pickers)
│   └── parquet/                               # 43 archivos .parquet (snappy) — salida
├── scripts/
│   ├── normalize_dates.py      # parsers ISO/UTC: date, datetime, time, string
│   ├── csv_to_parquet.py       # conversión CSV→Parquet, tipado por inferencia de columna
│   ├── validate_parquet.py     # validación filas/columnas/PK/fechas vs CSV+manifest
│   ├── refresh_all.py          # conversión + validación en un solo comando
│   ├── generate_docs.py        # regenera DATA_DICTIONARY.md
│   ├── generate_audit.py       # regenera DATA_AUDIT.md (auditoría de calidad de datos)
│   ├── build_dashboard.py      # datasets normalizados + genera dashboard/index.html (v1)
│   ├── dashboard_template.html # plantilla HTML v1 (Chart.js, pestañas, modo oscuro)
│   ├── build_dashboard_v2.py   # genera dashboard_v2/index.html (lee template v2)
│   ├── dashboard_template_v2.html  # plantilla HTML v2 (+ "Calidad de datos" + "Acumulado")
│   ├── build_dashboard_v3.py   # genera dashboard_v3/index.html (lee template v3)
│   ├── dashboard_template_v3.html  # plantilla HTML v3 (+ export CSV, top-N, heatmap, búsqueda)
│   └── data_quality.py         # métricas de calidad compartidas (HTML v2/v3 + Streamlit v2/v3)
├── streamlit_dashboard.py      # app Streamlit v1 (lee Parquet en vivo)
├── streamlit_dashboard_v2.py   # app Streamlit v2 (+ "Calidad de datos" + "Acumulado")
├── streamlit_dashboard_v3.py   # app Streamlit v3 (+ export CSV, top-N, heatmap, búsqueda)
├── dashboard/                  # HTML v1 (index.html + vendor/chart.umd.min.js)
├── dashboard_v2/               # HTML v2 (index.html + vendor/)
├── dashboard_v3/               # HTML v3 (index.html + vendor/)
├── docs/                       # PLAN_V2.md, FEATURES_V2.md, PLAN_V3.md, FEATURES_V3.md
├── DATA_DICTIONARY.md          # generado; tablas, esquemas y relaciones
├── DATA_AUDIT.md               # generado; auditoría de calidad de datos
├── REFRESH_GUIDE.md            # refresco, gateway, cron, troubleshooting
└── requirements.txt            # pandas, pyarrow, python-dateutil, streamlit (opcional)
```

## Paneles (v1 estable / v2 experimental / v3 experimental)
- v1 = `dashboard/index.html` y `streamlit_dashboard.py` (estables; no tocar).
- v2 = `dashboard_v2/index.html` y `streamlit_dashboard_v2.py` (features nuevas:
  pestaña "Calidad de datos" + toggle "Acumulado (YTD)"). Ver `docs/FEATURES_V2.md`.
- v3 = `dashboard_v3/index.html` y `streamlit_dashboard_v3.py` (features nuevas:
  exportación CSV, ranking top-N, heatmap semanal, búsqueda global). Ver
  `docs/FEATURES_V3.md`.
- Regenerar HTML v2: `.venv/bin/python scripts/build_dashboard_v2.py`.
- Regenerar HTML v3: `.venv/bin/python scripts/build_dashboard_v3.py`.
- Lanzar Streamlit v2: `.venv/bin/streamlit run streamlit_dashboard_v2.py`.
- Lanzar Streamlit v3: `.venv/bin/streamlit run streamlit_dashboard_v3.py`.
- Ambos consumen `scripts/data_quality.compute()` para la pestaña de calidad.

## Entorno / comandos
- Python: 3.14 en un venv `uv` en `.venv/` (sin pip del sistema).
- Dependencias: `uv pip install pandas pyarrow python-dateutil` (ver `requirements.txt`).
- Ejecutar la pipeline: `.venv/bin/python scripts/refresh_all.py`
  → convierte 43/43 y valida (`Validation PASSED`, exit 0).
- Scripts aislados: `csv_to_parquet.py`, `validate_parquet.py` aceptan
  `--csv-dir`, `--out-dir` / `--parquet-dir`. Defaults: `Data/parquet`.
- `.venv/bin/python` (NO `python3`; el sistema no tiene pandas/pip).

## Datos (decisiones de diseño)
- 43 tablas; fecha export `2026-09-07`. Ver `manifest.json` como fuente de verdad de
  tablas/columnas/filas.
- Fechas: ISO-8601 UTC. `T06:00:00.000Z` = medianoche local (UTC-6) → fecha `date32`.
  Timestamps `_at`/`timestamp` → `timestamp[us, tz=UTC]`. Horas `hora_*` → texto `HH:MM:SS`.
- Tipado por inferencia de columna en `csv_to_parquet.infer_type`:
  - `int`: `id`, `*_id`, y `INT_COLUMNS` (cantidad, pdf_tamano, numero_empleado, etc.)
  - `bool`: `BOOL_COLUMNS` (activo, puede_*, entregado, contestado, notificacion…)
  - `float`: solo `monto`.
  - `date`: `fecha*`, `periodo_*`, `fecha`; override a `datetime` para
    `fecha_hora_movimiento`/`fecha_hora_reubicacion`.
  - Todo lo demás es `string` limpio (valores vacíos → null).
- `audit_log`: mantiene JSON (`datos_antes`, `datos_despues`, etc.) como strings;
  `registro_id`, `usuario_id` → int.
- Elementos sensibles (nunca exponer en visuales): `password_hash`,
  `password_asignado_cifrado`.
- Relaciones: dimensiones `coordinaciones`, `personal_hospital`, `personal_ti`,
  `aplicativos_licencia`, `catalogo_suministros`, `puestos_cargo`, pisos, paneles/puertas/
  tarjetas, `monitor_sites`, `usuarios_sistema`, `grupos_permisos`, `perfiles_sistema`.
  Tablas puente N:N: `usuario_grupo`, `usuario_notas_exclusiones`,
  `control_acceso_tarjeta_puertas`, `incidencias_control_acceso_puertas`.

## Trampas conocidas
- `Data/` contiene un `.zip` con el mismo prefijo `hraelocal1-*`; los pickers de
  path SIEMPRE deben elegir el **directorio** (`p.is_dir()`), nunca el `.zip`.
- `source_raw[col].str.strip().ne("")` puede dar NaN/False en columnas con nulls:
  intersectar con `.notna()` en validaciones.