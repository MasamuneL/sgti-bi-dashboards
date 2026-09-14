"""Validate the generated Parquet files against the source CSVs/manifest.

Checks per table:
  - Parquet exists and its row count matches the manifest.
  - Column set matches the CSV header.
  - Non-null primary key columns (id-like) have no nulls.
  - Date columns are ISO (no parse failures log optionally).

Usage:
    python scripts/validate_parquet.py [--csv-dir DIR] [--parquet-dir DIR]
Exits non-zero if any check fails.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from csv_to_parquet import infer_type

# Tables which legitimately should never have a null id.
PK_TABLES = {
    "aplicativos_licencia",
    "asignaciones_licenciamiento",
    "audit_log",
    "bitacora_equipo_portatil",
    "coordinaciones",
    "cuentas_usuario",
    "entregas_suministro",
    "historico_reubicaciones_equipos",
    "ingresos_suministro",
    "minutas_circulares",
    "monitor_notifications",
    "monitor_sites",
    "notas_informativas",
    "oficios_realizados",
    "oficios_recibidos",
    "personal_hospital",
    "personal_ti",
    "usuarios_sistema",
    "vacaciones_incidencias",
    "vacaciones_incidencias_fechas",
}


def validate_parquet(table: str, csv_cols: list[str], expected_rows: int, pq_path: Path, csv_path: Path) -> list[str]:
    errors: list[str] = []
    if not pq_path.exists():
        return [f"missing parquet: {pq_path}"]

    parquet_file = pq.ParquetFile(pq_path)
    row_count = parquet_file.metadata.num_rows
    if row_count != expected_rows:
        errors.append(f"row count mismatch: expected {expected_rows}, got {row_count}")

    arrow_schema = parquet_file.schema_arrow
    pq_cols = [field.name for field in arrow_schema]
    if pq_cols != csv_cols:
        errors.append(f"column mismatch:\n  csv:      {csv_cols}\n  parquet:  {pq_cols}")

    if table in PK_TABLES:
        table_df = pq.read_table(pq_path).to_pandas()
        if "id" in table_df.columns:
            nulls = int(table_df["id"].isna().sum())
            if nulls:
                errors.append(f"primary key 'id' has {nulls} nulls")

    # Every non-empty value in a source date column must have parsed to a real
    # date in the parquet. Empty source cells -> null dates are expected.
    source_raw = pd.read_csv(csv_path, dtype="object", keep_default_na=False, encoding="utf-8")
    for col in csv_cols:
        if infer_type(table, col) == "date":
            pq_values = pq.read_table(pq_path, columns=[col]).to_pandas()[col]
            non_empty = source_raw[col].str.strip().ne("")
            non_empty = non_empty & source_raw[col].notna()
            failed = int((pq_values.isna() & non_empty).sum()) if non_empty.any() else 0
            if failed:
                errors.append(f"date column '{col}': {failed} non-empty source values failed to parse")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-dir", type=Path, help="Folder containing the CSV exports")
    parser.add_argument("--parquet-dir", type=Path, help="Folder with the generated Parquet files")
    args = parser.parse_args(argv)

    base = Path(__file__).resolve().parent.parent
    if args.csv_dir:
        csv_dir = args.csv_dir
    else:
        candidates = sorted((base / "Data").glob("hraelocal1-*"))
        csv_dir = next((p for p in candidates if p.is_dir()), list(candidates)[0].parent)
    parquet_dir = args.parquet_dir or (base / "Data" / "parquet")

    manifest = json.loads((csv_dir / "manifest.json").read_text(encoding="utf-8"))

    total_errors = 0
    for entry in manifest["tables"]:
        table = entry["table"]
        header = pd.read_csv(csv_dir / entry["file"], nrows=0).columns.tolist()
        pq_path = parquet_dir / f"{table}.parquet"
        errors = validate_parquet(table, header, entry["rows"], pq_path, csv_dir / entry["file"])
        status = "ok  " if not errors else "FAIL"
        print(f"  {status}  {table:42s} rows={entry['rows']:<6} cols={len(header)}")
        for err in errors:
            print(f"         ! {err}")
        total_errors += len(errors)

    print(f"\nValidation {'PASSED' if total_errors == 0 else f'FAILED ({total_errors} issues)'}")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())