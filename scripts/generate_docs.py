"""Generate DATA_DICTIONARY.md from the Parquet schemas + manifest.

Usage:
    python scripts/generate_docs.py [--parquet-dir DIR] [--out DATA_DICTIONARY.md]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

# Friendly business-name mapping for the dictionary, table -> (domain, description).
TABLE_INFO = {
    "aplicativos_licencia": ("Catálogo", "Software licensed (Office, Adobe, Creative Cloud, etc.)."),
    "asignaciones_licenciamiento": ("Fact", "License assignments to personnel (hostname, GLPI id, status)."),
    "audit_log": ("Fact", "Audit trail of every create/update/delete across the system."),
    "bitacora_equipo_portatil": ("Fact", "Loan log for portable/laptop equipment."),
    "bitacora_omision_reportes": ("Fact", "Missed daily activity reports by IT staff."),
    "catalogo_suministros": ("Catálogo", "Supply catalog (toners, paper and models/brands)."),
    "control_acceso_idfs": ("Catálogo", "IDF (Intermediate Distribution Frame) catalog."),
    "control_acceso_paneles": ("Catálogo", "Access-control panels catalog."),
    "control_acceso_pisos": ("Catálogo", "Floors used by access control."),
    "control_acceso_puertas": ("Catálogo", "Door catalog (one per access point)."),
    "control_acceso_tarjeta_puertas": ("Bridge", "N:N mapping cards <-> doors."),
    "control_acceso_tarjetas": ("Fact", "Physical access cards and their responsivas."),
    "control_acceso_tipos_panel": ("Catálogo", "Panel types for access control."),
    "coordinaciones": ("Catálogo", "Hospital coordinations/departments."),
    "cuentas_usuario": ("Fact", "User account requests (creation, delivery, negatives)."),
    "entregas_suministro": ("Fact", "Supply deliveries to coordinations (printer serials, counters)."),
    "entregas_suministro_consumos": ("Fact", "Per-delivery consumption of ingreso stock."),
    "grupo_permisos_detalle": ("Bridge", "Granular module permissions per permission group."),
    "grupos_permisos": ("Catálogo", "Permission groups catalog."),
    "historico_reubicaciones_equipos": ("Fact", "History of equipment relocations (computers, printers, phones)."),
    "incidencias_acceso_escalaciones": ("Fact", "Access-control incident escalations to providers."),
    "incidencias_acceso_notas_informativas": ("Fact", "Informative notes tied to access-control incidents."),
    "incidencias_control_acceso": ("Fact", "Access-control incidents."),
    "incidencias_control_acceso_puertas": ("Bridge", "N:N mapping incidents <-> doors."),
    "ingresos_suministro": ("Fact", "Supply intake/receipts with contract numbers."),
    "minutas_circulares": ("Fact", "Meeting minutes and circulars."),
    "monitor_notifications": ("Fact", "Uptime/downtime notifications from site health monitor."),
    "monitor_sites": ("Catálogo", "Monitored systems (SITAU, SIPAC, SIMEF)."),
    "notas_informativas": ("Fact", "Informative notes / daily activity reports."),
    "oficios_realizados": ("Fact", "Official documents sent out."),
    "oficios_recibidos": ("Fact", "Official documents received."),
    "perfiles_sistema": ("Catálogo", "System profiles (Admin, Coordinator, Technician, etc.)."),
    "personal_hospital": ("Catálogo", "Full hospital staff directory."),
    "personal_ti": ("Catálogo", "IT department personnel."),
    "pisos_reubicacion": ("Catálogo", "Floors used by equipment relocations."),
    "puestos_cargo": ("Catálogo", "Job position catalog."),
    "usuario_grupo": ("Bridge", "User -> permission group assignments."),
    "usuario_minutas_exclusiones": ("Bridge", "Users excluded from seeing specific minutes (empty)."),
    "usuario_modulos": ("Fact", "Granular module permissions per system user."),
    "usuario_notas_exclusiones": ("Bridge", "Users excluded from seeing specific notes."),
    "usuarios_sistema": ("Catálogo", "Application users (linked to personal_ti)."),
    "vacaciones_incidencias": ("Fact", "Vacation / incident requests with approval workflow."),
    "vacaciones_incidencias_fechas": ("Fact", "Specific dates covered by a vacation/incident request."),
}

RELATIONSHIPS = [
    # to_dimension_key, dimension_table, fact, from_column
    ("coordinaciones.id", "coordinaciones", "asignaciones_licenciamiento", "coordinacion_id"),
    ("aplicativos_licencia.id", "aplicativos_licencia", "asignaciones_licenciamiento", "aplicativo_id"),
    ("coordinaciones.id", "coordinaciones", "bitacora_equipo_portatil", "departamento_id"),
    ("personal_ti.id", "personal_ti", "bitacora_equipo_portatil", "personal_ti_id"),
    ("personal_hospital.numero_empleado", "personal_hospital", "bitacora_equipo_portatil", "numero_empleado"),
    ("personal_ti.id", "personal_ti", "bitacora_omision_reportes", "personal_ti_id"),
    ("coordinaciones.id", "coordinaciones", "control_acceso_tarjetas", "coordinacion_id"),
    ("personal_hospital.id", "personal_hospital", "control_acceso_tarjetas", "personal_hospital_id"),
    ("control_acceso_tarjetas.id", "control_acceso_tarjetas", "control_acceso_tarjeta_puertas", "control_acceso_tarjeta_id"),
    ("control_acceso_puertas.id", "control_acceso_puertas", "control_acceso_tarjeta_puertas", "puerta_id"),
    ("coordinaciones.id", "coordinaciones", "cuentas_usuario", "coordinacion_id"),
    ("puestos_cargo.id", "puestos_cargo", "cuentas_usuario", "puesto_id"),
    ("perfiles_sistema.id", "perfiles_sistema", "cuentas_usuario", "perfil_id"),
    ("coordinaciones.id", "coordinaciones", "entregas_suministro", "coordinacion_id"),
    ("personal_ti.id", "personal_ti", "entregas_suministro", "tecnico_personal_ti_id"),
    ("entregas_suministro.id", "entregas_suministro", "entregas_suministro_consumos", "entrega_id"),
    ("ingresos_suministro.id", "ingresos_suministro", "entregas_suministro_consumos", "ingreso_id"),
    ("grupos_permisos.id", "grupos_permisos", "grupo_permisos_detalle", "grupo_id"),
    ("coordinaciones.id", "coordinaciones", "historico_reubicaciones_equipos", "coordinacion_origen_id"),
    ("coordinaciones.id", "coordinaciones", "historico_reubicaciones_equipos", "coordinacion_destino_id"),
    ("pisos_reubicacion.id", "pisos_reubicacion", "historico_reubicaciones_equipos", "piso_anterior_id"),
    ("pisos_reubicacion.id", "pisos_reubicacion", "historico_reubicaciones_equipos", "piso_nuevo_id"),
    ("personal_ti.id", "personal_ti", "historico_reubicaciones_equipos", "responsable_personal_ti_id"),
    ("incidencias_control_acceso.id", "incidencias_control_acceso", "incidencias_acceso_escalaciones", "incidencia_id"),
    ("incidencias_control_acceso.id", "incidencias_control_acceso", "incidencias_acceso_notas_informativas", "incidencia_id"),
    ("control_acceso_paneles.id", "control_acceso_paneles", "incidencias_control_acceso", "panel_id"),
    ("control_acceso_idfs.id", "control_acceso_idfs", "incidencias_control_acceso", "idf_id"),
    ("control_acceso_pisos.id", "control_acceso_pisos", "incidencias_control_acceso", "piso_id"),
    ("incidencias_control_acceso.id", "incidencias_control_acceso", "incidencias_control_acceso_puertas", "incidencia_id"),
    ("control_acceso_puertas.id", "control_acceso_puertas", "incidencias_control_acceso_puertas", "puerta_id"),
    ("catalogo_suministros.id", "catalogo_suministros", "ingresos_suministro", "modelo_marca_id"),
    ("personal_ti.id", "personal_ti", "ingresos_suministro", "quien_recibe_personal_ti_id"),
    ("personal_ti.id", "personal_ti", "minutas_circulares", "elaboro_id"),
    ("coordinaciones.id", "coordinaciones", "minutas_circulares", "departamento_id"),
    ("monitor_sites.id", "monitor_sites", "monitor_notifications", "site_id"),
    ("personal_ti.id", "personal_ti", "notas_informativas", "elaboro_id"),
    ("coordinaciones.id", "coordinaciones", "notas_informativas", "departamento_id"),
    ("coordinaciones.id", "coordinaciones", "oficios_realizados", "departamento_id"),
    ("personal_ti.id", "personal_ti", "oficios_realizados", "elaborado_por_id"),
    ("coordinaciones.id", "coordinaciones", "oficios_recibidos", "departamento_id"),
    ("personal_ti.id", "personal_ti", "oficios_recibidos", "atendido_por_id"),
    ("usuarios_sistema.id", "usuarios_sistema", "usuario_grupo", "usuario_id"),
    ("grupos_permisos.id", "grupos_permisos", "usuario_grupo", "grupo_id"),
    ("usuarios_sistema.id", "usuarios_sistema", "usuario_modulos", "usuario_id"),
    ("usuarios_sistema.id", "usuarios_sistema", "usuario_notas_exclusiones", "usuario_id"),
    ("personal_hospital.id", "personal_hospital", "usuario_notas_exclusiones", "persona_id"),
    ("usuarios_sistema.id", "usuarios_sistema", "usuario_minutas_exclusiones", "usuario_id"),
    ("personal_hospital.id", "personal_hospital", "usuario_minutas_exclusiones", "persona_id"),
    ("personal_ti.id", "personal_ti", "usuarios_sistema", "personal_ti_id"),
    ("personal_ti.id", "personal_ti", "vacaciones_incidencias", "personal_ti_id"),
    ("usuarios_sistema.id", "usuarios_sistema", "vacaciones_incidencias", "registrado_por_id"),
    ("vacaciones_incidencias.id", "vacaciones_incidencias", "vacaciones_incidencias_fechas", "vacaciones_incidencia_id"),
    ("usuarios_sistema.id", "usuarios_sistema", "audit_log", "usuario_id"),
]


def arrow_to_human(field) -> str:
    t = field.type
    try:
        name = str(t)
    except Exception:
        name = type(t).__name__
    if t == "string":
        return "text"
    return name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet-dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("DATA_DICTIONARY.md"))
    args = parser.parse_args(argv)

    base = Path(__file__).resolve().parent.parent
    parquet_dir = args.parquet_dir or (base / "Data" / "parquet")
    candidates = sorted((base / "Data").glob("hraelocal1-*"))
    export_dir = next((p for p in candidates if p.is_dir()), base / "Data")
    manifest = json.loads((export_dir / "manifest.json").read_text(encoding="utf-8"))
    row_counts = {e["table"]: e["rows"] for e in manifest["tables"]}

    lines = [
        "# DATA_DICTIONARY.md",
        "",
        "Diccionario de datos del SGTI generado automaticamente desde los archivos Parquet.",
        "",
        f"- Carpeta origen: `Data/parquet/`",
        f"- Total de tablas: `{len(manifest['tables'])}`",
        "",
        "## 1. Tablas",
        "",
        "| Tabla | Dominio | Filas | Descripcion |",
        "|-------|---------|------:|-------------|",
    ]
    for entry in manifest["tables"]:
        table = entry["table"]
        domain, desc = TABLE_INFO.get(table, ("", ""))
        lines.append(f"| `{table}` | {domain} | {entry['rows']:,} | {desc} |")

    lines += [
        "",
        "## 2. Esquemas (columnas y tipos)",
        "",
    ]
    for entry in manifest["tables"]:
        table = entry["table"]
        schema = pq.read_schema(parquet_dir / f"{table}.parquet")
        lines.append(f"### `{table}` ({row_counts[table]:,} filas)")
        lines.append("")
        lines.append("| Columna | Tipo |")
        lines.append("|---------|------|")
        for field in schema:
            lines.append(f"| `{field.name}` | {arrow_to_human(field)} |")
        lines.append("")

    lines += [
        "## 3. Relaciones (modelo dimensional)",
        "",
        "Direccion: tabla de hechos -> tabla de dimension (1:N).",
        "",
        "| Dimension (lado 1) | Tabla de hechos/transaccion | Columna |",
        "|--------------------|-----------------------------|---------|",
    ]
    for dim, _dimension, fact, col in RELATIONSHIPS:
        lines.append(f"| `{dim}` | `{fact}` | `{col}` |")

    lines.append("")
    lines.append("## 4. Notas de tipo")
    lines.append("")
    lines.append("- `date32[day]`: fecha normalizada `YYYY-MM-DD`.")
    lines.append("- `timestamp[us, tz=UTC]`: fecha-hora en UTC (desplazame la zona en el modelo de Power BI).")
    lines.append("- `int64` nullable: ids y cantidades; sin `Int64` de numpy por compatibilidad.")
    lines.append("- Colores `bool`: banderas `activo`, `permitido`, `puede_*`, `entregado`, `contestado`, etc.")

    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())