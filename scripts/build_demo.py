"""Genera dashboards DEMO en `demo/` usando los datos sintéticos de `sample_data/`.

Los dashboards del usuario (dashboard/, dashboard_v2/, dashboard_v3/) y sus datos
reales en Data/ NO se tocan: este script convierte `sample_data/` a un Parquet
temporal, lo lee con SGTI_PARQUET_DIR y escribe los tres dashboards (v1, v2, v3)
en `demo/v1`, `demo/v2`, `demo/v3` con datos sintéticos anónimos.

Uso:
    .venv/bin/python scripts/build_demo.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
DEMO = os.path.join(ROOT, "demo")
TMP_PARQUET = os.path.join(ROOT, ".sample_parquet_tmp")


def run(cmd):
    print("+", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(r.returncode)


def main():
    # 1. Parquet sintético en un directorio temporal (no toca Data/parquet real).
    if os.path.isdir(TMP_PARQUET):
        shutil.rmtree(TMP_PARQUET)
    run([os.path.join(ROOT, ".venv", "bin", "python"),
         os.path.join(SCRIPTS, "csv_to_parquet.py"),
         "--csv-dir", os.path.join(ROOT, "sample_data"),
         "--out-dir", TMP_PARQUET])

    os.environ["SGTI_PARQUET_DIR"] = TMP_PARQUET
    sys.path.insert(0, SCRIPTS)
    import build_dashboard as bd          # noqa: E402
    import build_dashboard_v2 as bdv2     # noqa: E402
    import build_dashboard_v3 as bdv3     # noqa: E402

    # 2. Escribir cada dashboard en demo/{v1,v2,v3} en vez de las carpetas reales.
    targets = [
        (bd,   os.path.join(DEMO, "v1", "index.html")),
        (bdv2, os.path.join(DEMO, "v2", "index.html")),
        (bdv3, os.path.join(DEMO, "v3", "index.html")),
    ]
    for mod, out in targets:
        mod.OUT = out
        mod.main()

    # 3. Copiar vendor (Chart.js) a cada carpeta demo.
    src_vendor = os.path.join(ROOT, "dashboard_v3", "vendor", "chart.umd.min.js")
    for sub in ("v1", "v2", "v3"):
        dst = os.path.join(DEMO, sub, "vendor")
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(src_vendor, os.path.join(dst, "chart.umd.min.js"))

    # 4. Limpiar el Parquet temporal.
    if os.path.isdir(TMP_PARQUET):
        shutil.rmtree(TMP_PARQUET)

    print("\nDashboards demo generados en", DEMO)
    print("Abre demo/v3/index.html para ver la versión más reciente.")


if __name__ == "__main__":
    main()
