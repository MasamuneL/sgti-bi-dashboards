# Guia de refresco y automatizacion

## 1. Flujo de actualizacion de datos

```
1. Nueva exportacion CSV desde el SGTI (carpeta hraelocal1-*-csv-*)
2. python scripts/refresh_all.py
3. Los .parquet de Data/parquet se regeneran y validan
4. Los paneles (HTML/Streamlit) releen los parquet
```

`refresh_all.py` ejecuta en orden:
1. `csv_to_parquet.py` — convierte todos los CSV a Parquet (snappy).
2. `validate_parquet.py` — verifica conteos de filas, columnas, PKs sin nulos y
   que todas las fechas no vacias se hayan normalizado.

> Nota: porque hay varios exportes (`hraelocal1-csv-*`), los scripts eligen
> **el directorio mas reciente que contenga `manifest.json`**; tambien puede
> indicarse explicitamente con `--csv-dir`.

## 2. Ejecucion manual (con el entorno virtual)

```bash
source .venv/bin/activate        # o: .venv\Scripts\activate en Windows
python scripts/refresh_all.py
```

Resultado esperado:
```
Converted 43/43 tables to .../Data/parquet
Validation PASSED
```

## 3. Regenerar los paneles

### 3.1 HTML
- `scripts/build_dashboard_v3.py` regenera `dashboard_v3/index.html` (la version mas
  reciente). Para v1/v2 usar `build_dashboard.py` / `build_dashboard_v2.py`.

### 3.2 Streamlit
- `streamlit_dashboard_v3.py` lee los Parquet en vivo; no requiere regeneracion,
  solo reiniciar la app si cambio el esquema.

## 4. Cronograma sugerido

| Origen | Frecuencia | Comando | Notas |
|--------|-----------|---------|-------|
| Export del SGTI | Semanal (dom 05:00) | `scripts/refresh_all.py` | Back-up de CSV previo |

## 5. Solucion de problemas

| Sintoma | Causa probable | Solucion |
|---------|---------------|----------|
| `Converted 42/43 ... FAIL` | CSV con formato inesperado | Revisar el mensaje y ajustar `normalize_dates.csv` / `csv_to_parquet.py` |
| `Validation FAILED` | Fecha no vacia sin parsear | Buscar el valor en el CSV y normalizarlo manualmente |
| Tiempos `hora_*` como texto | Diseno del Parquet | Filtrar con `TIMEVALUE()` agrega coste; considerar columna calculada |

## 6. Pruebas de regresion

```bash
source .venv/bin/activate
python scripts/validate_parquet.py
```
Debe imprimir `Validation PASSED` y salir con codigo 0.