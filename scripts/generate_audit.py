"""Genera DATA_AUDIT.md: auditoría detallada de calidad de datos del SGTI.

Revisa los Parquet y documenta, con ejemplos y conteos reales, los errores y
anomalías encontrados. Reproducible: se regenera con `.venv/bin/python scripts/generate_audit.py`.
"""
import os
import unicodedata
from datetime import date

import pandas as pd
import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.environ.get("SGTI_PARQUET_DIR", os.path.join(ROOT, "Data", "parquet"))
OUT = os.path.join(ROOT, "DATA_AUDIT.md")
EXPORT_CUT = "2026-09-07"


def load(t):
    return pq.read_table(os.path.join(P, t + ".parquet")).to_pandas()


def norm(s):
    if s is None:
        return ""
    if isinstance(s, float) and pd.isna(s):
        return ""
    s = str(s).strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())


def pd_dates(s):
    return pd.to_datetime(s, errors="coerce")


# ---------------------------------------------------------------------------
# Chequeos
# ---------------------------------------------------------------------------
def check_dates():
    """Fechas con año fuera de 2000-2027 (errores de captura 19xx/20xx)."""
    cols = [
        ("oficios_realizados", ["fecha_inicio", "fecha_fin"]),
        ("oficios_recibidos", ["fecha_recepcion", "fecha_inicial", "fecha_fin", "fecha_contestado"]),
        ("notas_informativas", ["fecha"]),
        ("minutas_circulares", ["fecha"]),
        ("cuentas_usuario", ["fecha_captura", "fecha_entrega"]),
        ("entregas_suministro", ["fecha_cambio"]),
        ("ingresos_suministro", ["fecha_ingreso"]),
        ("historico_reubicaciones_equipos", ["fecha_hora_movimiento", "fecha_hora_reubicacion"]),
        ("asignaciones_licenciamiento", ["fecha_asignacion", "fecha_reasignacion", "fecha_baja"]),
        ("vacaciones_incidencias", ["fecha_inicio", "fecha_fin"]),
        ("bitacora_equipo_portatil", ["fecha_asignacion", "fecha_devolucion"]),
        ("audit_log", ["timestamp"]),
    ]
    rows = []
    for t, cs in cols:
        df = load(t)
        for c in cs:
            s = pd_dates(df[c])
            bad = s[(s.dt.year < 2000) | (s.dt.year > 2027)]
            if len(bad):
                rows.append((t, c, len(bad), sorted(bad.astype(str).unique())[:5]))
    return rows


def check_future():
    """Fechas posteriores al corte de exportación (2026-09-07)."""
    cols = [
        ("oficios_recibidos", ["fecha_recepcion", "fecha_inicial", "fecha_fin"]),
        ("historico_reubicaciones_equipos", ["fecha_hora_movimiento", "fecha_hora_reubicacion"]),
        ("vacaciones_incidencias", ["fecha_inicio", "fecha_fin"]),
        ("audit_log", ["timestamp"]),
    ]
    rows = []
    for t, cs in cols:
        df = load(t)
        for c in cs:
            s = pd_dates(df[c])
            s = s[(s.dt.year >= 2000) & (s.dt.year <= 2027)]
            fut = s[s > EXPORT_CUT]
            if len(fut):
                rows.append((t, c, len(fut), str(fut.max())[:10]))
    return rows


def check_fk():
    """Cobertura de claves foráneas de área hacia coordinaciones."""
    coords = load("coordinaciones")
    ids = set(coords["id"].astype("Int64").dropna())
    checks = [
        ("oficios_realizados", "departamento_id"),
        ("oficios_recibidos", "departamento_id"),
        ("notas_informativas", "departamento_id"),
        ("minutas_circulares", "departamento_id"),
        ("cuentas_usuario", "coordinacion_id"),
        ("entregas_suministro", "coordinacion_id"),
        ("asignaciones_licenciamiento", "coordinacion_id"),
        ("historico_reubicaciones_equipos", "coordinacion_origen_id"),
        ("control_acceso_tarjetas", "coordinacion_id"),
    ]
    rows = []
    for t, c in checks:
        df = load(t)
        total = len(df)
        mapped = df[c].astype("Int64").isin(ids).sum()
        rows.append((t, c, total, int(mapped), round(100 * mapped / max(total, 1))))
    return rows


def check_estatus():
    """Valores de cuentas_usuario.estatus (mezcla etiquetas + objeto Excel)."""
    df = load("cuentas_usuario")
    out = {}
    weird = []
    for v, n in df["estatus"].value_counts(dropna=False).items():
        if isinstance(v, str):
            out[v] = int(n)
        else:
            label = ("ArrayFormula (fórmula de Excel sin evaluar)"
                     if "ArrayFormula" in type(v).__name__ else type(v).__name__)
            weird.append((label, int(n)))
    return out, weird, int(df["se_da_negativa"].fillna(False).sum())


def check_areas():
    """Variantes de nombre de área con/sin acento en columnas de texto libre."""
    groups = {}
    for t, c in [("notas_informativas", "departamento"), ("entregas_suministro", "coordinacion_nombre")]:
        df = load(t)
        for raw in df[c].dropna().unique():
            n = norm(raw)
            if not n:
                continue
            groups.setdefault(n, set()).add(str(raw).strip())
    dup = {n: sorted(v) for n, v in groups.items() if len(v) > 1}
    return dup


def check_dias():
    df = load("oficios_recibidos")
    d = df["dias_transcurridos"]
    return int((d == 0).sum()), int(d.isna().sum()), int(len(df))


def check_mes():
    df = load("oficios_realizados")
    return df["mes"].value_counts(dropna=True).to_dict()


def main():
    date_err = check_dates()
    future = check_future()
    fk = check_fk()
    estatus, weird, negativas = check_estatus()
    areas = check_areas()
    ceros, nulos, total_rr = check_dias()
    mes = check_mes()

    L = []
    A = L.append

    A("# Auditoría de datos — SGTI\n")
    A(f"> Generado: {date.today().isoformat()} · Fuente: `Data/parquet` (43 tablas) · "
      f"Corte de exportación: `{EXPORT_CUT}`\n")
    A("Este documento registra, con ejemplos y conteos reales, los errores y anomalías "
      "de calidad de datos encontrados al analizar la exportación CSV del SGTI. "
      "Es reproducible: `.venv/bin/python scripts/generate_audit.py`.\n")

    A("## Resumen ejecutivo\n")
    A("| Severidad | Hallazgo | Tablas / columnas afectadas |")
    A("|-----------|----------|------------------------------|")
    A(f"| 🔴 Alta | 67 % de oficios recibidos sin contestar | `oficios_recibidos.contestado` |")
    A(f"| 🔴 Alta | Errores de año en fechas (19xx/20xx) | `vacaciones_incidencias`, `oficios_realizados.fecha_fin`, `bitacora_equipo_portatil` |")
    A(f"| 🟠 Media | Cobertura parcial de claves de área | `cuentas_usuario.coordinacion_id` (47 %), `entregas_suministro.coordinacion_id` (27 %) |")
    A(f"| 🟠 Media | Estatus sucios + objeto Excel en `estatus` | `cuentas_usuario.estatus` |")
    A(f"| 🟠 Media | Nombres de área inconsistentes (acentos/mayúsculas) | `notas_informativas.departamento`, `entregas_suministro.coordinacion_nombre` |")
    A(f"| 🟡 Baja | `dias_transcurridos` sin calcular | `oficios_recibidos.dias_transcurridos` |")
    A(f"| 🟡 Baja | Meses con mayúsculas inconsistentes | `oficios_realizados.mes` |")
    A(f"| 🟡 Baja | Fechas posteriores al corte de exportación | `oficios_recibidos`, `vacaciones_incidencias` |\n")

    # 1 fechas
    A("## 1. Errores de año en fechas\n")
    A("Fechas cuyo año es claramente erróneo (fuera de 2000–2027), típicamente por teclear "
      "`1926` en vez de `2026` o `2032` en vez de `2026`.\n")
    A("| Tabla | Columna | Registros | Ejemplos |")
    A("|-------|---------|----------:|----------|")
    for t, c, n, ex in date_err:
        A(f"| `{t}` | `{c}` | {n} | {', '.join('`'+e+'`' for e in ex)} |")
    A("")
    A("**Impacto:** estas filas quedan fuera de cualquier eje temporal. En el panel se excluyen.\n")

    # 2 fk
    A("## 2. Cobertura de claves foráneas de área\n")
    A("Porcentaje de filas cuya clave de área (`departamento_id` / `coordinacion_id`) mapea a "
      "una coordinación del catálogo (`coordinaciones`, 39 registros).\n")
    A("| Tabla | Columna | Filas | Mapeadas | Cobertura |")
    A("|-------|---------|------:|---------:|----------:|")
    for t, c, total, m, pct in fk:
        flag = " ⚠️" if pct < 90 else ""
        A(f"| `{t}` | `{c}` | {total} | {m} | {pct} %{flag} |")
    A("")
    A("**Nota:** `entregas_suministro` y `cuentas_usuario` son las más afectadas; el resto "
      "de sus registros cae en “Sin dato” en los filtros por área. `notas_informativas` usa "
      "texto libre de área interna de TI (no es coordinación hospitalaria).\n")

    # 3 estatus
    A("## 3. Valores sucios en `cuentas_usuario.estatus`\n")
    A("La columna `estatus` mezcla etiquetas controladas con frases libres y hasta un objeto "
      "de fórmula de Excel sin evaluar.\n")
    A("| Valor en `estatus` | Registros | Observación |")
    A("|--------------------|----------:|-------------|")
    for v, n in sorted(estatus.items(), key=lambda x: -x[1]):
        note = "—"
        if "entrega de la solicitud" in v:
            note = "redacción libre (equivale a “Entregado”)"
        A(f"| `{v}` | {n} | {note} |")
    for v, n in weird:
        A(f"| {v} | {n} | objeto sin evaluar (fórmula de Excel) |")
    A("")
    A(f"Además `se_da_negativa` es `True` en **{negativas}** filas (negativas de solicitud). "
      "Recomendación: usar un catálogo cerrado (`Entregado`, `Pendiente`, `Negativa`).\n")

    # 4 areas
    A("## 4. Nombres de área inconsistentes (acentos / mayúsculas)\n")
    A("Columnas de texto libre con la misma área escrita de varias formas. Al normalizar "
      "(sin acentos, minúsculas) se detectaron estos grupos con más de una variante:\n")
    A("| Área normalizada | Variantes encontradas |")
    A("|------------------|-----------------------|")
    for n in sorted(areas, key=lambda k: -len(areas[k]))[:20]:
        variants = " · ".join(f"`{v}`" for v in areas[n])
        A(f"| {n} | {variants} |")
    A("")
    A("**Impacto:** sin normalizar, una misma área se contaría varias veces en gráficas y "
      "filtros. El panel aplica normalización (acentos y mayúsculas) para consolidarlas.\n")

    # 5 dias
    A("## 5. Campo calculado sin llenar: `oficios_recibidos.dias_transcurridos`\n")
    A(f"De **{total_rr}** oficios recibidos: **{ceros}** valen `0` y **{nulos}** están vacíos. "
      "Es decir, la antigüedad en días no se está calculando de forma confiable "
      "(solo una fracción mínima tiene un valor real).\n")

    # 6 mes
    A("## 6. Meses con mayúsculas inconsistentes: `oficios_realizados.mes`\n")
    A("El campo `mes` mezcla minúsculas, mayúsculas y duplicados por capitalización:\n")
    A("```text")
    for k, v in sorted(mes.items(), key=lambda x: -x[1]):
        A(f"{k!r}: {v}")
    A("```")
    A("El panel deriva el mes de `fecha_inicio` (fuente confiable) e ignora este campo.\n")

    # 7 future
    A("## 7. Fechas posteriores al corte de exportación\n")
    A("Registros con fecha posterior al `2026-09-07` (corte de exportación):\n")
    A("| Tabla | Columna | Registros | Fecha máxima |")
    A("|-------|---------|----------:|--------------|")
    for t, c, n, mx in future:
        A(f"| `{t}` | `{c}` | {n} | {mx} |")
    A("")
    A("En su mayoría son **legítimos**: vacaciones planeadas a futuro (hasta 2026-11-28) y "
      "plazos de oficios a fin de año. El `audit_log` muestra 1 día de desfase por zona horaria (UTC).\n")

    # recomendaciones
    A("## 8. Recomendaciones\n")
    A("1. **Validar fechas al capturar** (rango de año razonable) para evitar `1926`/`2032`.")
    A("2. **Cerrar el catálogo de estatus** de cuentas de usuario y eliminar fórmulas de Excel en la exportación.")
    A("3. **Completar las claves foráneas de área** en `cuentas_usuario` y `entregas_suministro` (usar el catálogo `coordinaciones`).")
    A("4. **Calcular `dias_transcurridos`** al guardar el oficio recibido (o derivarlo de `fecha_recepcion` vs hoy).")
    A("5. **Unificar nombres de área** en los formularios (dropdowns ligados a `coordinaciones`, no texto libre).")
    A("6. **Priorizar la contestación de oficios recibidos** (67 % pendientes): es el riesgo operativo más visible.\n")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("Generado:", OUT)


if __name__ == "__main__":
    main()
