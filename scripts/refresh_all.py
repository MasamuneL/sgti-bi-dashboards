"""One-command refresh: re-convert CSVs to Parquet then validate.

Usage:
    python scripts/refresh_all.py
Optionally pass the same CLI flags accepted by both stages.
"""

from __future__ import annotations

import sys

import csv_to_parquet
import validate_parquet


def main() -> int:
    print("=== [1/2] Converting CSV -> Parquet ===")
    if csv_to_parquet.main() != 0:
        print("Conversion failed.")
        return 1
    print()
    print("=== [2/2] Validating Parquet ===")
    if validate_parquet.main() != 0:
        print("Validation failed.")
        return 1
    print()
    print("Refresh complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())