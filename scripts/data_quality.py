"""Métricas de calidad de datos para el tablero "Calidad de datos" (v2).

Reutiliza los chequeos de generate_audit.py y los expone como un dict JSON-able,
compartido por el HTML (via build_dashboard_v2.py) y por Streamlit (streamlit_dashboard_v2.py).

Uso:
    from data_quality import compute   # -> dict
    .venv/bin/python scripts/data_quality.py   # -> vuelca JSON a stdout
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_audit as ga  # noqa: E402

HALLAZGOS = [
    {"severidad": "alta", "titulo": "Alto backlog de oficios recibidos sin contestar",
     "descripcion": "250 de 373 oficios recibidos (67 %) siguen pendientes de contestación."},
    {"severidad": "alta", "titulo": "Errores de año en fechas",
     "descripcion": "vacaciones_incidencias con año 2032 y oficios_realizados.fecha_fin / "
                    "bitacora_equipo_portatil con 1926."},
    {"severidad": "media", "titulo": "Cobertura parcial de claves de área",
     "descripcion": "cuentas_usuario.coordinacion_id (47 %) y entregas_suministro.coordinacion_id "
                    "(27 %) dejan registros sin área asignada."},
    {"severidad": "media", "titulo": "Estatus sucios en cuentas_usuario.estatus",
     "descripcion": "Mezcla etiquetas con frases libres y un objeto ArrayFormula de Excel sin evaluar."},
    {"severidad": "media", "titulo": "Nombres de área inconsistentes",
     "descripcion": "La misma área aparece con/sin acento y con mayúsculas distintas en el texto libre."},
    {"severidad": "baja", "titulo": "dias_transcurridos sin calcular",
     "descripcion": "En oficios_recibidos, 186 registros valen 0 y 187 están vacíos."},
    {"severidad": "baja", "titulo": "Meses con mayúsculas inconsistentes",
     "descripcion": "oficios_realizados.mes mezcla marzo/Marzo/JULIO; se deriva de fecha_inicio."},
]


def compute():
    fk = [{"tabla": t, "columna": c, "total": tot, "mapeadas": m, "pct": p}
          for t, c, tot, m, p in ga.check_fk()]
    date_err = ga.check_dates()
    estatus, weird, _neg = ga.check_estatus()
    areas = ga.check_areas()
    ceros, nulos, total_rr = ga.check_dias()

    valores = ([{"valor": k, "n": v} for k, v in sorted(estatus.items(), key=lambda x: -x[1])]
               + [{"valor": k, "n": v} for k, v in weird])

    return {
        "fk_coverage": fk,
        "fechas_invalidas": {
            "total": sum(n for _, _, n, _ in date_err),
            "detalle": [{"tabla": t, "columna": c, "n": n, "ejemplos": ex}
                        for t, c, n, ex in date_err],
        },
        "estatus_sucios": {
            "distintos": len(valores),
            "formulas_excel": len(weird),
            "valores": valores,
        },
        "areas_inconsistentes": {
            "grupos": len(areas),
            "ejemplos": [{"normalizado": n, "variantes": v}
                         for n, v in sorted(areas.items(), key=lambda kv: -len(kv[1]))[:10]],
        },
        "dias_transcurridos": {"ceros": ceros, "nulos": nulos, "total": total_rr},
        "hallazgos": HALLAZGOS,
    }


if __name__ == "__main__":
    print(json.dumps(compute(), ensure_ascii=False))
