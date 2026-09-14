# Guia de refresco y automatizacion

## 1. Flujo de actualizacion de datos

```
1. Nueva exportacion CSV desde el SGTI (carpeta hraelocal1-*-csv-*)
2. python scripts/refresh_all.py
3. Los .parquet de Data/parquet se regeneran y validan
4. Power BI: refrescar el dataset (Import mode) -> relee los parquet
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

## 3. Refresco de Power BI

### 3.1 Durante el desarrollo (Desktop)
- En `Modelo` (o pestaña de vistas), el boton **Actualizar** (`Ctrl+R`) relee los parquet.

### 3.2 Power BI Service (programado)
El conector de Power BI a archivos Parquet requiere un **gateway** local porque
los archivos viven en la maquina/servidor del hospital:

1. Instalar `On-premises Data Gateway` en la maquina que contenga `Data/parquet`:
   https://powerbi.microsoft.com/en-us/gateway/
2. En **Configurar origen de datos** agregar una entrada del tipo **Folder**
   apuntando a `C:\...\Analisis_de_SGTI\Data\parquet`.
   (O alternar tipo **Parquet** si el conector lo soporta.)
3. En el **dataset** publicado: `Configuraciones > Gateway > Conectar`, elegir el
   gateway + la fuente "Folder".
4. Configurar **Refresh programado** (ej. diario 06:00). El gateway ejecuta primero
   el refresh de datos (solo parquet; no regen el CSV).

> Para regenerar automaticamente los parquet antes del refresh, programe
> `python scripts/refresh_all.py` por separado (Windows Task Scheduler / cron) y
> deje el refresh de Power BI 30-60 min despues.

### 3.3 Modo DirectQuery
- Con Dataset en DirectQuery a la carpeta, cada reporte consulta los parquet en
  tiempo real; no hay "refresh" de datos, solo se publica el esquema.
- El modelo con **RELACIONES compuestas** (pocas dims en Import + hechos DQ) da lo
  mejor de ambos mundos si el rendimiento lo permite.

## 4. Cronograma sugerido

| Origen | Frecuencia | Comando | Notas |
|--------|-----------|---------|-------|
| Export del SGTI | Semanal (dom 05:00) | `scripts/refresh_all.py` | Back-up de CSV previo |
| Refresh Power BI | Diario 06:30 | Config del dataset | Rele todo el dashboard |

## 5. Solucion de problemas

| Sintoma | Causa probable | Solucion |
|---------|---------------|----------|
| `Converted 42/43 ... FAIL` | CSV con formato inesperado | Revisar el mensaje y ajustar `normalize_dates.csv` / `csv_to_parquet.py` |
| `Validation FAILED` | Fecha no vacia sin parsear | Buscar el valor en el CSV y normalizarlo manualmente |
| Parquet no se ve en Power Query | Ruta con backslashes o accesos | Usar `\\` o barra `/`, y verificar permisos del gateway |
| Refresh falla en el servicio | Gateway sin conexion/fuente | Revisar la pestaña `Configuraciones > Gateway` del dataset |
| Tiempos `hora_*` como texto | Diseno del Parquet | Filtrar con `TIMEVALUE()` agrega coste; considerar columna calculada |

## 6. Pruebas de regresion

```bash
source .venv/bin/activate
python scripts/validate_parquet.py
```
Debe imprimir `Validation PASSED` y salir con codigo 0.