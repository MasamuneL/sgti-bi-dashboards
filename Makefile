# Makefile del proyecto SGTI — paneles de reportes BI.
#
# Targets de uso común (ver `make help`):
#   make refresh    Convertir CSV → Parquet y validar (usa Data/, datos reales)
#   make dashboard  Generar el panel HTML v3 (la versión vigente)
#   make demo       Regenerar la demo con datos sintéticos (sample_data/)
#   make streamlit  Lanzar Streamlit v3 (lee los Parquet en vivo)
#   make audit      Regenerar DATA_AUDIT.md
#   make docs       Regenerar DATA_DICTIONARY.md
#
# Todos usan el venv del proyecto (.venv/bin/…). Si aún no existe, créalo con:
#   uv venv .venv && uv pip install -r requirements.txt

PY      := .venv/bin/python
ST      := .venv/bin/streamlit
SCRIPTS := scripts

.PHONY: help refresh dashboard demo streamlit audit docs validate all clean

help:
	@echo "Targets disponibles:"
	@echo "  make refresh    -> CSV -> Parquet + validacion (datos reales en Data/)"
	@echo "  make dashboard  -> genera dashboard_v3/index.html (HTML vigente)"
	@echo "  make demo       -> regenera demo/v1..v3 con datos sinteticos"
	@echo "  make streamlit  -> lanza Streamlit v3 en http://localhost:8501"
	@echo "  make audit      -> regenera DATA_AUDIT.md"
	@echo "  make docs       -> regenera DATA_DICTIONARY.md"
	@echo "  make validate   -> solo valida los Parquet actuales"
	@echo "  make clean      -> borra Data/parquet y las demos generadas"

refresh:
	$(PY) $(SCRIPTS)/refresh_all.py

dashboard:
	$(PY) $(SCRIPTS)/build_dashboard_v3.py

demo:
	$(PY) $(SCRIPTS)/build_sample_data.py
	$(PY) $(SCRIPTS)/build_demo.py

streamlit:
	$(ST) run streamlit_dashboard_v3.py

audit:
	$(PY) $(SCRIPTS)/generate_audit.py

docs:
	$(PY) $(SCRIPTS)/generate_docs.py

validate:
	$(PY) $(SCRIPTS)/validate_parquet.py

clean:
	rm -rf Data/parquet demo/v1 demo/v2 demo/v3
	@echo "Borrados Data/parquet y demo/v1..v3. Regenera con 'make refresh' o 'make demo'."

all: refresh dashboard
