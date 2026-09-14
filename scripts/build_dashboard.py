"""Genera dashboard/index.html con datos embebidos desde los Parquet normalizados.

Lee Data/parquet, arma datasets compactos (fecha, area, estado/tipo) mas columnas
de detalle para las tablas de drill-down, y los inyecta en
scripts/dashboard_template.html reemplazando el placeholder __DATA_JSON__.
"""
import json
import os
import unicodedata

import pandas as pd
import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.environ.get("SGTI_PARQUET_DIR", os.path.join(ROOT, "Data", "parquet"))
TEMPLATE = os.path.join(ROOT, "scripts", "dashboard_template.html")
OUT = os.path.join(ROOT, "dashboard", "index.html")


def load(t):
    return pq.read_table(os.path.join(P, t + ".parquet")).to_pandas()


# ---------------------------------------------------------------------------
# Normalizacion de texto libre (acentos, mayusculas, espacios)
# ---------------------------------------------------------------------------
def norm(s):
    if s is None:
        return ""
    if isinstance(s, float) and pd.isna(s):
        return ""
    s = str(s).strip()
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower()
    return " ".join(s.split())


ACCENTS = {
    "informatica": "Informática", "informatico": "Informático",
    "enfermeria": "Enfermería", "estadisticas": "Estadísticas",
    "ensenanza": "Enseñanza", "medicas": "Médicas", "medica": "Médica",
    "medico": "Médico", "investigacion": "Investigación",
    "direccion": "Dirección", "subdireccion": "Subdirección",
    "coordinacion": "Coordinación", "coordinaciones": "Coordinaciones",
    "tecnico": "Técnico", "tecnica": "Técnica", "planeacion": "Planeación",
    "cirugia": "Cirugía", "pediatria": "Pediatría", "gineco": "Gineco",
    "obstetricia": "Obstetricia", "cardiologia": "Cardiología",
    "critica": "Crítica", "gestion": "Gestión", "calidad": "Calidad",
    "telecomunicaciones": "Telecomunicaciones", "asistencia": "Asistencia",
    "aux": "Aux.", "diag": "Diag.", "tratamiento": "Tratamiento",
    "laboratorio": "Laboratorio", "archivo": "Archivo", "apoyo": "Apoyo",
    "administrativo": "Administrativo", "administrativa": "Administrativa",
    "soporte": "Soporte", "desarrollo": "Desarrollo", "redes": "Redes",
    "seguridad": "Seguridad", "analista": "Analista", "asistente": "Asistente",
    "manager": "Manager", "otro": "Otro", "otros": "Otros",
}
LOW = {"de", "del", "la", "las", "los", "el", "y", "e", "en", "para", "a", "o", "u"}


def title_es(n):
    parts = n.replace("-", " - ").split()
    out = []
    for i, p in enumerate(parts):
        if p == "-":
            out.append("-")
            continue
        if p in ACCENTS:
            w = ACCENTS[p]
        else:
            w = p.capitalize()
        if i > 0 and p in LOW:
            w = p
        out.append(w)
    s = " ".join(out)
    s = s.replace(" - ", "-")
    return s


ALIAS = {
    "soporte tecnico": "Soporte Técnico",
    "coordinador de informatica": "Coordinación de Informática",
    "coordinacion de informatica": "Coordinación de Informática",
    "informatica": "Informática",
    "asistente de la coordinacion de informatica": "Asistente de Informática",
    "analista ti": "Analista TI",
    "manager it": "Manager IT",
}


def clean_name(raw):
    n = norm(raw)
    if not n:
        return "Sin dato"
    return ALIAS.get(n, title_es(n))


def txt(x):
    if x is None:
        return ""
    if isinstance(x, float) and pd.isna(x):
        return ""
    return str(x).strip()


def dstr(s):
    if s is None:
        return ""
    try:
        ts = pd.to_datetime(s, errors="coerce")
    except Exception:
        return ""
    if pd.isna(ts):
        return ""
    try:
        # descarta fechas con año claramente erróneo (errores de captura 19xx/20xx)
        if ts.year < 2000 or ts.year > 2027:
            return ""
        return ts.strftime("%Y-%m-%d")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Dimensiones
# ---------------------------------------------------------------------------
coords = load("coordinaciones")
cmap = dict(zip(coords["id"].astype("Int64"), coords["nombre"]))

pti = load("personal_ti")
pmap = dict(zip(pti["id"].astype("Int64"), pti["nombre"]))


def coord_name(fk):
    if fk is None or (isinstance(fk, float) and pd.isna(fk)):
        return "Sin dato"
    try:
        v = int(fk)
    except (TypeError, ValueError):
        return "Sin dato"
    return cmap.get(v, "Sin dato")


def persona(pid):
    if pid is None or (isinstance(pid, float) and pd.isna(pid)):
        return ""
    try:
        v = int(pid)
    except (TypeError, ValueError):
        return ""
    return txt(pmap.get(v, ""))


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------
def build_or():
    df = load("oficios_realizados")
    out = []
    for r in df.itertuples(index=False):
        ent, canc = bool(r.entregado), bool(r.cancelado)
        st = "Cancelado" if canc else ("Entregado" if ent else "Sin entregar")
        out.append({"fecha": dstr(r.fecha_inicio), "area": coord_name(r.departamento_id),
                    "estado": st, "numero": txt(r.numero_oficio), "asunto": txt(r.asunto)})
    return out


def build_rr():
    df = load("oficios_recibidos")
    out = []
    for r in df.itertuples(index=False):
        st = "Contestado" if bool(r.contestado) else "Pendiente"
        out.append({"fecha": dstr(r.fecha_recepcion), "area": coord_name(r.departamento_id),
                    "estado": st, "numero": txt(r.numero_oficio),
                    "remitente": txt(r.nombre_remitente), "asunto": txt(r.asunto)})
    return out


def build_nt():
    df = load("notas_informativas")
    out = []
    for r in df.itertuples(index=False):
        out.append({"fecha": dstr(r.fecha), "area": clean_name(r.departamento),
                    "asunto": txt(r.asunto), "autor": persona(r.elaboro_id)})
    return out


def build_cu():
    df = load("cuentas_usuario")
    out = []
    for r in df.itertuples(index=False):
        raw = norm(r.estatus)
        neg = bool(r.se_da_negativa)
        if neg or "negativa" in raw:
            st = "Negativa"
        elif "entreg" in raw:
            st = "Entregada"
        elif "pendiente" in raw:
            st = "Pendiente"
        else:
            st = "Otro"
        out.append({"fecha": dstr(r.fecha_captura), "area": coord_name(r.coordinacion_id),
                    "estado": st, "persona": txt(r.nombre_completo),
                    "username": txt(r.username_asignado)})
    return out


def build_en():
    df = load("entregas_suministro")
    out = []
    for r in df.itertuples(index=False):
        t = "Tóner" if norm(r.tipo_suministro) == "toner" else "Papel"
        out.append({"fecha": dstr(r.fecha_cambio), "area": clean_name(r.coordinacion_nombre),
                    "tipo": t, "cantidad": int(r.cantidad) if pd.notna(r.cantidad) else 0,
                    "marca": txt(r.modelo_marca_nombre)})
    return out


def build_in():
    df = load("ingresos_suministro")
    out = []
    for r in df.itertuples(index=False):
        t = "Tóner" if norm(r.tipo_suministro) == "toner" else "Papel"
        monto = float(r.monto) if pd.notna(r.monto) else 0.0
        out.append({"fecha": dstr(r.fecha_ingreso), "tipo": t,
                    "cantidad": int(r.cantidad) if pd.notna(r.cantidad) else 0,
                    "monto": monto, "contrato": txt(r.numero_contrato)})
    return out


def build_re():
    df = load("historico_reubicaciones_equipos")
    tipo_map = {"COMPUTO": "Cómputo", "IMPRESION": "Impresión", "TELEFONIA": "Telefonía"}
    out = []
    for r in df.itertuples(index=False):
        t = tipo_map.get(norm(r.tipo_equipo).upper(), norm(r.tipo_equipo).upper() or "Otro")
        out.append({"fecha": dstr(r.fecha_hora_movimiento), "area": coord_name(r.coordinacion_destino_id),
                    "tipo": t, "equipo": txt(r.identificador_equipo),
                    "origen": txt(r.coordinacion_origen_nombre)})
    return out


def build_li():
    df = load("asignaciones_licenciamiento")
    out = []
    for r in df.itertuples(index=False):
        out.append({"fecha": dstr(r.fecha_asignacion), "area": coord_name(r.coordinacion_id),
                    "ap": txt(r.aplicativo_nombre) or "Sin dato", "hostname": txt(r.hostname),
                    "persona": txt(r.nombre_completo)})
    return out


def build_va():
    df = load("vacaciones_incidencias")
    out = []
    for r in df.itertuples(index=False):
        t = "Vacaciones" if norm(r.tipo) == "vacaciones" else "Incidencia"
        s = {"APROBADA": "Aprobada", "PENDIENTE": "Pendiente"}.get(
            norm(r.estado_aprobacion).upper(), title_es(norm(r.estado_aprobacion)) or "Otro")
        out.append({"fecha": dstr(r.fecha_inicio), "tipo": t, "estado": s,
                    "persona": persona(r.personal_ti_id)})
    return out


def build_au():
    df = load("audit_log")
    out = []
    for r in df.itertuples(index=False):
        out.append({"fecha": dstr(r.timestamp), "accion": txt(r.accion) or "Otro",
                    "modulo": txt(r.modulo) or "Otro"})
    return out


def main():
    data = {
        "oficiosRealizados": build_or(),
        "oficiosRecibidos": build_rr(),
        "notas": build_nt(),
        "cuentas": build_cu(),
        "entregas": build_en(),
        "ingresos": build_in(),
        "reubicaciones": build_re(),
        "licencias": build_li(),
        "vacaciones": build_va(),
        "audit": build_au(),
    }

    all_dates = []
    for rows in data.values():
        for r in rows:
            if r.get("fecha"):
                all_dates.append(r["fecha"])
    all_dates.sort()
    min_date = all_dates[0] if all_dates else "2026-01-01"
    max_date = all_dates[-1] if all_dates else "2026-12-31"

    payload = {"meta": {"minDate": min_date, "maxDate": max_date, "export": "2026-09-07"},
               "data": data}

    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()

    js = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("__DATA_JSON__", js)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print("Generado:", OUT)
    print("Rango fechas:", min_date, "->", max_date)
    for k, v in data.items():
        print(f"  {k}: {len(v)}")


if __name__ == "__main__":
    main()
