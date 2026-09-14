# Guia de configuracion del modelo de Power BI (SGTI)

Este proyecto genera un lago de datos ligero de Parquet a partir de las exportaciones
CSV del SGTI. Esta guia describe como construir el modelo en Power BI Desktop.

## 1. Requisitos

- **Power BI Desktop** (version >= Dec 2022 para el conector Parquet integrado).
- Los archivos Parquet en `Data/parquet/` (generados por `csv_to_parquet.py`).
- (Opcional) Power BI Service + On-premises Gateway para refresco programado.

## 2. Crear la consulta de funcion `fnLoadParquet`

1. En Power Query (Power BI Desktop), `Obtener datos > Consulta en blanco`.
2. `Edicion avanzada` y pegar el bloque "Consulta de funcion" de `powerbi/SGTI_Load_Data.pq`.
3. Nombrar la consulta `fnLoadParquet`.

## 3. Crear una consulta por tabla

1. Para cada bloque `// --- <tabla> ---` en `SGTI_Load_Data.pq`:
   - `Obtener datos > Consulta en blanco` > `Edicion avanzada`.
   - Pegar el bloque y reemplazar `PARQUET_FOLDER_ABSOLUTE` por la ruta absoluta a
     `Data/parquet` (ej. `C:\Servicio_Social\Analisis_de_SGTI\Data\parquet`).
   - Nombrar la consulta igual que la tabla (sin `.parquet`).
2. Deshabilitar el tipo de carga para tablas que solo se usen como dimensiones:
   `Propiedades de la consulta > Habilitar carga > "Incluir en el modelo"`.
3. Oprimir `Cerrar y aplicar`.

Sugerencia: un primer modelo util es:
- **Dimensiones**: coordinaciones, personal_hospital, personal_ti, aplicativos_licencia,
  catalogo_suministros, puestos_cargo, pisos_reubicacion, control_acceso_paneles,
  control_acceso_puertas, monitor_sites, usuarios_sistema.
- **Hechos**: asignaciones_licenciamiento, entregas_suministro, ingresos_suministro,
  historico_reubicaciones_equipos, oficios_recibidos, oficios_realizados,
  notas_informativas, vacaciones_incidencias, cuentas_usuario, audit_log.

## 4. Relaciones

Usar `powerbi/SGTI_Relationships.csv` como lista maestra (53 relaciones many-to-one,
direccion de filtro unica). En `Modelo > Administrar relaciones`:

- (1) `coordinaciones[id]`  -> (muchos) tablas con `coordinacion_id`.
- (1) `personal_hospital[id]` -> `control_acceso_tarjetas[personal_hospital_id]`.
- (1) `personal_ti[id]` -> `usuarios_sistema[personal_ti_id]`, `historico_reubicaciones_equipos[responsable_personal_ti_id]`, etc.
- (1) `monitor_sites[id]` -> `monitor_notifications[site_id]`.
- Tablas puente (N:N): `usuario_grupo`, `usuario_notas_exclusiones`,
  `control_acceso_tarjeta_puertas`, `incidencias_control_acceso_puertas` se modelan
  con dos relaciones (una a cada lado).

## 5. Modelo de estrellas / medidas

1. Crear la tabla de fechas `Dim_Fecha` (bloque del archivo `SGTI_Measures.dax`).
2. Crear las medidas KPIs pegando `SGTI_Measures.dax` en `Modelo > Nueva medida`.
   Cada medida debe pegarse como medida propia (o usar `DAX Studio` para batch).
3. Marcar `Dim_Fecha` como tabla de fechas: `Modelo > Marcar como tabla de fechas`.

## 6. Roles RLS

1. `Modelo > Administrar roles`.
2. Crear roles con las reglas de `powerbi/SGTI_RLS.md`.
3. Probar con `Modelo > Ver como roles`.

## 7. Paginas de reporte sugeridas

1. **Ejecutivo**: KPIs (empleados, coordinaciones, oficios, licencias, suministros).
2. **Activos / Equipo**: reubicaciones, equipos portatiles, licenciamiento.
3. **Suministros**: ingresos vs entregas vs disponibilidad por coordinacion.
4. **Documentos**: oficios recibidos (contestados, YTD), notas y minutas.
5. **Personal y Accesos**: vacaciones, cuentas de usuario, tarjetas y puertas.
6. **Auditoria y Monitor**: eventos por accion, sitios arriba/abajo.

## 8. Publicar y refrescar

Ver `REFRESH_GUIDE.md`.

## Notas
- Los datos son de **lectura directa del Parquet**: un refresh solo vuelve a leer
  los archivos de `Data/parquet`. No hay base de datos intermedia.
- Los valores de tiempo (columnas `hora_*`) quedaron como texto `HH:MM:SS`; usar
  `TIMEVALUE()` al filtrar dentro de Power BI.
- El campo `password_hash` y `password_asignado_cifrado` contienen hashes; no exponerlos
  en ningun visual.