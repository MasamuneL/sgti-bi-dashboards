# Auditoría de datos — SGTI

> Generado: 2026-09-11 · Fuente: `Data/parquet` (43 tablas) · Corte de exportación: `2026-09-07`

Este documento registra, con ejemplos y conteos reales, los errores y anomalías de calidad de datos encontrados al analizar la exportación CSV del SGTI. Es reproducible: `.venv/bin/python scripts/generate_audit.py`.

## Resumen ejecutivo

| Severidad | Hallazgo | Tablas / columnas afectadas |
|-----------|----------|------------------------------|
| 🔴 Alta | 67 % de oficios recibidos sin contestar | `oficios_recibidos.contestado` |
| 🔴 Alta | Errores de año en fechas (19xx/20xx) | `vacaciones_incidencias`, `oficios_realizados.fecha_fin`, `bitacora_equipo_portatil` |
| 🟠 Media | Cobertura parcial de claves de área | `cuentas_usuario.coordinacion_id` (47 %), `entregas_suministro.coordinacion_id` (27 %) |
| 🟠 Media | Estatus sucios + objeto Excel en `estatus` | `cuentas_usuario.estatus` |
| 🟠 Media | Nombres de área inconsistentes (acentos/mayúsculas) | `notas_informativas.departamento`, `entregas_suministro.coordinacion_nombre` |
| 🟡 Baja | `dias_transcurridos` sin calcular | `oficios_recibidos.dias_transcurridos` |
| 🟡 Baja | Meses con mayúsculas inconsistentes | `oficios_realizados.mes` |
| 🟡 Baja | Fechas posteriores al corte de exportación | `oficios_recibidos`, `vacaciones_incidencias` |

## 1. Errores de año en fechas

Fechas cuyo año es claramente erróneo (fuera de 2000–2027), típicamente por teclear `1926` en vez de `2026` o `2032` en vez de `2026`.

| Tabla | Columna | Registros | Ejemplos |
|-------|---------|----------:|----------|
| `oficios_realizados` | `fecha_fin` | 1 | `1926-06-02` |
| `vacaciones_incidencias` | `fecha_inicio` | 1 | `2032-08-21` |
| `vacaciones_incidencias` | `fecha_fin` | 1 | `2032-08-23` |
| `bitacora_equipo_portatil` | `fecha_asignacion` | 1 | `1926-02-16` |

**Impacto:** estas filas quedan fuera de cualquier eje temporal. En el panel se excluyen.

## 2. Cobertura de claves foráneas de área

Porcentaje de filas cuya clave de área (`departamento_id` / `coordinacion_id`) mapea a una coordinación del catálogo (`coordinaciones`, 39 registros).

| Tabla | Columna | Filas | Mapeadas | Cobertura |
|-------|---------|------:|---------:|----------:|
| `oficios_realizados` | `departamento_id` | 245 | 238 | 97 % |
| `oficios_recibidos` | `departamento_id` | 373 | 356 | 95 % |
| `notas_informativas` | `departamento_id` | 529 | 47 | 9 % ⚠️ |
| `minutas_circulares` | `departamento_id` | 12 | 0 | 0 % ⚠️ |
| `cuentas_usuario` | `coordinacion_id` | 646 | 301 | 47 % ⚠️ |
| `entregas_suministro` | `coordinacion_id` | 161 | 44 | 27 % ⚠️ |
| `asignaciones_licenciamiento` | `coordinacion_id` | 149 | 103 | 69 % ⚠️ |
| `historico_reubicaciones_equipos` | `coordinacion_origen_id` | 84 | 84 | 100 % |
| `control_acceso_tarjetas` | `coordinacion_id` | 5 | 5 | 100 % |

**Nota:** `entregas_suministro` y `cuentas_usuario` son las más afectadas; el resto de sus registros cae en “Sin dato” en los filtros por área. `notas_informativas` usa texto libre de área interna de TI (no es coordinación hospitalaria).

## 3. Valores sucios en `cuentas_usuario.estatus`

La columna `estatus` mezcla etiquetas controladas con frases libres y hasta un objeto de fórmula de Excel sin evaluar.

| Valor en `estatus` | Registros | Observación |
|--------------------|----------:|-------------|
| `Entregado` | 486 | — |
| `Pendiente` | 112 | — |
| `Se realizó entrega de la solicitud` | 42 | redacción libre (equivale a “Entregado”) |
| `Se generó negativa a solicitud` | 5 | — |
| `<openpyxl.worksheet.formula.ArrayFormula object at 0x7ecd79ef8740>` | 1 | — |

Además `se_da_negativa` es `True` en **8** filas (negativas de solicitud). Recomendación: usar un catálogo cerrado (`Entregado`, `Pendiente`, `Negativa`).

## 4. Nombres de área inconsistentes (acentos / mayúsculas)

Columnas de texto libre con la misma área escrita de varias formas. Al normalizar (sin acentos, minúsculas) se detectaron estos grupos con más de una variante:

| Área normalizada | Variantes encontradas |
|------------------|-----------------------|
| soporte tecnico | `Soporte Tecnico` · `Soporte Técnico` · `Soporte técnico` |
| coordinador de informatica | `Coordinador de Informatica` · `Coordinador de Informática` |
| coordinacion de informatica | `COORDINACION DE INFORMATICA` · `Coordinación de Informática` |
| informatica | `Informatica` · `Informática` |
| coordinacion de mantenimiento | `COORDINACION DE MANTENIMIENTO` · `Coordinación de Mantenimiento` |

**Impacto:** sin normalizar, una misma área se contaría varias veces en gráficas y filtros. El panel aplica normalización (acentos y mayúsculas) para consolidarlas.

## 5. Campo calculado sin llenar: `oficios_recibidos.dias_transcurridos`

De **373** oficios recibidos: **186** valen `0` y **187** están vacíos. Es decir, la antigüedad en días no se está calculando de forma confiable (solo una fracción mínima tiene un valor real).

## 6. Meses con mayúsculas inconsistentes: `oficios_realizados.mes`

El campo `mes` mezcla minúsculas, mayúsculas y duplicados por capitalización:

```text
'marzo': 41
'abril': 40
'enero': 33
'febrero': 30
'Junio': 30
'Julio': 30
'Mayo': 21
'agosto': 16
'mayo': 2
'JULIO': 2
```
El panel deriva el mes de `fecha_inicio` (fuente confiable) e ignora este campo.

## 7. Fechas posteriores al corte de exportación

Registros con fecha posterior al `2026-09-07` (corte de exportación):

| Tabla | Columna | Registros | Fecha máxima |
|-------|---------|----------:|--------------|
| `oficios_recibidos` | `fecha_recepcion` | 1 | 2026-10-19 |
| `oficios_recibidos` | `fecha_inicial` | 1 | 2026-10-19 |
| `oficios_recibidos` | `fecha_fin` | 3 | 2026-12-31 |
| `historico_reubicaciones_equipos` | `fecha_hora_reubicacion` | 2 | 2026-10-27 |
| `vacaciones_incidencias` | `fecha_inicio` | 15 | 2026-11-28 |
| `vacaciones_incidencias` | `fecha_fin` | 15 | 2026-11-28 |
| `audit_log` | `timestamp` | 2 | 2026-09-08 |

En su mayoría son **legítimos**: vacaciones planeadas a futuro (hasta 2026-11-28) y plazos de oficios a fin de año. El `audit_log` muestra 1 día de desfase por zona horaria (UTC).

## 8. Recomendaciones

1. **Validar fechas al capturar** (rango de año razonable) para evitar `1926`/`2032`.
2. **Cerrar el catálogo de estatus** de cuentas de usuario y eliminar fórmulas de Excel en la exportación.
3. **Completar las claves foráneas de área** en `cuentas_usuario` y `entregas_suministro` (usar el catálogo `coordinaciones`).
4. **Calcular `dias_transcurridos`** al guardar el oficio recibido (o derivarlo de `fecha_recepcion` vs hoy).
5. **Unificar nombres de área** en los formularios (dropdowns ligados a `coordinaciones`, no texto libre).
6. **Priorizar la contestación de oficios recibidos** (67 % pendientes): es el riesgo operativo más visible.
