from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from generator import EXPECTED_CENTER_ROWS


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    if "is_deleted" in normalized:
        value = normalized["is_deleted"]
        if isinstance(value, bool):
            normalized["is_deleted"] = 1 if value else 0
        elif isinstance(value, str):
            normalized["is_deleted"] = 1 if value.lower() in ("1", "true", "yes") else 0
        else:
            normalized["is_deleted"] = int(value)
    if "reader_id" in normalized:
        normalized["reader_id"] = int(normalized["reader_id"])
    if "branch_id" in normalized:
        normalized["branch_id"] = int(normalized["branch_id"])
    return normalized


def load_json_rows(file_path: Path) -> list[dict[str, Any]]:
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "rows" in data:
        data = data["rows"]
    if not isinstance(data, list):
        raise ValueError("Файл результата Q0 должен содержать JSON-массив строк.")
    return [normalize_row(row) for row in data]


def compare_rows(actual_rows: list[dict[str, Any]]) -> dict[str, Any]:
    expected = [normalize_row(row) for row in EXPECTED_CENTER_ROWS]
    actual = [normalize_row(row) for row in actual_rows]

    expected_by_id = {row["reader_id"]: row for row in expected}
    actual_by_id = {row["reader_id"]: row for row in actual}

    errors: list[str] = []

    for reader_id, expected_row in expected_by_id.items():
        if reader_id not in actual_by_id:
            errors.append(f"Не найдена ожидаемая запись reader_id={reader_id}.")
            continue
        actual_row = actual_by_id[reader_id]
        for field_name, expected_value in expected_row.items():
            actual_value = actual_row.get(field_name)
            if str(actual_value) != str(expected_value):
                errors.append(
                    f"reader_id={reader_id}, поле {field_name}: ожидалось {expected_value}, получено {actual_value}."
                )

    for reader_id in actual_by_id:
        if reader_id not in expected_by_id:
            errors.append(f"В результате есть лишняя запись reader_id={reader_id}.")

    return {
        "success": not errors,
        "errors": errors,
        "expected_count": len(expected),
        "actual_count": len(actual),
    }
