# Análisis de SGTI — Paneles de reportes BI

Pipeline que convierte las exportaciones CSV del **SGTI** (sistema de gestión de TI de
un hospital) en Parquet normalizado y alimenta paneles de reportes de **solo lectura**
(HTML autónomo y Streamlit).

> Este repositorio **no contiene datos reales**. Incluye datos **sintéticos** de ejemplo
> (`sample_data/`) con el mismo esquema (43 tablas) para que puedas ver los paneles
> funcionando y sustituirlos después por tu propia exportación CSV.

## Estructura

```
Analisis_de_SGTI/
├── dashboard/                  # HTML v1 (histórica)
├── dashboard_v2/               # HTML v2 (histórica)
├── dashboard_v3/               # HTML v3 (VIGENTE) — export CSV, top-N, heatmap, búsqueda
├── demo/                       # paneles generados con datos sintéticos (ver demo/v3)
├── streamlit_dashboard*.py     # apps Streamlit v1/v2/v3 (v3 vigente)
├── scripts/                    # pipeline CSV→Parquet, validación, auditoría, generadores
├── sample_data/                # 43 CSVs sintéticos + manifest.json (plantillas sustituibles)
├── Data/                       # tus datos reales (NO versionados; ver .gitignore)
├── docs/                       # PLAN/FEATURES de cada iteración
├── Makefile                    # atajos: make refresh / dashboard / demo / streamlit
├── DATA_DICTIONARY.md          # tablas, esquemas y relaciones
├── DATA_AUDIT.md               # auditoría de calidad de datos
└── README.md
```

**Versión vigente: v3** (HTML en `dashboard_v3/`, Streamlit en `streamlit_dashboard_v3.py`).
v1 y v2 se conservan por compatibilidad/historial, pero ya no se actualizan.

## Atajos con make

```bash
make refresh    # CSV → Parquet + validación (datos reales en Data/)
make dashboard  # genera dashboard_v3/index.html (HTML vigente)
make demo       # regenera demo/v1..v3 con datos sintéticos
make streamlit  # lanza Streamlit v3
make help       # lista todos los targets
```

Estos atajos usan el venv del proyecto (`.venv/`); si no existe, créalo primero:

```bash
uv venv .venv && uv pip install -r requirements.txt
```

## Qué hay aquí

- `dashboard/`, `dashboard_v2/`, `dashboard_v3/` — paneles HTML (Chart.js vendored,
  se abren con doble clic, sin internet).
  - v1: pestañas por módulo + filtros + drill-down + modo oscuro.
  - v2: añade pestaña "Calidad de datos" y toggle "Acumulado (YTD)".
  - v3: añade exportación CSV, ranking top-N, heatmap semanal y búsqueda global.
- `demo/` — los mismos paneles **generados con datos sintéticos** (ábrelos ya:
  `demo/v3/index.html`).
- `streamlit_dashboard.py`, `_v2.py`, `_v3.py` — apps Streamlit que leen Parquet en vivo.
- `scripts/` — pipeline CSV→Parquet, validación, auditoría y generadores de paneles.
- `docs/` — planes y documentación de cada iteración (v1/v2/v3).
- `DATA_DICTIONARY.md` — tablas, esquemas y relaciones.
- `DATA_AUDIT.md` — auditoría de calidad de datos.

## Requisitos

- Python 3.14 en un venv `uv` (ver `requirements.txt`).
- Dependencias: `uv pip install pandas pyarrow python-dateutil` (streamlit es opcional).

## Ver los paneles demo (datos sintéticos, ya listos)

Abre `demo/v3/index.html` con doble clic. Es la versión más reciente con datos de
ejemplo (nombres ficticios, correos `@ejemplo.gob.mx`).

Para regenerar la demo desde las plantillas:

```bash
.venv/bin/python scripts/build_sample_data.py   # (re)genera sample_data/
.venv/bin/python scripts/build_demo.py          # genera demo/v1..v3
```

## Usar tus datos reales

Los paneles leen de `Data/parquet`. El flujo completo:

```bash
# 1. Copia la exportación CSV del SGTI (carpeta hraelocal1-*-csv-* con manifest.json)
#    a Data/ (no la subas al repo: está en .gitignore).

# 2. Convierte CSV → Parquet y valida:
.venv/bin/python scripts/refresh_all.py

# 3. Genera el panel HTML (v3 es la más reciente):
.venv/bin/python scripts/build_dashboard_v3.py

# 4. O lanza Streamlit (lee los Parquet en vivo):
.venv/bin/streamlit run streamlit_dashboard_v3.py
```

## Pipeline

```
CSV del SGTI ──▶ scripts/csv_to_parquet.py ──▶ Data/parquet (43 .parquet)
                        │                          │
                        └─ manifest.json           ├─▶ scripts/build_dashboard*.py ──▶ dashboard*/index.html
                                                   ├─▶ streamlit_dashboard*.py
                                                   └─▶ scripts/generate_audit.py ──▶ DATA_AUDIT.md
```

`refresh_all.py` = `csv_to_parquet.py` + `validate_parquet.py` en un solo comando
(espera "Converted 43/43" y "Validation PASSED").

## Alcance

Los datos son **solo lectura** para reportes de BI: visualización, análisis,
exportación, distribución y calidad de datos. No hay gestión, aprobación ni flujos
operativos. Elementos sensibles (`password_hash`, `password_asignado_cifrado`) nunca se
exponen en visuales.
