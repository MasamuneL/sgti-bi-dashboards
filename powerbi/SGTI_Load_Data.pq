// ============================================================
//  SGTI - Carga de datos desde archivos Parquet
//  -----------------------------------------------------------
//  1) Reemplace PARQUET_FOLDER_ABSOLUTE por la ruta completa a su carpeta
//     'Data/parquet' (ejemplo local: C:\ÁREA_DE_TRABAJO\Data\parquet)
//  2) Pegue cada consulta en Power Query Desktop (Advanced Editor).
//  3) El modelo se conecta a la carpeta Parquet; un refresh solo.
//     re-importa los archivos .parquet mas recientes.
// ============================================================

// -----------------------------------------------------------
// Consulta de funcion (cree UNA consulta llamada fnLoadParquet)
// -----------------------------------------------------------
let
    fnLoadParquet = (path as text) as table =>
        let
            Source = Parquet.Contents(File.Contents(path))
        in
            Source
in
    fnLoadParquet

// -----------------------------------------------------------
// Consultas de tablas (una consulta por archivo Parquet)
// Reemplace PARQUET_FOLDER_ABSOLUTE por la ruta absoluta a 'Data\parquet',
// p. ej. C:\Data\parquet
// -----------------------------------------------------------

// --- aplicativos_licencia ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\aplicativos_licencia.parquet")
in
    Source

// --- asignaciones_licenciamiento ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\asignaciones_licenciamiento.parquet")
in
    Source

// --- audit_log ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\audit_log.parquet")
in
    Source

// --- bitacora_equipo_portatil ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\bitacora_equipo_portatil.parquet")
in
    Source

// --- bitacora_omision_reportes ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\bitacora_omision_reportes.parquet")
in
    Source

// --- catalogo_suministros ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\catalogo_suministros.parquet")
in
    Source

// --- control_acceso_idfs ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\control_acceso_idfs.parquet")
in
    Source

// --- control_acceso_paneles ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\control_acceso_paneles.parquet")
in
    Source

// --- control_acceso_pisos ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\control_acceso_pisos.parquet")
in
    Source

// --- control_acceso_puertas ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\control_acceso_puertas.parquet")
in
    Source

// --- control_acceso_tarjeta_puertas ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\control_acceso_tarjeta_puertas.parquet")
in
    Source

// --- control_acceso_tarjetas ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\control_acceso_tarjetas.parquet")
in
    Source

// --- control_acceso_tipos_panel ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\control_acceso_tipos_panel.parquet")
in
    Source

// --- coordinaciones ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\coordinaciones.parquet")
in
    Source

// --- cuentas_usuario ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\cuentas_usuario.parquet")
in
    Source

// --- entregas_suministro ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\entregas_suministro.parquet")
in
    Source

// --- entregas_suministro_consumos ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\entregas_suministro_consumos.parquet")
in
    Source

// --- grupo_permisos_detalle ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\grupo_permisos_detalle.parquet")
in
    Source

// --- grupos_permisos ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\grupos_permisos.parquet")
in
    Source

// --- historico_reubicaciones_equipos ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\historico_reubicaciones_equipos.parquet")
in
    Source

// --- incidencias_acceso_escalaciones ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\incidencias_acceso_escalaciones.parquet")
in
    Source

// --- incidencias_acceso_notas_informativas ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\incidencias_acceso_notas_informativas.parquet")
in
    Source

// --- incidencias_control_acceso ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\incidencias_control_acceso.parquet")
in
    Source

// --- incidencias_control_acceso_puertas ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\incidencias_control_acceso_puertas.parquet")
in
    Source

// --- ingresos_suministro ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\ingresos_suministro.parquet")
in
    Source

// --- minutas_circulares ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\minutas_circulares.parquet")
in
    Source

// --- monitor_notifications ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\monitor_notifications.parquet")
in
    Source

// --- monitor_sites ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\monitor_sites.parquet")
in
    Source

// --- notas_informativas ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\notas_informativas.parquet")
in
    Source

// --- oficios_realizados ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\oficios_realizados.parquet")
in
    Source

// --- oficios_recibidos ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\oficios_recibidos.parquet")
in
    Source

// --- perfiles_sistema ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\perfiles_sistema.parquet")
in
    Source

// --- personal_hospital ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\personal_hospital.parquet")
in
    Source

// --- personal_ti ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\personal_ti.parquet")
in
    Source

// --- pisos_reubicacion ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\pisos_reubicacion.parquet")
in
    Source

// --- puestos_cargo ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\puestos_cargo.parquet")
in
    Source

// --- usuario_grupo ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\usuario_grupo.parquet")
in
    Source

// --- usuario_minutas_exclusiones ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\usuario_minutas_exclusiones.parquet")
in
    Source

// --- usuario_modulos ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\usuario_modulos.parquet")
in
    Source

// --- usuario_notas_exclusiones ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\usuario_notas_exclusiones.parquet")
in
    Source

// --- usuarios_sistema ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\usuarios_sistema.parquet")
in
    Source

// --- vacaciones_incidencias ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\vacaciones_incidencias.parquet")
in
    Source

// --- vacaciones_incidencias_fechas ---
let
    Source = fnLoadParquet("PARQUET_FOLDER_ABSOLUTE\vacaciones_incidencias_fechas.parquet")
in
    Source