"""Genera datos de muestra SINTÉTICOS y anónimos para el repo público.

Escribe 43 CSVs + manifest.json en `sample_data/` con el MISMO esquema (columnas
y tipos) que la exportación real del SGTI, pero con valores ficticios obvios
(nombres "Persona Ejemplo NN", correos @ejemplo.gob.mx, fechas dentro de 2026).

Uso:
    .venv/bin/python scripts/build_sample_data.py           # (re)genera sample_data/
    .venv/bin/python scripts/csv_to_parquet.py \
        --csv-dir sample_data --out-dir Data/parquet        # convierte a Parquet
    .venv/bin/python scripts/build_dashboard_v3.py          # regenera los dashboards

Para usar datos reales, NO se ejecuta este script: se copia la exportación CSV del
SGTI a Data/ y se corre `scripts/refresh_all.py` (ver README.md).
"""
from __future__ import annotations

import json
import os
import random
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "sample_data")

# Esquema real (nombre de columna por tabla), extraído de los Parquet originales.
# Es la "plantilla" que el usuario sustituye por su exportación real.
SCHEMA = {
    "aplicativos_licencia": "id,nombre,creado_por_id,activo,created_at",
    "asignaciones_licenciamiento": "id,asignacion_anterior_id,hostname,glpi_id,nombre_completo,area_departamento,coordinacion_id,coordinacion_nombre,correo,aplicativo_id,aplicativo_nombre,fecha_asignacion,estatus,fecha_reasignacion,fecha_baja,baja_autorizada_por_id,registrado_por_id,created_at,updated_at",
    "audit_log": "id,usuario_id,accion,modulo,descripcion,registro_id,ip,user_agent,timestamp,tabla_objetivo,registro_etiqueta,datos_antes,datos_despues,campos_modificados,metadata",
    "bitacora_equipo_portatil": "id,departamento_id,personal_ti_id,nombre_usuario,numero_empleado,fecha_asignacion,hora_asignacion,fecha_devolucion,hora_devolucion,devolucion_qr_token_hash,registrado_por_id,created_at,updated_at",
    "bitacora_omision_reportes": "id,personal_ti_id,area,fecha_omision,observaciones,registrado_por_id,created_at,updated_at",
    "catalogo_suministros": "id,tipo_suministro,nombre,creado_por_id,activo,created_at",
    "control_acceso_idfs": "id,source_id,piso_id,nombre,activo",
    "control_acceso_paneles": "id,source_id,idf_id,tipo_panel_id,nombre,activo",
    "control_acceso_pisos": "id,source_id,nombre,activo",
    "control_acceso_puertas": "id,source_id,panel_id,nombre,activo",
    "control_acceso_tarjeta_puertas": "control_acceso_tarjeta_id,puerta_id,puerta_nombre_snapshot",
    "control_acceso_tarjetas": "id,personal_hospital_id,oficio_correspondiente,fecha_activacion,estatus_responsiva,numero_tarjeta,nombre_completo,numero_empleado,turno,ubicacion,coordinacion_id,coordinacion_nombre_snapshot,puertas,registrado_por_id,created_at,updated_at,pdf_nombre_original,pdf_nombre_archivo,pdf_ruta,pdf_mime,pdf_tamano,pdf_subido_at",
    "control_acceso_tipos_panel": "id,source_id,nombre,activo",
    "coordinaciones": "id,nombre,nombre_coordinador,activo,created_at,updated_at",
    "cuentas_usuario": "id,fecha_captura,nombre_completo,puesto_id,coordinacion_id,username_asignado,password_asignado_cifrado,correo,es_cuenta_generica,estatus,quien_entrega_id,fecha_entrega,perfil_id,se_da_negativa,observaciones,registrado_por_id,created_at,updated_at",
    "entregas_suministro": "id,tipo_suministro,modelo_marca_id,modelo_marca_nombre,tamano,cantidad,folio_ticket,numero_serie_impresora,consecutivo_asignado,coordinacion_id,coordinacion_nombre,contador_total,fecha_cambio,tecnico_personal_ti_id,tecnico_nombre,quien_recibe_personal_ti_id,quien_recibe_personal_hospital_id,quien_recibe_nombre,registrado_por_id,created_at,updated_at,pdf_nombre_original,pdf_nombre_archivo,pdf_ruta,pdf_mime,pdf_tamano,pdf_subido_at",
    "entregas_suministro_consumos": "entrega_id,ingreso_id,cantidad",
    "grupo_permisos_detalle": "grupo_id,modulo,permitido,puede_eliminar,puede_editar,puede_aprobar_vacaciones,puede_ver_todos_excepto,puede_ver_todos_excepto_minutas,puede_agregar_suministro,puede_entregar_papel_suministro,puede_asignar_toner_suministro,puede_ver_graficas_suministro,puede_ver_inventario_suministro,puede_ver_toners_suministro,puede_ver_papel_suministro,puede_ver_contratos_suministro,puede_ocultar_instrucciones",
    "grupos_permisos": "id,nombre,descripcion,created_at,updated_at",
    "historico_reubicaciones_equipos": "id,tipo_equipo,identificador_equipo,numero_ticket_oficio,ubicacion_anterior,piso_anterior_id,piso_anterior_nombre,responsable_personal_ti_id,responsable_nombre,coordinacion_origen_id,coordinacion_origen_nombre,fecha_hora_movimiento,nueva_ubicacion,piso_nuevo_id,piso_nuevo_nombre,coordinacion_destino_id,coordinacion_destino_nombre,fecha_hora_reubicacion,estatus,registrado_por_id,created_at,updated_at",
    "incidencias_acceso_escalaciones": "id,incidencia_id,numero_atencion_interna,estatus,observaciones_proveedor,pdf_nombre_original,pdf_nombre_archivo,pdf_ruta,pdf_mime,pdf_tamano,pdf_subido_at,registrado_por_id,actualizado_por_id,created_at,updated_at",
    "incidencias_acceso_notas_informativas": "id,incidencia_id,incidencia_snapshot,fecha_elaboracion,lugar_elaboracion,periodo_inicio,periodo_fin,area_responsable,responsable_reporte,cargo_responsable,turno_jornada,objetivo,actividad_realizada,equipo_sistema_servicio,resultado_estatus,observaciones_actividad,causa,atencion_proporcionada,afectacion,mantenimiento_acciones_preventivas,resultados,pendientes_seguimiento,conclusion,firmante_nombre,firmante_cargo_area,observaciones_proveedor_snapshot,plantilla_version,creado_por_id,actualizado_por_id,created_at,updated_at",
    "incidencias_control_acceso": "id,numero_ticket_servicio,tipo_incidencia,panel_id,idf_id,piso_id,puertas_involucradas,piso,fecha_falla,observaciones,requiere_atencion_proveedor,panel_nombre_snapshot,idf_nombre_snapshot,piso_nombre_snapshot,registrado_por_id,created_at,updated_at,pdf_nombre_original,pdf_nombre_archivo,pdf_ruta,pdf_mime,pdf_tamano,pdf_subido_at",
    "incidencias_control_acceso_puertas": "incidencia_id,puerta_id,puerta_nombre_snapshot",
    "ingresos_suministro": "id,tipo_suministro,modelo_marca_id,modelo_marca_nombre,tamano,cantidad,cantidad_disponible,monto,fecha_ingreso,numero_contrato,quien_recibe_personal_ti_id,quien_recibe_nombre,registrado_por_id,created_at,updated_at",
    "minutas_circulares": "id,fecha,nombre,departamento,elaboro_id,departamento_id,asunto,observaciones,registrado_por_id,created_at,updated_at,pdf_nombre_original,pdf_nombre_archivo,pdf_ruta,pdf_mime,pdf_tamano,pdf_subido_at",
    "monitor_notifications": "id,site_id,event_type,title,detail,read_at,created_at",
    "monitor_sites": "id,nombre,url,method,expected_status,timeout_seconds,check_interval_seconds,failure_threshold,success_threshold,consecutive_failures,consecutive_successes,current_status,last_checked_at,last_status_change_at,last_latency_ms,last_error_message,registrado_por_id,activo,created_at,updated_at",
    "notas_informativas": "id,fecha,nombre,departamento,elaboro_id,departamento_id,asunto,observaciones,registrado_por_id,created_at,updated_at,pdf_nombre_original,pdf_nombre_archivo,pdf_ruta,pdf_mime,pdf_tamano,pdf_subido_at",
    "oficios_realizados": "id,fecha_inicio,fecha_fin,numero_oficio,dirigido_a,departamento,departamento_id,asunto,entregado,cancelado,observacion,mes,elaborado_por_id,registrado_por_id,created_at,updated_at,pdf_nombre_original,pdf_nombre_archivo,pdf_ruta,pdf_mime,pdf_tamano,pdf_subido_at",
    "oficios_recibidos": "id,fecha_recepcion,hora_recepcion,fecha_inicial,fecha_fin,numero_oficio,nombre_remitente,departamento,departamento_id,asunto,notificacion,contestado,fecha_contestado,dias_transcurridos,observacion,atendido_por_id,registrado_por_id,created_at,updated_at,pdf_nombre_original,pdf_nombre_archivo,pdf_ruta,pdf_mime,pdf_tamano,pdf_subido_at",
    "perfiles_sistema": "id,nombre_perfil,descripcion,activo,created_at",
    "personal_hospital": "id,numero_empleado,apellidos,nombres,nombre_completo,numero_plaza,servicio,puesto,coordinacion_nombre,coordinacion_id,jornada,hora_entrada,hora_salida,dias_laborales,status_laboral,activo,fuente_fila,importado_por_id,ultima_importacion_at,created_at,updated_at",
    "personal_ti": "id,nombre,puesto,departamento,correo,extension,activo,created_at,updated_at",
    "pisos_reubicacion": "id,nombre,creado_por_id,activo,created_at",
    "puestos_cargo": "id,denominacion,activo,created_at",
    "usuario_grupo": "usuario_id,grupo_id,created_at",
    "usuario_minutas_exclusiones": "usuario_id,persona_id,created_at",
    "usuario_modulos": "usuario_id,modulo,permitido,puede_eliminar,puede_editar,puede_ver_todos_excepto,puede_ver_todos_excepto_minutas,puede_agregar_suministro,puede_entregar_papel_suministro,puede_asignar_toner_suministro,puede_ver_graficas_suministro,puede_ver_inventario_suministro,puede_ver_toners_suministro,puede_ver_papel_suministro,puede_ver_contratos_suministro,puede_ocultar_instrucciones,puede_aprobar_vacaciones,created_at,updated_at",
    "usuario_notas_exclusiones": "usuario_id,persona_id,created_at",
    "usuarios_sistema": "id,personal_ti_id,username,password_hash,rol,activo,ultimo_acceso,created_at,updated_at,avatar_url",
    "vacaciones_incidencias": "id,personal_ti_id,tipo,estado_aprobacion,fecha_inicio,fecha_fin,nota,justificacion_declinado,registrado_por_id,resuelto_por_id,resuelto_at,created_at,updated_at",
    "vacaciones_incidencias_fechas": "id,vacaciones_incidencia_id,fecha",
}

# Número de filas sintéticas por tabla. Las tablas que alimentan los dashboards
# tienen volumen suficiente para que las gráficas se vean; el resto, 1-3 filas.
ROW_COUNTS = {
    "coordinaciones": 8, "personal_ti": 6, "personal_hospital": 12,
    "oficios_realizados": 30, "oficios_recibidos": 40,
    "notas_informativas": 30, "minutas_circulares": 8,
    "cuentas_usuario": 40, "entregas_suministro": 20, "ingresos_suministro": 10,
    "historico_reubicaciones_equipos": 15, "asignaciones_licenciamiento": 15,
    "vacaciones_incidencias": 10, "vacaciones_incidencias_fechas": 20,
    "audit_log": 30, "usuarios_sistema": 6, "usuario_modulos": 12,
    "control_acceso_tarjetas": 4, "control_acceso_puertas": 4,
    "control_acceso_paneles": 3, "control_acceso_idfs": 3,
    "control_acceso_pisos": 3, "control_acceso_tipos_panel": 2,
    "catalogo_suministros": 4, "puestos_cargo": 4, "pisos_reubicacion": 4,
    "perfiles_sistema": 3, "grupos_permisos": 2, "grupo_permisos_detalle": 6,
    "usuario_grupo": 6, "usuario_notas_exclusiones": 2,
    "usuario_minutas_exclusiones": 0,
    "monitor_sites": 3, "monitor_notifications": 3,
    "aplicativos_licencia": 3, "entregas_suministro_consumos": 4,
    "bitacora_equipo_portatil": 4, "bitacora_omision_reportes": 2,
    "incidencias_control_acceso": 2, "incidencias_control_acceso_puertas": 0,
    "incidencias_acceso_escalaciones": 1,
    "incidencias_acceso_notas_informativas": 1,
    "control_acceso_tarjeta_puertas": 2,
}

rng = random.Random(20260907)  # determinista


def dstr(y, m, d):
    return f"{y:04d}-{m:02d}-{d:02d}"


def rand_date(start="2026-01-01", end="2026-08-31"):
    a = date.fromisoformat(start)
    b = date.fromisoformat(end)
    n = (b - a).days
    return (a + timedelta(days=rng.randint(0, n))).isoformat()


def rand_ts():
    return rand_date() + "T" + f"{rng.randint(7,18):02d}:{rng.randint(0,59):02d}:00Z"


COORD_NOMBRES = [
    "Dirección", "Subdirección Médica", "Subdirección Administrativa",
    "Coordinación de Informática", "Coordinación de Enfermería",
    "Coordinación de Enseñanza", "Coordinación de Recursos Humanos",
    "Coordinación de Mantenimiento",
]
COORD_RESPONSABLES = [
    "Dra. Ejemplo Uno", "Dr. Ejemplo Dos", "Mtra. Ejemplo Tres",
    "Ing. Ejemplo Cuatro", "E.E. Ejemplo Cinco", "Dr. Ejemplo Seis",
    "Mtro. Ejemplo Siete", "Ing. Ejemplo Ocho",
]

APLICATIVOS = ["Microsoft Office", "Adobe Acrobat Pro", "Google Workspace"]
MODULOS = ["oficios-recibidos", "oficios-realizados", "notas", "cuentas",
           "suministro-toners-hojas", "historico-reubicaciones", "licenciamientos"]


def cell_for(col, i):
    """Valor sintético según el nombre de columna."""
    c = col.lower()
    if c == "id":
        return str(i + 1)
    if c in ("monto",):
        return f"{rng.randint(500, 5000) + rng.random():.2f}"
    if c in ("cantidad", "cantidad_disponible"):
        return str(rng.randint(1, 20))
    if c in ("contador_total", "pdf_tamano", "extension"):
        return str(rng.randint(1000, 99999))
    if c in ("numero_empleado", "numero_plaza", "numero_tarjeta", "consecutivo_asignado",
             "glpi_id", "source_id"):
        return str(rng.randint(100, 99999))
    if c in ("timeout_seconds", "check_interval_seconds", "failure_threshold",
             "success_threshold", "consecutive_failures", "consecutive_successes",
             "last_latency_ms", "expected_status"):
        return str(rng.randint(1, 300))
    if c in ("dias_transcurridos", "asignacion_anterior_id", "baja_autorizada_por_id",
             "quien_entrega_id", "resuelto_por_id", "actualizado_por_id",
             "creado_por_id", "importado_por_id", "registrado_por_id",
             "elaborado_por_id", "elaboro_id", "atendido_por_id", "usuario_id",
             "personal_ti_id", "personal_hospital_id", "responsable_personal_ti_id",
             "tecnico_personal_ti_id", "quien_recibe_personal_ti_id",
             "quien_recibe_personal_hospital_id", "quien_recibe_personal_ti_id",
             "registrado_por_id", "aplicativo_id", "perfil_id", "puesto_id",
             "modelo_marca_id", "coordinacion_id", "departamento_id",
             "coordinacion_origen_id", "coordinacion_destino_id", "piso_anterior_id",
             "piso_nuevo_id", "piso_id", "panel_id", "idf_id", "tipo_panel_id",
             "puerta_id", "control_acceso_tarjeta_id", "site_id", "grupo_id",
             "incidencia_id", "entrega_id", "ingreso_id",
             "vacaciones_incidencia_id", "persona_id", "monitor_sites_id"):
        return str(rng.randint(1, 8))
    if c.startswith("fecha") or c.startswith("periodo") or c in ("fecha",):
        return rand_date()
    if c in ("ultimo_acceso", "last_checked_at", "last_status_change_at", "read_at",
             "resuelto_at", "ultima_importacion_at", "pdf_subido_at",
             "fecha_hora_movimiento", "fecha_hora_reubicacion", "timestamp"):
        return rand_ts()
    if c.endswith("_at"):
        return rand_ts()
    if c.startswith("hora"):
        return f"{rng.randint(7,18):02d}:{rng.randint(0,59):02d}:00"
    if c == "activo" or c.startswith("puede_") or c == "permitido":
        return "true" if rng.random() < 0.85 else "false"
    if c in ("entregado", "cancelado", "contestado", "notificacion",
             "es_cuenta_generica", "se_da_negativa", "requiere_atencion_proveedor"):
        return "true" if rng.random() < 0.3 else "false"
    if c == "nombre":
        return f"Registro de ejemplo {i + 1}"
    if c == "descripcion" or c == "observaciones" or c == "observacion" or c == "nota":
        return "Dato de muestra sintético (no es información real)."
    if c == "correo":
        return f"usuario.ejemplo{i + 1}@ejemplo.gob.mx"
    if c == "username" or c == "username_asignado":
        return f"usuario.ejemplo{i + 1}"
    if c == "password_hash" or c == "password_asignado_cifrado" or c == "devolucion_qr_token_hash":
        return "hash-sintetico-no-real"
    if c == "rol":
        return "TECNICO" if i % 3 else "COORDINADOR"
    if c == "nombre_completo" or c == "nombre_remitente" or c == "quien_recibe_nombre" \
            or c == "tecnico_nombre" or c == "responsable_nombre" or c == "firmante_nombre" \
            or c == "responsable_reporte":
        return f"Persona Ejemplo {i + 1:02d}"
    if c in ("apellidos", "nombres"):
        return f"Ejemplo {i + 1:02d}"
    if c == "numero_empleado":
        return str(10000 + i)
    if c == "nombre_coordinador":
        return COORD_RESPONSABLES[i % len(COORD_RESPONSABLES)]
    if c == "coordinacion_nombre" or c == "coordinacion_nombre_snapshot" \
            or c == "area_departamento" or c == "area" or c == "departamento" \
            or c == "coordinacion_origen_nombre" or c == "coordinacion_destino_nombre" \
            or c == "area_responsable":
        return COORD_NOMBRES[rng.randint(0, len(COORD_NOMBRES) - 1)]
    if c == "aplicativo_nombre" or c == "ap":
        return APLICATIVOS[i % len(APLICATIVOS)]
    if c == "modulo":
        return MODULOS[i % len(MODULOS)]
    if c == "estatus" or c == "estado_aprobacion" or c == "estatus_responsiva" \
            or c == "current_status" or c == "resultado_estatus":
        return "Entregado" if rng.random() < 0.6 else "Pendiente"
    if c == "tipo_suministro":
        return "toner" if rng.random() < 0.6 else "papel"
    if c == "tipo_equipo":
        return ["COMPUTO", "IMPRESION", "TELEFONIA"][i % 3]
    if c == "tipo":
        return "vacaciones" if rng.random() < 0.7 else "incidencia"
    if c == "accion":
        return ["CREAR", "ACTUALIZAR", "ELIMINAR"][i % 3]
    if c == "tabla_objetivo":
        return ["oficios_recibidos", "cuentas_usuario", "entregas_suministro"][i % 3]
    if c == "numero_oficio" or c == "numero_ticket_oficio" or c == "numero_ticket_servicio" \
            or c == "numero_contrato" or c == "folio_ticket":
        return f"EJ-{2026:04d}-{i + 1:04d}"
    if c == "numero_atencion_interna":
        return f"INT-{i + 1:04d}"
    if c == "identificador_equipo" or c == "numero_serie_impresora" or c == "hostname":
        return f"EQ-DEMO-{i + 1:04d}"
    if c == "modelo_marca_nombre":
        return "Marca de ejemplo"
    if c == "ip":
        return "192.168.0.100"
    if c == "user_agent":
        return "Mozilla/5.0 (demo)"
    if c == "url":
        return "https://ejemplo.gob.mx"
    if c == "method":
        return "GET"
    if c == "event_type":
        return ["UP", "DOWN", "RECOVERED"][i % 3]
    if c == "title":
        return "Notificación de ejemplo"
    if c == "detail" or c == "last_error_message" or c == "justificacion_declinado" \
            or c == "descripcion" or c == "registro_etiqueta":
        return "Texto sintético de ejemplo."
    if c == "asunto":
        return "Asunto de ejemplo para el registro de muestra"
    if c == "dirigido_a" or c == "ubicacion" or c == "ubicacion_anterior" \
            or c == "nueva_ubicacion" or c == "lugar_elaboracion" or c == "piso" \
            or c == "puertas_involucradas" or c == "puertas" or c == "turno" \
            or c == "jornada" or c == "status_laboral" or c == "servicio" \
            or c == "puesto" or c == "denominacion" or c == "nombre_perfil" \
            or c == "tipo_incidencia" or c == "plantilla_version" \
            or c == "piso_anterior_nombre" or c == "piso_nuevo_nombre" \
            or c == "puerta_nombre_snapshot" or c == "panel_nombre_snapshot" \
            or c == "idf_nombre_snapshot" or c == "piso_nombre_snapshot" \
            or c == "observaciones_proveedor" or c == "observaciones_proveedor_snapshot" \
            or c == "incidencia_snapshot" or c == "fuente_fila" \
            or c == "cargo_responsable" or c == "firmante_cargo_area" \
            or c == "turno_jornada" or c == "objetivo" or c == "actividad_realizada" \
            or c == "equipo_sistema_servicio" or c == "causa" \
            or c == "atencion_proporcionada" or c == "afectacion" \
            or c == "mantenimiento_acciones_preventivas" or c == "resultados" \
            or c == "pendientes_seguimiento" or c == "conclusion" \
            or c == "observaciones_actividad" or c == "datos_antes" \
            or c == "datos_despues" or c == "campos_modificados" or c == "metadata" \
            or c == "dias_laborales" or c == "tamano" or c == "mes" \
            or c == "pdf_nombre_original" or c == "pdf_nombre_archivo" \
            or c == "pdf_ruta" or c == "pdf_mime" or c == "avatar_url" \
            or c == "oficio_correspondiente":
        return "dato-sintetico"
    if c == "pdf_tamano":
        return str(rng.randint(1000, 50000))
    return "dato-sintetico"


def build_rows(table, n):
    cols = SCHEMA[table].split(",")
    rows = []
    for i in range(n):
        rows.append([cell_for(c, i) for c in cols])
    return cols, rows


def write_csv(table):
    cols, rows = build_rows(table, ROW_COUNTS.get(table, 1))
    path = os.path.join(OUT_DIR, table + ".csv")
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for row in rows:
            # escapa comas/comillas por si un valor las contuviera
            cells = []
            for v in row:
                if "," in v or '"' in v or "\n" in v:
                    v = '"' + v.replace('"', '""') + '"'
                cells.append(v)
            f.write(",".join(cells) + "\n")
    return len(rows)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tables = []
    for table in SCHEMA:
        n = write_csv(table)
        tables.append({"table": table, "file": table + ".csv",
                       "rows": n, "columns": len(SCHEMA[table].split(","))})

    manifest = {
        "database": "hraelocal1-demo",
        "exportedAt": "2026-09-07T19:58:04.805Z",
        "tableCount": len(tables),
        "note": "Datos SINTÉTICOS de ejemplo (no son información real del hospital). "
                "Sustituir por la exportación CSV real del SGTI para datos reales.",
        "tables": tables,
    }
    with open(os.path.join(OUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Generadas {len(tables)} tablas sintéticas en {OUT_DIR}")
    print("Nota: son datos de ejemplo; para datos reales usar refresh_all.py (ver README.md).")


if __name__ == "__main__":
    main()
