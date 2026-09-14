# DATA_DICTIONARY.md

Diccionario de datos del SGTI generado automaticamente desde los archivos Parquet.

- Carpeta origen: `Data/parquet/`
- Total de tablas: `43`

## 1. Tablas

| Tabla | Dominio | Filas | Descripcion |
|-------|---------|------:|-------------|
| `aplicativos_licencia` | Catálogo | 4 | Software licensed (Office, Adobe, Creative Cloud, etc.). |
| `asignaciones_licenciamiento` | Fact | 149 | License assignments to personnel (hostname, GLPI id, status). |
| `audit_log` | Fact | 2,452 | Audit trail of every create/update/delete across the system. |
| `bitacora_equipo_portatil` | Fact | 53 | Loan log for portable/laptop equipment. |
| `bitacora_omision_reportes` | Fact | 7 | Missed daily activity reports by IT staff. |
| `catalogo_suministros` | Catálogo | 5 | Supply catalog (toners, paper and models/brands). |
| `control_acceso_idfs` | Catálogo | 5 | IDF (Intermediate Distribution Frame) catalog. |
| `control_acceso_paneles` | Catálogo | 10 | Access-control panels catalog. |
| `control_acceso_pisos` | Catálogo | 4 | Floors used by access control. |
| `control_acceso_puertas` | Catálogo | 64 | Door catalog (one per access point). |
| `control_acceso_tarjeta_puertas` | Bridge | 22 | N:N mapping cards <-> doors. |
| `control_acceso_tarjetas` | Fact | 5 | Physical access cards and their responsivas. |
| `control_acceso_tipos_panel` | Catálogo | 2 | Panel types for access control. |
| `coordinaciones` | Catálogo | 39 | Hospital coordinations/departments. |
| `cuentas_usuario` | Fact | 646 | User account requests (creation, delivery, negatives). |
| `entregas_suministro` | Fact | 161 | Supply deliveries to coordinations (printer serials, counters). |
| `entregas_suministro_consumos` | Fact | 168 | Per-delivery consumption of ingreso stock. |
| `grupo_permisos_detalle` | Bridge | 30 | Granular module permissions per permission group. |
| `grupos_permisos` | Catálogo | 2 | Permission groups catalog. |
| `historico_reubicaciones_equipos` | Fact | 84 | History of equipment relocations (computers, printers, phones). |
| `incidencias_acceso_escalaciones` | Fact | 1 | Access-control incident escalations to providers. |
| `incidencias_acceso_notas_informativas` | Fact | 1 | Informative notes tied to access-control incidents. |
| `incidencias_control_acceso` | Fact | 1 | Access-control incidents. |
| `incidencias_control_acceso_puertas` | Bridge | 0 | N:N mapping incidents <-> doors. |
| `ingresos_suministro` | Fact | 24 | Supply intake/receipts with contract numbers. |
| `minutas_circulares` | Fact | 12 | Meeting minutes and circulars. |
| `monitor_notifications` | Fact | 23 | Uptime/downtime notifications from site health monitor. |
| `monitor_sites` | Catálogo | 3 | Monitored systems (SITAU, SIPAC, SIMEF). |
| `notas_informativas` | Fact | 529 | Informative notes / daily activity reports. |
| `oficios_realizados` | Fact | 245 | Official documents sent out. |
| `oficios_recibidos` | Fact | 373 | Official documents received. |
| `perfiles_sistema` | Catálogo | 5 | System profiles (Admin, Coordinator, Technician, etc.). |
| `personal_hospital` | Catálogo | 1,663 | Full hospital staff directory. |
| `personal_ti` | Catálogo | 27 | IT department personnel. |
| `pisos_reubicacion` | Catálogo | 4 | Floors used by equipment relocations. |
| `puestos_cargo` | Catálogo | 31 | Job position catalog. |
| `usuario_grupo` | Bridge | 16 | User -> permission group assignments. |
| `usuario_minutas_exclusiones` | Bridge | 0 | Users excluded from seeing specific minutes (empty). |
| `usuario_modulos` | Fact | 345 | Granular module permissions per system user. |
| `usuario_notas_exclusiones` | Bridge | 147 | Users excluded from seeing specific notes. |
| `usuarios_sistema` | Catálogo | 23 | Application users (linked to personal_ti). |
| `vacaciones_incidencias` | Fact | 38 | Vacation / incident requests with approval workflow. |
| `vacaciones_incidencias_fechas` | Fact | 100 | Specific dates covered by a vacation/incident request. |

## 2. Esquemas (columnas y tipos)

### `aplicativos_licencia` (4 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `nombre` | text |
| `creado_por_id` | int64 |
| `activo` | bool |
| `created_at` | timestamp[us, tz=UTC] |

### `asignaciones_licenciamiento` (149 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `asignacion_anterior_id` | int64 |
| `hostname` | text |
| `glpi_id` | int64 |
| `nombre_completo` | text |
| `area_departamento` | text |
| `coordinacion_id` | int64 |
| `coordinacion_nombre` | text |
| `correo` | text |
| `aplicativo_id` | int64 |
| `aplicativo_nombre` | text |
| `fecha_asignacion` | date32[day] |
| `estatus` | text |
| `fecha_reasignacion` | date32[day] |
| `fecha_baja` | date32[day] |
| `baja_autorizada_por_id` | int64 |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `audit_log` (2,452 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `usuario_id` | int64 |
| `accion` | text |
| `modulo` | text |
| `descripcion` | text |
| `registro_id` | int64 |
| `ip` | text |
| `user_agent` | text |
| `timestamp` | timestamp[us, tz=UTC] |
| `tabla_objetivo` | text |
| `registro_etiqueta` | text |
| `datos_antes` | text |
| `datos_despues` | text |
| `campos_modificados` | text |
| `metadata` | text |

### `bitacora_equipo_portatil` (53 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `departamento_id` | int64 |
| `personal_ti_id` | int64 |
| `nombre_usuario` | text |
| `numero_empleado` | int64 |
| `fecha_asignacion` | date32[day] |
| `hora_asignacion` | text |
| `fecha_devolucion` | date32[day] |
| `hora_devolucion` | text |
| `devolucion_qr_token_hash` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `bitacora_omision_reportes` (7 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `personal_ti_id` | int64 |
| `area` | text |
| `fecha_omision` | date32[day] |
| `observaciones` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `catalogo_suministros` (5 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `tipo_suministro` | text |
| `nombre` | text |
| `creado_por_id` | int64 |
| `activo` | bool |
| `created_at` | timestamp[us, tz=UTC] |

### `control_acceso_idfs` (5 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `source_id` | int64 |
| `piso_id` | int64 |
| `nombre` | text |
| `activo` | bool |

### `control_acceso_paneles` (10 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `source_id` | int64 |
| `idf_id` | int64 |
| `tipo_panel_id` | int64 |
| `nombre` | text |
| `activo` | bool |

### `control_acceso_pisos` (4 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `source_id` | int64 |
| `nombre` | text |
| `activo` | bool |

### `control_acceso_puertas` (64 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `source_id` | int64 |
| `panel_id` | int64 |
| `nombre` | text |
| `activo` | bool |

### `control_acceso_tarjeta_puertas` (22 filas)

| Columna | Tipo |
|---------|------|
| `control_acceso_tarjeta_id` | int64 |
| `puerta_id` | int64 |
| `puerta_nombre_snapshot` | text |

### `control_acceso_tarjetas` (5 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `personal_hospital_id` | int64 |
| `oficio_correspondiente` | text |
| `fecha_activacion` | date32[day] |
| `estatus_responsiva` | text |
| `numero_tarjeta` | int64 |
| `nombre_completo` | text |
| `numero_empleado` | int64 |
| `turno` | text |
| `ubicacion` | text |
| `coordinacion_id` | int64 |
| `coordinacion_nombre_snapshot` | text |
| `puertas` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |
| `pdf_nombre_original` | text |
| `pdf_nombre_archivo` | text |
| `pdf_ruta` | text |
| `pdf_mime` | text |
| `pdf_tamano` | int64 |
| `pdf_subido_at` | timestamp[us, tz=UTC] |

### `control_acceso_tipos_panel` (2 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `source_id` | int64 |
| `nombre` | text |
| `activo` | bool |

### `coordinaciones` (39 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `nombre` | text |
| `nombre_coordinador` | text |
| `activo` | bool |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `cuentas_usuario` (646 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `fecha_captura` | date32[day] |
| `nombre_completo` | text |
| `puesto_id` | int64 |
| `coordinacion_id` | int64 |
| `username_asignado` | text |
| `password_asignado_cifrado` | text |
| `correo` | text |
| `es_cuenta_generica` | bool |
| `estatus` | text |
| `quien_entrega_id` | int64 |
| `fecha_entrega` | date32[day] |
| `perfil_id` | int64 |
| `se_da_negativa` | bool |
| `observaciones` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `entregas_suministro` (161 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `tipo_suministro` | text |
| `modelo_marca_id` | int64 |
| `modelo_marca_nombre` | text |
| `tamano` | text |
| `cantidad` | int64 |
| `folio_ticket` | text |
| `numero_serie_impresora` | text |
| `consecutivo_asignado` | int64 |
| `coordinacion_id` | int64 |
| `coordinacion_nombre` | text |
| `contador_total` | int64 |
| `fecha_cambio` | date32[day] |
| `tecnico_personal_ti_id` | int64 |
| `tecnico_nombre` | text |
| `quien_recibe_personal_ti_id` | int64 |
| `quien_recibe_personal_hospital_id` | int64 |
| `quien_recibe_nombre` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |
| `pdf_nombre_original` | text |
| `pdf_nombre_archivo` | text |
| `pdf_ruta` | text |
| `pdf_mime` | text |
| `pdf_tamano` | int64 |
| `pdf_subido_at` | timestamp[us, tz=UTC] |

### `entregas_suministro_consumos` (168 filas)

| Columna | Tipo |
|---------|------|
| `entrega_id` | int64 |
| `ingreso_id` | int64 |
| `cantidad` | int64 |

### `grupo_permisos_detalle` (30 filas)

| Columna | Tipo |
|---------|------|
| `grupo_id` | int64 |
| `modulo` | text |
| `permitido` | bool |
| `puede_eliminar` | bool |
| `puede_editar` | bool |
| `puede_aprobar_vacaciones` | bool |
| `puede_ver_todos_excepto` | bool |
| `puede_ver_todos_excepto_minutas` | bool |
| `puede_agregar_suministro` | bool |
| `puede_entregar_papel_suministro` | bool |
| `puede_asignar_toner_suministro` | bool |
| `puede_ver_graficas_suministro` | bool |
| `puede_ver_inventario_suministro` | bool |
| `puede_ver_toners_suministro` | bool |
| `puede_ver_papel_suministro` | bool |
| `puede_ver_contratos_suministro` | bool |
| `puede_ocultar_instrucciones` | bool |

### `grupos_permisos` (2 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `nombre` | text |
| `descripcion` | text |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `historico_reubicaciones_equipos` (84 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `tipo_equipo` | text |
| `identificador_equipo` | text |
| `numero_ticket_oficio` | text |
| `ubicacion_anterior` | text |
| `piso_anterior_id` | int64 |
| `piso_anterior_nombre` | text |
| `responsable_personal_ti_id` | int64 |
| `responsable_nombre` | text |
| `coordinacion_origen_id` | int64 |
| `coordinacion_origen_nombre` | text |
| `fecha_hora_movimiento` | timestamp[us, tz=UTC] |
| `nueva_ubicacion` | text |
| `piso_nuevo_id` | int64 |
| `piso_nuevo_nombre` | text |
| `coordinacion_destino_id` | int64 |
| `coordinacion_destino_nombre` | text |
| `fecha_hora_reubicacion` | timestamp[us, tz=UTC] |
| `estatus` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `incidencias_acceso_escalaciones` (1 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `incidencia_id` | int64 |
| `numero_atencion_interna` | text |
| `estatus` | text |
| `observaciones_proveedor` | text |
| `pdf_nombre_original` | text |
| `pdf_nombre_archivo` | text |
| `pdf_ruta` | text |
| `pdf_mime` | text |
| `pdf_tamano` | int64 |
| `pdf_subido_at` | timestamp[us, tz=UTC] |
| `registrado_por_id` | int64 |
| `actualizado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `incidencias_acceso_notas_informativas` (1 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `incidencia_id` | int64 |
| `incidencia_snapshot` | text |
| `fecha_elaboracion` | date32[day] |
| `lugar_elaboracion` | text |
| `periodo_inicio` | date32[day] |
| `periodo_fin` | date32[day] |
| `area_responsable` | text |
| `responsable_reporte` | text |
| `cargo_responsable` | text |
| `turno_jornada` | text |
| `objetivo` | text |
| `actividad_realizada` | text |
| `equipo_sistema_servicio` | text |
| `resultado_estatus` | text |
| `observaciones_actividad` | text |
| `causa` | text |
| `atencion_proporcionada` | text |
| `afectacion` | text |
| `mantenimiento_acciones_preventivas` | text |
| `resultados` | text |
| `pendientes_seguimiento` | text |
| `conclusion` | text |
| `firmante_nombre` | text |
| `firmante_cargo_area` | text |
| `observaciones_proveedor_snapshot` | text |
| `plantilla_version` | text |
| `creado_por_id` | int64 |
| `actualizado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `incidencias_control_acceso` (1 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `numero_ticket_servicio` | text |
| `tipo_incidencia` | text |
| `panel_id` | int64 |
| `idf_id` | int64 |
| `piso_id` | int64 |
| `puertas_involucradas` | text |
| `piso` | text |
| `fecha_falla` | date32[day] |
| `observaciones` | text |
| `requiere_atencion_proveedor` | bool |
| `panel_nombre_snapshot` | text |
| `idf_nombre_snapshot` | text |
| `piso_nombre_snapshot` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |
| `pdf_nombre_original` | text |
| `pdf_nombre_archivo` | text |
| `pdf_ruta` | text |
| `pdf_mime` | text |
| `pdf_tamano` | int64 |
| `pdf_subido_at` | timestamp[us, tz=UTC] |

### `incidencias_control_acceso_puertas` (0 filas)

| Columna | Tipo |
|---------|------|
| `incidencia_id` | int64 |
| `puerta_id` | int64 |
| `puerta_nombre_snapshot` | text |

### `ingresos_suministro` (24 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `tipo_suministro` | text |
| `modelo_marca_id` | int64 |
| `modelo_marca_nombre` | text |
| `tamano` | text |
| `cantidad` | int64 |
| `cantidad_disponible` | int64 |
| `monto` | double |
| `fecha_ingreso` | date32[day] |
| `numero_contrato` | text |
| `quien_recibe_personal_ti_id` | int64 |
| `quien_recibe_nombre` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `minutas_circulares` (12 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `fecha` | date32[day] |
| `nombre` | text |
| `departamento` | text |
| `elaboro_id` | int64 |
| `departamento_id` | int64 |
| `asunto` | text |
| `observaciones` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |
| `pdf_nombre_original` | text |
| `pdf_nombre_archivo` | text |
| `pdf_ruta` | text |
| `pdf_mime` | text |
| `pdf_tamano` | int64 |
| `pdf_subido_at` | timestamp[us, tz=UTC] |

### `monitor_notifications` (23 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `site_id` | int64 |
| `event_type` | text |
| `title` | text |
| `detail` | text |
| `read_at` | timestamp[us, tz=UTC] |
| `created_at` | timestamp[us, tz=UTC] |

### `monitor_sites` (3 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `nombre` | text |
| `url` | text |
| `method` | text |
| `expected_status` | int64 |
| `timeout_seconds` | int64 |
| `check_interval_seconds` | int64 |
| `failure_threshold` | int64 |
| `success_threshold` | int64 |
| `consecutive_failures` | int64 |
| `consecutive_successes` | int64 |
| `current_status` | text |
| `last_checked_at` | timestamp[us, tz=UTC] |
| `last_status_change_at` | timestamp[us, tz=UTC] |
| `last_latency_ms` | int64 |
| `last_error_message` | text |
| `registrado_por_id` | int64 |
| `activo` | bool |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `notas_informativas` (529 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `fecha` | date32[day] |
| `nombre` | text |
| `departamento` | text |
| `elaboro_id` | int64 |
| `departamento_id` | int64 |
| `asunto` | text |
| `observaciones` | text |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |
| `pdf_nombre_original` | text |
| `pdf_nombre_archivo` | text |
| `pdf_ruta` | text |
| `pdf_mime` | text |
| `pdf_tamano` | int64 |
| `pdf_subido_at` | timestamp[us, tz=UTC] |

### `oficios_realizados` (245 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `fecha_inicio` | date32[day] |
| `fecha_fin` | date32[day] |
| `numero_oficio` | text |
| `dirigido_a` | text |
| `departamento` | text |
| `departamento_id` | int64 |
| `asunto` | text |
| `entregado` | bool |
| `cancelado` | bool |
| `observacion` | text |
| `mes` | text |
| `elaborado_por_id` | int64 |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |
| `pdf_nombre_original` | text |
| `pdf_nombre_archivo` | text |
| `pdf_ruta` | text |
| `pdf_mime` | text |
| `pdf_tamano` | int64 |
| `pdf_subido_at` | timestamp[us, tz=UTC] |

### `oficios_recibidos` (373 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `fecha_recepcion` | date32[day] |
| `hora_recepcion` | text |
| `fecha_inicial` | date32[day] |
| `fecha_fin` | date32[day] |
| `numero_oficio` | text |
| `nombre_remitente` | text |
| `departamento` | text |
| `departamento_id` | int64 |
| `asunto` | text |
| `notificacion` | bool |
| `contestado` | bool |
| `fecha_contestado` | date32[day] |
| `dias_transcurridos` | int64 |
| `observacion` | text |
| `atendido_por_id` | int64 |
| `registrado_por_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |
| `pdf_nombre_original` | text |
| `pdf_nombre_archivo` | text |
| `pdf_ruta` | text |
| `pdf_mime` | text |
| `pdf_tamano` | int64 |
| `pdf_subido_at` | timestamp[us, tz=UTC] |

### `perfiles_sistema` (5 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `nombre_perfil` | text |
| `descripcion` | text |
| `activo` | bool |
| `created_at` | timestamp[us, tz=UTC] |

### `personal_hospital` (1,663 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `numero_empleado` | int64 |
| `apellidos` | text |
| `nombres` | text |
| `nombre_completo` | text |
| `numero_plaza` | int64 |
| `servicio` | text |
| `puesto` | text |
| `coordinacion_nombre` | text |
| `coordinacion_id` | int64 |
| `jornada` | text |
| `hora_entrada` | text |
| `hora_salida` | text |
| `dias_laborales` | text |
| `status_laboral` | text |
| `activo` | bool |
| `fuente_fila` | text |
| `importado_por_id` | int64 |
| `ultima_importacion_at` | timestamp[us, tz=UTC] |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `personal_ti` (27 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `nombre` | text |
| `puesto` | text |
| `departamento` | text |
| `correo` | text |
| `extension` | int64 |
| `activo` | bool |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `pisos_reubicacion` (4 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `nombre` | text |
| `creado_por_id` | int64 |
| `activo` | bool |
| `created_at` | timestamp[us, tz=UTC] |

### `puestos_cargo` (31 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `denominacion` | text |
| `activo` | bool |
| `created_at` | timestamp[us, tz=UTC] |

### `usuario_grupo` (16 filas)

| Columna | Tipo |
|---------|------|
| `usuario_id` | int64 |
| `grupo_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |

### `usuario_minutas_exclusiones` (0 filas)

| Columna | Tipo |
|---------|------|
| `usuario_id` | int64 |
| `persona_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |

### `usuario_modulos` (345 filas)

| Columna | Tipo |
|---------|------|
| `usuario_id` | int64 |
| `modulo` | text |
| `permitido` | bool |
| `puede_eliminar` | bool |
| `puede_editar` | bool |
| `puede_ver_todos_excepto` | bool |
| `puede_ver_todos_excepto_minutas` | bool |
| `puede_agregar_suministro` | bool |
| `puede_entregar_papel_suministro` | bool |
| `puede_asignar_toner_suministro` | bool |
| `puede_ver_graficas_suministro` | bool |
| `puede_ver_inventario_suministro` | bool |
| `puede_ver_toners_suministro` | bool |
| `puede_ver_papel_suministro` | bool |
| `puede_ver_contratos_suministro` | bool |
| `puede_ocultar_instrucciones` | bool |
| `puede_aprobar_vacaciones` | bool |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `usuario_notas_exclusiones` (147 filas)

| Columna | Tipo |
|---------|------|
| `usuario_id` | int64 |
| `persona_id` | int64 |
| `created_at` | timestamp[us, tz=UTC] |

### `usuarios_sistema` (23 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `personal_ti_id` | int64 |
| `username` | text |
| `password_hash` | text |
| `rol` | text |
| `activo` | bool |
| `ultimo_acceso` | text |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |
| `avatar_url` | text |

### `vacaciones_incidencias` (38 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `personal_ti_id` | int64 |
| `tipo` | text |
| `estado_aprobacion` | text |
| `fecha_inicio` | date32[day] |
| `fecha_fin` | date32[day] |
| `nota` | text |
| `justificacion_declinado` | text |
| `registrado_por_id` | int64 |
| `resuelto_por_id` | int64 |
| `resuelto_at` | timestamp[us, tz=UTC] |
| `created_at` | timestamp[us, tz=UTC] |
| `updated_at` | timestamp[us, tz=UTC] |

### `vacaciones_incidencias_fechas` (100 filas)

| Columna | Tipo |
|---------|------|
| `id` | int64 |
| `vacaciones_incidencia_id` | int64 |
| `fecha` | date32[day] |

## 3. Relaciones (modelo dimensional)

Direccion: tabla de hechos -> tabla de dimension (1:N).

| Dimension (lado 1) | Tabla de hechos/transaccion | Columna |
|--------------------|-----------------------------|---------|
| `coordinaciones.id` | `asignaciones_licenciamiento` | `coordinacion_id` |
| `aplicativos_licencia.id` | `asignaciones_licenciamiento` | `aplicativo_id` |
| `coordinaciones.id` | `bitacora_equipo_portatil` | `departamento_id` |
| `personal_ti.id` | `bitacora_equipo_portatil` | `personal_ti_id` |
| `personal_hospital.numero_empleado` | `bitacora_equipo_portatil` | `numero_empleado` |
| `personal_ti.id` | `bitacora_omision_reportes` | `personal_ti_id` |
| `coordinaciones.id` | `control_acceso_tarjetas` | `coordinacion_id` |
| `personal_hospital.id` | `control_acceso_tarjetas` | `personal_hospital_id` |
| `control_acceso_tarjetas.id` | `control_acceso_tarjeta_puertas` | `control_acceso_tarjeta_id` |
| `control_acceso_puertas.id` | `control_acceso_tarjeta_puertas` | `puerta_id` |
| `coordinaciones.id` | `cuentas_usuario` | `coordinacion_id` |
| `puestos_cargo.id` | `cuentas_usuario` | `puesto_id` |
| `perfiles_sistema.id` | `cuentas_usuario` | `perfil_id` |
| `coordinaciones.id` | `entregas_suministro` | `coordinacion_id` |
| `personal_ti.id` | `entregas_suministro` | `tecnico_personal_ti_id` |
| `entregas_suministro.id` | `entregas_suministro_consumos` | `entrega_id` |
| `ingresos_suministro.id` | `entregas_suministro_consumos` | `ingreso_id` |
| `grupos_permisos.id` | `grupo_permisos_detalle` | `grupo_id` |
| `coordinaciones.id` | `historico_reubicaciones_equipos` | `coordinacion_origen_id` |
| `coordinaciones.id` | `historico_reubicaciones_equipos` | `coordinacion_destino_id` |
| `pisos_reubicacion.id` | `historico_reubicaciones_equipos` | `piso_anterior_id` |
| `pisos_reubicacion.id` | `historico_reubicaciones_equipos` | `piso_nuevo_id` |
| `personal_ti.id` | `historico_reubicaciones_equipos` | `responsable_personal_ti_id` |
| `incidencias_control_acceso.id` | `incidencias_acceso_escalaciones` | `incidencia_id` |
| `incidencias_control_acceso.id` | `incidencias_acceso_notas_informativas` | `incidencia_id` |
| `control_acceso_paneles.id` | `incidencias_control_acceso` | `panel_id` |
| `control_acceso_idfs.id` | `incidencias_control_acceso` | `idf_id` |
| `control_acceso_pisos.id` | `incidencias_control_acceso` | `piso_id` |
| `incidencias_control_acceso.id` | `incidencias_control_acceso_puertas` | `incidencia_id` |
| `control_acceso_puertas.id` | `incidencias_control_acceso_puertas` | `puerta_id` |
| `catalogo_suministros.id` | `ingresos_suministro` | `modelo_marca_id` |
| `personal_ti.id` | `ingresos_suministro` | `quien_recibe_personal_ti_id` |
| `personal_ti.id` | `minutas_circulares` | `elaboro_id` |
| `coordinaciones.id` | `minutas_circulares` | `departamento_id` |
| `monitor_sites.id` | `monitor_notifications` | `site_id` |
| `personal_ti.id` | `notas_informativas` | `elaboro_id` |
| `coordinaciones.id` | `notas_informativas` | `departamento_id` |
| `coordinaciones.id` | `oficios_realizados` | `departamento_id` |
| `personal_ti.id` | `oficios_realizados` | `elaborado_por_id` |
| `coordinaciones.id` | `oficios_recibidos` | `departamento_id` |
| `personal_ti.id` | `oficios_recibidos` | `atendido_por_id` |
| `usuarios_sistema.id` | `usuario_grupo` | `usuario_id` |
| `grupos_permisos.id` | `usuario_grupo` | `grupo_id` |
| `usuarios_sistema.id` | `usuario_modulos` | `usuario_id` |
| `usuarios_sistema.id` | `usuario_notas_exclusiones` | `usuario_id` |
| `personal_hospital.id` | `usuario_notas_exclusiones` | `persona_id` |
| `usuarios_sistema.id` | `usuario_minutas_exclusiones` | `usuario_id` |
| `personal_hospital.id` | `usuario_minutas_exclusiones` | `persona_id` |
| `personal_ti.id` | `usuarios_sistema` | `personal_ti_id` |
| `personal_ti.id` | `vacaciones_incidencias` | `personal_ti_id` |
| `usuarios_sistema.id` | `vacaciones_incidencias` | `registrado_por_id` |
| `vacaciones_incidencias.id` | `vacaciones_incidencias_fechas` | `vacaciones_incidencia_id` |
| `usuarios_sistema.id` | `audit_log` | `usuario_id` |

## 4. Notas de tipo

- `date32[day]`: fecha normalizada `YYYY-MM-DD`.
- `timestamp[us, tz=UTC]`: fecha-hora en UTC (desplazame la zona en el modelo de Power BI).
- `int64` nullable: ids y cantidades; sin `Int64` de numpy por compatibilidad.
- Colores `bool`: banderas `activo`, `permitido`, `puede_*`, `entregado`, `contestado`, etc.