"""Convert the exported SGTI CSVs into a mirrored folder of Parquet files.

Usage:
    python scripts/csv_to_parquet.py [--csv-dir DIR] [--out-dir DIR]

- Reads the manifest.json next to the CSVs as the source of truth for
  table/file mapping and expected row counts.
- Normalizes all date/datetime columns to ISO-8601 (dates to date32,
  timestamps to UTC microsecond timestamps).
- Typecasts ID columns to nullable Int64, flags to boolean, amounts to float.
- Writes with snappy compression into ``--out-dir`` (default Data/parquet).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from normalize_dates import (
    clean_string_series,
    normalize_time_series,
    parse_date_series,
    parse_datetime_series,
)

BOOL_COLUMNS = {
    "activo",
    "permitido",
    "puede_eliminar",
    "puede_editar",
    "puede_aprobar_vacaciones",
    "puede_ver_todos_excepto",
    "puede_ver_todos_excepto_minutas",
    "puede_agregar_suministro",
    "puede_entregar_papel_suministro",
    "puede_asignar_toner_suministro",
    "puede_ver_graficas_suministro",
    "puede_ver_inventario_suministro",
    "puede_ver_toners_suministro",
    "puede_ver_papel_suministro",
    "puede_ver_contratos_suministro",
    "puede_ocultar_instrucciones",
    "entregado",
    "cancelado",
    "contestado",
    "notificacion",
    "es_cuenta_generica",
    "se_da_negativa",
    "requiere_atencion_proveedor",
}

INT_COLUMNS = {
    "id",
    "cantidad",
    "cantidad_disponible",
    "pdf_tamano",
    "numero_empleado",
    "numero_plaza",
    "numero_tarjeta",
    "contador_total",
    "dias_transcurridos",
    "extension",
    "expected_status",
    "timeout_seconds",
    "check_interval_seconds",
    "failure_threshold",
    "success_threshold",
    "consecutive_failures",
    "consecutive_successes",
    "last_latency_ms",
    "consecutivo_asignado",
}

# Columns whose name matches a generic pattern but must be handled differently.
OVERRIDES: dict[str, dict[str, str]] = {
    "historico_reubicaciones_equipos": {
        "fecha_hora_movimiento": "datetime",
        "fecha_hora_reubicacion": "datetime",
    },
}


def infer_type(table: str, column: str) -> str:
    """Return kind for a column: date|datetime|time|int|float|bool|string."""
    if column in OVERRIDES.get(table, {}):
        return OVERRIDES[table][column]
    if column in BOOL_COLUMNS:
        return "bool"
    if column == "monto":
        return "float"
    if column == "timestamp" or column.endswith("_at"):
        return "datetime"
    if column == "fecha" or column.startswith("fecha_") or column.startswith("periodo_"):
        return "date"
    if column.startswith("hora_"):
        return "time"
    if column == "id" or column.endswith("_id") or column in INT_COLUMNS:
        return "int"
    return "string"


def to_bool_series(series: pd.Series) -> pd.Series:
    """Map 0/1/true/false (or empty) to nullable boolean."""
    def _b(v):
        if v is None:
            return pd.NA
        if isinstance(v, (bool, np.bool_)):
            return bool(v)
        text = str(v).strip().lower()
        if text in {"1", "true", "t", "si", "sí", "y", "yes"}:
            return True
        if text in {"0", "false", "f", "no", "n"}:
            return False
        return pd.NA

    return series.map(_b).astype("boolean")


def to_int_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def to_float_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("float64")


def transform_table(frame: pd.DataFrame, table: str) -> pd.DataFrame:
    """Apply per-column type normalization."""
    result = frame.copy()
    for column in result.columns:
        kind = infer_type(table, column)
        col = result[column]
        if kind == "date":
            result[column] = parse_date_series(col)
        elif kind == "datetime":
            result[column] = parse_datetime_series(col)
        elif kind == "time":
            result[column] = normalize_time_series(clean_string_series(col))
        elif kind == "int":
            result[column] = to_int_series(clean_string_series(col))
        elif kind == "float":
            result[column] = to_float_series(clean_string_series(col))
        elif kind == "bool":
            result[column] = to_bool_series(clean_string_series(col))
        else:
            result[column] = clean_string_series(col)
    return result


def build_arrow_type(kind: str) -> pa.DataType:
    if kind == "date":
        return pa.date32()
    if kind == "datetime":
        return pa.timestamp("us", tz="UTC")
    if kind == "time":
        return pa.string()
    if kind == "int":
        return pa.int64()
    if kind == "float":
        return pa.float64()
    if kind == "bool":
        return pa.bool_()
    return pa.string()


def convert_file(csv_path: Path, out_dir: Path, table: str) -> Path:
    frame = pd.read_csv(csv_path, dtype="object", keep_default_na=False, encoding="utf-8")
    frame = transform_table(frame, table)

    arrow_table = pa.Table.from_pandas(frame, preserve_index=False)
    expected_schema = pa.schema(
        [
            pa.field(col, build_arrow_type(infer_type(table, col)))
            for col in frame.columns
        ]
    )
    arrow_table = arrow_table.cast(expected_schema)

    out_path = out_dir / f"{table}.parquet"
    pq.write_table(arrow_table, out_path, compression="snappy")
    return out_path


def load_manifest(manifest_path: Path) -> dict:
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-dir", type=Path, help="Folder containing the CSV exports")
    parser.add_argument("--out-dir", type=Path, help="Destination folder for Parquet files")
    args = parser.parse_args(argv)

    base = Path(__file__).resolve().parent.parent
    if args.csv_dir:
        csv_dir = args.csv_dir
    else:
        candidates = sorted((base / "Data").glob("hraelocal1-*"))
        csv_dir = next((p for p in candidates if p.is_dir()), base / "Data")
    out_dir = args.out_dir or (base / "Data" / "parquet")

    manifest_path = csv_dir / "manifest.json"
    manifest = load_manifest(manifest_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    failures = []
    for entry in manifest["tables"]:
        table = entry["table"]
        csv_path = csv_dir / entry["file"]
        try:
            out_path = convert_file(csv_path, out_dir, table)
            rows = entry["rows"]
            print(f"  ok   {table:42s} -> {out_path.name} ({rows} rows)")
            converted += 1
        except Exception as exc:  # noqa: BLE001 - surface every failing table
            failures.append((table, str(exc)))
            print(f"  FAIL {table:42s} {exc}")

    print(f"\nConverted {converted}/{len(manifest['tables'])} tables to {out_dir}")
    if failures:
        for table, err in failures:
            print(f"  - {table}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())