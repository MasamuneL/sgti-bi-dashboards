"""Panel SGTI alternativo en Streamlit (lee Data/parquet en vivo) — v2.

Ejecutar:
    .venv/bin/streamlit run streamlit_dashboard_v2.py

Copia de streamlit_dashboard.py con dos features nuevas:
  1. Pestaña "Calidad de datos" (métricas de scripts/data_quality.py).
  2. Checkbox "Acumulado (YTD)" en el sidebar que convierte las series
     mensuales en suma corrida.

Reutiliza el cargador/normalizador de scripts/build_dashboard.py, así que las
reglas de limpieza (acentos, fechas erróneas, áreas consolidadas) son idénticas
a las del dashboard HTML.
"""
import os
import sys

import pandas as pd
import streamlit as st
import altair as alt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
import build_dashboard as bd  # noqa: E402
import data_quality as dq  # noqa: E402

st.set_page_config(page_title="SGTI — Panel de Gestión de TI", layout="wide",
                   page_icon="🏥", initial_sidebar_state="expanded")

CUSTOM_CSS = """
<style>
/* Tarjetas de métricas */
[data-testid="stMetric"] {
    border: 1px solid rgba(128, 140, 160, 0.22);
    border-top: 3px solid #2563eb;
    border-radius: 12px;
    padding: 14px 16px 12px;
}
[data-testid="stMetricLabel"] { font-size: 0.78rem; letter-spacing: .03em; }
[data-testid="stMetricValue"] { font-size: 1.9rem; }
/* Tarjetas de gráficas */
[data-testid="stVegaLiteChart"] {
    border: 1px solid rgba(128, 140, 160, 0.18);
    border-radius: 14px;
    padding: 8px;
}
/* Cabecera */
.sgti-header { border-left: 5px solid #2563eb; padding: 2px 0 2px 18px; margin-bottom: 8px; }
.sgti-header h1 { margin: 0 0 3px 0; font-size: 1.85rem; line-height: 1.15; }
.sgti-header .sgti-sub { color: rgba(128, 140, 160, 0.95); font-size: 0.9rem; }
.sgti-header .sgti-sub b { font-weight: 600; }
/* Marca en sidebar */
.sgti-brand { font-size: 1.05rem; font-weight: 700; }
.sgti-brand-sub { font-size: 0.78rem; opacity: .75; margin-bottom: 4px; }
/* DataFrames redondeados */
[data-testid="stDataFrame"] { border-radius: 12px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DARK_CSS = """
<style>
html, body, .stApp, [data-testid="stAppViewContainer"] { background: #0b1220 !important; }
[data-testid="stSidebar"] { background: #0f172a !important; }
[data-testid="stAppViewContainer"], [data-testid="stSidebar"] { color: #e2e8f0 !important; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
h1, h2, h3, h4, h5, h6 { color: #e2e8f0 !important; }
[data-testid="stCaptionContainer"], [data-testid="stMarkdownContainer"] { color: #cbd5e1 !important; }
[data-testid="stMetric"] { background: #141d2e !important; }
[data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] { color: #e2e8f0 !important; }
[data-testid="stDataFrame"] { background: #141d2e !important; }
[data-testid="stDataFrame"] * { color: #cbd5e1 !important; }
[data-testid="stTab"] { color: #cbd5e1 !important; }
[data-testid="stTab"][aria-selected="true"] { color: #3b82f6 !important; }
[data-testid="stMultiSelect"] *, [data-testid="stDateInput"] * { color: #cbd5e1 !important; }
</style>
"""

# ---------------------------------------------------------------------------
# Datos (mismos datasets que el HTML)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Cargando Data/parquet…")
def load_all():
    frames = {
        "or": pd.DataFrame(bd.build_or()),
        "rr": pd.DataFrame(bd.build_rr()),
        "nt": pd.DataFrame(bd.build_nt()),
        "cu": pd.DataFrame(bd.build_cu()),
        "en": pd.DataFrame(bd.build_en()),
        "ing": pd.DataFrame(bd.build_in()),
        "re": pd.DataFrame(bd.build_re()),
        "li": pd.DataFrame(bd.build_li()),
        "va": pd.DataFrame(bd.build_va()),
        "au": pd.DataFrame(bd.build_au()),
    }
    for k, df in frames.items():
        df["mes"] = df["fecha"].str[:7]
    return frames


DATA = load_all()
ALL_DATES = sorted({d for df in DATA.values() for d in df["fecha"] if d})
MIN_DATE = pd.to_datetime(ALL_DATES[0]).date()
MAX_DATE = pd.to_datetime(ALL_DATES[-1]).date()

C = {"green": "#16a34a", "amber": "#d97706", "red": "#dc2626", "gray": "#64748b",
     "blue": "#2563eb", "purple": "#7c3aed", "teal": "#0d9488", "pink": "#db2777"}
ESTADO_COLORES = {"Entregado": C["green"], "Contestado": C["green"], "Aprobada": C["green"],
                  "Entregada": C["green"], "Sin entregar": C["amber"], "Pendiente": C["amber"],
                  "Cancelado": C["red"], "Negativa": C["red"], "Otro": C["gray"]}
PALETTE = [C["blue"], C["green"], C["amber"], C["red"], C["purple"], C["teal"], C["pink"], C["gray"]]
TIPO_COLORES = {"Tóner": C["teal"], "Papel": C["purple"]}
MODULO_LABELS = {
    "oficios-recibidos": "Oficios recibidos",
    "oficios-realizados": "Oficios realizados",
    "notas": "Notas informativas",
    "suministro-toners-hojas": "Suministro (tóner/hojas)",
    "cuentas": "Cuentas de usuario",
    "historico-reubicaciones": "Reubicaciones de equipo",
    "vacaciones-incidencias": "Vacaciones / incidencias",
    "equipo-portatil": "Equipo portátil",
    "omision-reportes": "Omisión de reportes",
    "licenciamientos": "Licenciamientos",
    "minutas-circulares": "Minutas / circulares",
    "control-acceso": "Control de acceso",
}


def shorten(s, n=48):
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"


# ---------------------------------------------------------------------------
# Filtros globales
# ---------------------------------------------------------------------------
st.sidebar.markdown(
    '<div class="sgti-brand">SGTI — Panel de Gestión de TI</div>'
    '<div class="sgti-brand-sub">Hospital Regional de Alta Especialidad</div>',
    unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("Filtros")
dfrom, dto = st.sidebar.date_input(
    "Rango de fechas", value=(MIN_DATE, MAX_DATE), min_value=MIN_DATE, max_value=MAX_DATE)
if not isinstance(dfrom, tuple):
    dfrom, dto = dfrom, dto
FROM, TO = dfrom.strftime("%Y-%m-%d"), dto.strftime("%Y-%m-%d")
ACUM = st.sidebar.checkbox("Ver acumulado (YTD)", value=False)
DARK = st.sidebar.toggle("Modo oscuro", value=False)
_TXT = "#cbd5e1" if DARK else "#374151"
_GRID = "#2a3648" if DARK else "#eef0f3"
_BG = "#0b1220" if DARK else "#ffffff"
if DARK:
    st.markdown(DARK_CSS, unsafe_allow_html=True)


def filtro_fecha(df):
    m = (df["fecha"] == "") | ((df["fecha"] >= FROM) & (df["fecha"] <= TO))
    return df[m]


def filtro_multiselect(df, col, label, prefix):
    opts = sorted(df[col].dropna().unique())
    sel = st.multiselect(label, opts, key=f"ms_{prefix}_{col}")
    return df if not sel else df[df[col].isin(sel)]


# ---------------------------------------------------------------------------
# Helpers de gráficas (Altair)
# ---------------------------------------------------------------------------
def _theme(chart):
    return (chart
            .configure_axis(labelColor=_TXT, titleColor=_TXT, gridColor=_GRID, domainColor=_GRID)
            .configure_legend(labelColor=_TXT, titleColor=_TXT)
            .configure_title(color=_TXT, fontSize=14, fontWeight=600)
            .configure_view(stroke=None)
            .properties(background=_BG))


def donut(df, col, title, color_map=None, height=280):
    cmap = color_map or ESTADO_COLORES
    c = df[col].value_counts().reset_index()
    c.columns = [col, "n"]
    cats = list(c[col])
    rng = [cmap.get(k, PALETTE[i % len(PALETTE)]) for i, k in enumerate(cats)]
    return _theme(alt.Chart(c).mark_arc(innerRadius=55, outerRadius=95).encode(
        theta=alt.Theta("n:Q", stack=True),
        color=alt.Color(f"{col}:N", scale=alt.Scale(domain=cats, range=rng),
                        legend=alt.Legend(orient="bottom", title=None, labelLimit=0)),
        tooltip=[col, "n"],
    ).properties(title=title, height=height))


def hbar_top(df, col, title, n=10, color=C["blue"], height=400):
    c = df[col].value_counts().head(n).rename_axis(col).reset_index(name="n")
    c["label"] = c[col].map(lambda x: shorten(x))
    return _theme(alt.Chart(c).mark_bar(color=color).encode(
        x=alt.X("n:Q", axis=alt.Axis(format="d"), title="Registros"),
        y=alt.Y("label:N", sort="-x", title=None, axis=alt.Axis(labelLimit=340)),
        tooltip=[alt.Tooltip(col, title=col), "n"],
    ).properties(title=title, height=height))


def monthly(df, title, color=C["blue"], kind="bar", height=300):
    m = df.groupby("mes").size().reset_index(name="n")
    if ACUM:
        m = m.sort_values("mes")
        m["n"] = m["n"].cumsum()
    mk = alt.Chart(m).mark_bar(color=color) if kind == "bar" else alt.Chart(m).mark_line(
        color=color, point=True, strokeWidth=2.5)
    return _theme(mk.encode(x=alt.X("mes:N", title=None),
                            y=alt.Y("n:Q", axis=alt.Axis(format="d"), title="Registros"),
                            tooltip=["mes", "n"]).properties(title=title, height=height))


def monthly_grouped(a, b, la, lb, title, ca=C["blue"], cb=C["teal"], height=320):
    ma = a.groupby("mes").size().reset_index(name="n"); ma["cat"] = la
    mb = b.groupby("mes").size().reset_index(name="n"); mb["cat"] = lb
    m = pd.concat([ma, mb])
    if ACUM:
        m = m.sort_values(["cat", "mes"])
        m["n"] = m.groupby("cat")["n"].cumsum()
    return _theme(alt.Chart(m).mark_bar().encode(
        x=alt.X("mes:N", title=None),
        y=alt.Y("n:Q", axis=alt.Axis(format="d"), title="Registros"),
        color=alt.Color("cat:N", scale=alt.Scale(domain=[la, lb], range=[ca, cb]),
                        legend=alt.Legend(orient="bottom", title=None)),
        xOffset="cat:N", tooltip=["mes", "cat", "n"],
    ).properties(title=title, height=height))


def tabla(df, cols):
    cfg = {c: st.column_config.TextColumn(c, width="large")
           for c in cols if df[c].dtype == object}
    st.dataframe(df[cols], width="stretch", hide_index=True, column_config=cfg)


# ---------------------------------------------------------------------------
# Cabecera
# ---------------------------------------------------------------------------
st.markdown(
    f'<div class="sgti-header"><h1>SGTI — Panel de Gestión de TI</h1>'
    f'<div class="sgti-sub">Hospital Regional de Alta Especialidad · Exportación 2026-09-07 · '
    f'Rango activo: <b>{FROM}</b> → <b>{TO}</b></div></div>',
    unsafe_allow_html=True)

tabs = st.tabs(["Resumen", "Oficios realizados", "Oficios recibidos", "Notas informativas",
                "Cuentas de usuario", "Suministros", "Operaciones", "Hallazgos",
                "Calidad de datos"])

# ===== Resumen =====
with tabs[0]:
    OR, RR, NT, CU, EN, RE = (filtro_fecha(DATA[k]) for k in
                              ("or", "rr", "nt", "cu", "en", "re"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Oficios realizados", len(OR), f"{OR.estado.eq('Entregado').sum()} entregados")
    c2.metric("Oficios recibidos", len(RR), f"{RR.estado.eq('Contestado').sum()} contestados")
    c3.metric("Notas informativas", len(NT))
    c4, c5, c6 = st.columns(3)
    c4.metric("Cuentas de usuario", len(CU), f"{CU.estado.eq('Entregada').sum()} entregadas")
    c5.metric("Entregas suministro", len(EN), f"{EN.tipo.eq('Tóner').sum()} tóner")
    c6.metric("Equipos reubicados", len(RE))
    col_a, col_b = st.columns(2)
    with col_a:
        st.altair_chart(donut(OR, "estado", "Oficios realizados por estado"), width="stretch")
    with col_b:
        st.altair_chart(donut(RR, "estado", "Oficios recibidos por estado"), width="stretch")
    st.altair_chart(monthly_grouped(OR, RR, "Realizados", "Recibidos", "Oficios por mes"),
                    width="stretch")
    st.altair_chart(monthly(filtro_fecha(DATA["nt"]), "Notas informativas por mes",
                            color=C["purple"], kind="line"), width="stretch")

# ===== Oficios realizados =====
with tabs[1]:
    df = filtro_fecha(DATA["or"])
    f1, f2 = st.columns(2)
    with f1:
        df = filtro_multiselect(df, "area", "Área / Destino", "or")
    with f2:
        df = filtro_multiselect(df, "estado", "Estado", "or")
    st.caption(f"Mostrando {len(df)} oficios realizados.")
    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(donut(df, "estado", "Por estado"), width="stretch")
    with c2:
        st.altair_chart(monthly(df, "Por mes"), width="stretch")
    st.altair_chart(hbar_top(df, "area", "Por área (top 10)"), width="stretch")
    tabla(df, ["fecha", "numero", "area", "estado", "asunto"])

# ===== Oficios recibidos =====
with tabs[2]:
    df = filtro_fecha(DATA["rr"])
    f1, f2 = st.columns(2)
    with f1:
        df = filtro_multiselect(df, "area", "Área / Remitente", "rr")
    with f2:
        df = filtro_multiselect(df, "estado", "Estado", "rr")
    st.caption(f"Mostrando {len(df)} oficios recibidos.")
    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(donut(df, "estado", "Por estado"), width="stretch")
    with c2:
        st.altair_chart(monthly(df, "Por mes", color=C["teal"]), width="stretch")
    st.altair_chart(hbar_top(df, "area", "Por área (top 10)", color=C["teal"]), width="stretch")
    tabla(df, ["fecha", "numero", "remitente", "area", "estado", "asunto"])

# ===== Notas informativas =====
with tabs[3]:
    df = filtro_fecha(DATA["nt"])
    df = filtro_multiselect(df, "area", "Área (TI)", "nt")
    st.caption(f"Mostrando {len(df)} notas informativas.")
    st.altair_chart(monthly(df, "Notas por mes", color=C["purple"], kind="line"),
                    width="stretch")
    st.altair_chart(hbar_top(df, "area", "Por área (top 10)", color=C["purple"]),
                    width="stretch")
    tabla(df, ["fecha", "area", "autor", "asunto"])

# ===== Cuentas de usuario =====
with tabs[4]:
    df = filtro_fecha(DATA["cu"])
    f1, f2 = st.columns(2)
    with f1:
        df = filtro_multiselect(df, "area", "Coordinación", "cu")
    with f2:
        df = filtro_multiselect(df, "estado", "Estatus", "cu")
    st.caption(f"Mostrando {len(df)} cuentas de usuario.")
    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(donut(df, "estado", "Por estatus"), width="stretch")
    with c2:
        st.altair_chart(monthly(df, "Por mes (captura)", color=C["teal"]), width="stretch")
    st.altair_chart(hbar_top(df, "area", "Por coordinación (top 10)", color=C["teal"]),
                    width="stretch")
    tabla(df, ["fecha", "persona", "username", "area", "estado"])

# ===== Suministros =====
with tabs[5]:
    en = filtro_fecha(DATA["en"])
    ing = filtro_fecha(DATA["ing"])
    f1, f2 = st.columns(2)
    with f1:
        tipo = st.multiselect("Tipo", ["Tóner", "Papel"], key="ms_tipo_sumin")
    with f2:
        areas = sorted(en["area"].dropna().unique())
        areaf = st.multiselect("Área", areas, key="ms_area_sumin")
    if tipo:
        en = en[en["tipo"].isin(tipo)]; ing = ing[ing["tipo"].isin(tipo)]
    if areaf:
        en = en[en["area"].isin(areaf)]
    st.caption(f"Mostrando {len(en)} entregas y {len(ing)} ingresos.")
    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(donut(en, "tipo", "Entregas por tipo", color_map=TIPO_COLORES), width="stretch")
    with c2:
        st.altair_chart(monthly_grouped(en, ing, "Entregas", "Ingresos", "Ingresos vs entregas por mes",
                                        ca=C["teal"], cb=C["purple"]), width="stretch")
    st.altair_chart(hbar_top(en, "area", "Entregas por área (top 10)", color=C["teal"]),
                    width="stretch")
    st.subheader("Detalle de entregas")
    tabla(en, ["fecha", "tipo", "area", "cantidad", "marca"])
    st.subheader("Detalle de ingresos")
    tabla(ing, ["fecha", "tipo", "cantidad", "monto", "contrato"])

# ===== Operaciones =====
with tabs[6]:
    re, li, va, au = (filtro_fecha(DATA[k]) for k in ("re", "li", "va", "au"))
    c1, c2 = st.columns(2)
    with c1:
        st.altair_chart(donut(re, "tipo", "Reubicaciones por tipo"), width="stretch")
    with c2:
        st.altair_chart(monthly(re, "Reubicaciones por mes"), width="stretch")
    c3, c4 = st.columns(2)
    with c3:
        st.altair_chart(hbar_top(li, "ap", "Licencias por aplicativo", n=6, color=C["pink"]),
                        width="stretch")
    with c4:
        st.altair_chart(donut(va, "estado", "Vacaciones / incidencias por estado"),
                        width="stretch")
    au["modulo_lbl"] = au["modulo"].map(lambda m: MODULO_LABELS.get(m, m.replace("-", " ").title()))
    st.altair_chart(hbar_top(au, "modulo_lbl", "Actividad por módulo", n=8, color=C["gray"]),
                    width="stretch")
    st.subheader("Detalle de reubicaciones")
    tabla(re, ["fecha", "tipo", "equipo", "origen", "area"])
    st.subheader("Detalle de licencias")
    tabla(li, ["fecha", "ap", "hostname", "persona", "area"])

# ===== Hallazgos =====
with tabs[7]:
    st.info("Auditoría detallada (con ejemplos por tabla y columna) en **DATA_AUDIT.md** "
            "de la raíz del proyecto.")
    hallazgos = [
        ("🔴", "Alto backlog de oficios recibidos sin contestar",
         "250 de 373 oficios recibidos (67 %) siguen pendientes de contestación."),
        ("🟢", "Oficios emitidos casi al 100 % entregados",
         "242 de 245 oficios realizados (99 %) están entregados; solo 3 sin entregar."),
        ("🟠", "Nombres de área inconsistentes",
         "“Soporte Técnico” vs “Soporte Tecnico”, “Informática” vs “Informatica”; normalizados en el panel."),
        ("🔴", "Errores de año en fechas",
         "vacaciones_incidencias con 2032; oficios_realizados.fecha_fin y bitacora con 1926."),
        ("🟠", "Datos sucios en cuentas_usuario.estatus",
         "Mezcla etiquetas con frases libres y un objeto ArrayFormula de Excel sin evaluar."),
        ("🟠", "Cobertura parcial de claves de área",
         "cuentas_usuario.coordinacion_id 47 %; entregas_suministro.coordinacion_id 27 %."),
        ("🟡", "dias_transcurridos sin calcular",
         "186 en 0 y 187 vacíos en oficios_recibidos."),
        ("🟢", "Concentración de licencias en Microsoft Office",
         "133 de 149 asignaciones (89 %) son Office; Adobe aporta 11."),
        ("🟢", "Tóner domina las entregas de suministro",
         "94 entregas de tóner frente a 67 de papel; solo 24 ingresos registrados."),
    ]
    for icon, t, d in hallazgos:
        st.markdown(f"**{icon} {t}**  \n{d}")
        st.divider()

# ===== Calidad de datos =====
with tabs[8]:
    q = dq.compute()

    fk = q["fk_coverage"]
    bajo_90 = sum(1 for f in fk if f["pct"] < 90)
    n_tablas = len(fk)
    fechas_inv = q["fechas_invalidas"]["total"]
    estatus_dist = q["estatus_sucios"]["distintos"]
    formulas_excel = q["estatus_sucios"]["formulas_excel"]
    areas_grupos = q["areas_inconsistentes"]["grupos"]
    dias_sin = q["dias_transcurridos"]["ceros"] + q["dias_transcurridos"]["nulos"]
    dias_total = q["dias_transcurridos"]["total"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Claves de área < 90%", bajo_90, f"de {n_tablas} tablas")
    c2.metric("Fechas inválidas", fechas_inv)
    c3.metric("Estatus sucios", estatus_dist, f"{formulas_excel} fórmulas Excel")
    c4.metric("Áreas duplicadas", areas_grupos)
    c5.metric("Días sin calcular", dias_sin, f"de {dias_total} oficios")

    col_a, col_b = st.columns(2)
    with col_a:
        fkdf = pd.DataFrame(fk)
        fkdf["color"] = fkdf["pct"].map(
            lambda p: C["green"] if p >= 90 else C["amber"] if p >= 50 else C["red"])
        st.altair_chart(
            alt.Chart(fkdf).mark_bar().encode(
                x=alt.X("pct:Q", axis=alt.Axis(format=".0f"), title="Cobertura (%)"),
                y=alt.Y("tabla:N", sort="-x", title=None, axis=alt.Axis(labelLimit=340)),
                color=alt.Color("color:N", scale=None, legend=None),
                tooltip=["tabla", "columna", "mapeadas", "total", "pct"],
            ).properties(title="Cobertura de clave de área por tabla", height=400),
            width="stretch")
    with col_b:
        vdf = pd.DataFrame(q["estatus_sucios"]["valores"]).head(8)
        vdf["label"] = vdf["valor"].map(lambda x: shorten(x))
        st.altair_chart(
            alt.Chart(vdf).mark_bar(color=C["blue"]).encode(
                x=alt.X("n:Q", axis=alt.Axis(format="d"), title="Registros"),
                y=alt.Y("label:N", sort="-x", title=None, axis=alt.Axis(labelLimit=340)),
                tooltip=[alt.Tooltip("valor", title="valor"), "n"],
            ).properties(title="Valores crudos de cuentas_usuario.estatus", height=400),
            width="stretch")

    st.subheader("Hallazgos de calidad")
    ICONO = {"alta": "🔴", "media": "🟠", "baja": "🟡"}
    for h in q["hallazgos"]:
        icon = ICONO.get(h["severidad"], "⚪")
        st.markdown(f"**{icon} {h['titulo']}**  \n{h['descripcion']}")
        st.divider()
