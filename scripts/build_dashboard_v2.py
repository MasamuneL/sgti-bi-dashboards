"""Genera dashboard_v2/index.html (versión con pestaña "Calidad de datos" + acumulado).

Reutiliza los datasets de build_dashboard.py y agrega el payload "quality" desde
data_quality.compute(). Lee scripts/dashboard_template_v2.html.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_dashboard as bd  # noqa: E402
import data_quality as dq  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "scripts", "dashboard_template_v2.html")
OUT = os.path.join(ROOT, "dashboard_v2", "index.html")


def main():
    data = {
        "oficiosRealizados": bd.build_or(),
        "oficiosRecibidos": bd.build_rr(),
        "notas": bd.build_nt(),
        "cuentas": bd.build_cu(),
        "entregas": bd.build_en(),
        "ingresos": bd.build_in(),
        "reubicaciones": bd.build_re(),
        "licencias": bd.build_li(),
        "vacaciones": bd.build_va(),
        "audit": bd.build_au(),
    }
    all_dates = sorted(r.get("fecha") for rows in data.values() for r in rows if r.get("fecha"))
    payload = {
        "meta": {"minDate": all_dates[0], "maxDate": all_dates[-1], "export": "2026-09-07"},
        "data": data,
        "quality": dq.compute(),
    }

    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()
    js = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("__DATA_JSON__", js)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("Generado:", OUT)
    print("Registros:", {k: len(v) for k, v in data.items()})


if __name__ == "__main__":
    main()
