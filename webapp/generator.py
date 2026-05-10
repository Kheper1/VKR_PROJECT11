from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = PROJECT_ROOT / "generated"
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "results"


DEFAULT_SCHEMA: dict[str, Any] = {
    "table": "readers",
    "description": "Таблица Читатели для проверки работоспособности распределённой базы данных",
    "columns": [
        {"name": "reader_id", "type": "INT", "primary_key": True},
        {"name": "full_name", "type": "VARCHAR(255)", "nullable": False},
        {"name": "birth_date", "type": "DATE", "nullable": True},
        {"name": "phone", "type": "VARCHAR(30)", "nullable": True},
        {"name": "email", "type": "VARCHAR(255)", "nullable": True},
        {"name": "branch_id", "type": "INT", "nullable": False},
        {"name": "is_deleted", "type": "BOOLEAN", "nullable": False},
    ],
}


EXPECTED_CENTER_ROWS: list[dict[str, Any]] = [
    {
        "reader_id": 1,
        "full_name": "Ivanov Ivan Ivanovich",
        "birth_date": "1990-01-15",
        "phone": "+7-900-111-99-99",
        "email": "ivanov.updated@example.com",
        "branch_id": 1,
        "is_deleted": 0,
    },
    {
        "reader_id": 2,
        "full_name": "Petrova Anna Sergeevna",
        "birth_date": "1988-05-20",
        "phone": "+7-900-222-22-22",
        "email": "petrova@example.com",
        "branch_id": 2,
        "is_deleted": 1,
    },
    {
        "reader_id": 3,
        "full_name": "Sidorov Petr Andreevich",
        "birth_date": "1995-09-10",
        "phone": "+7-900-333-33-33",
        "email": "sidorov.new@example.com",
        "branch_id": 3,
        "is_deleted": 0,
    },
    {
        "reader_id": 4,
        "full_name": "Kuznetsova Maria Pavlovna",
        "birth_date": "2001-03-12",
        "phone": "+7-900-444-44-44",
        "email": "kuznetsova@example.com",
        "branch_id": 1,
        "is_deleted": 0,
    },
    {
        "reader_id": 5,
        "full_name": "Orlov Dmitry Viktorovich",
        "birth_date": "1992-11-01",
        "phone": "+7-900-555-55-55",
        "email": "orlov@example.com",
        "branch_id": 2,
        "is_deleted": 0,
    },
    {
        "reader_id": 6,
        "full_name": "Morozova Elena Igorevna",
        "birth_date": "1999-07-07",
        "phone": "+7-900-666-66-66",
        "email": "morozova@example.com",
        "branch_id": 3,
        "is_deleted": 0,
    },
]


INITIAL_CENTER_ROWS: list[dict[str, Any]] = [
    {
        "reader_id": 1,
        "full_name": "Ivanov Ivan Ivanovich",
        "birth_date": "1990-01-15",
        "phone": "+7-900-111-11-11",
        "email": "ivanov@example.com",
        "branch_id": 1,
        "is_deleted": 0,
    },
    {
        "reader_id": 2,
        "full_name": "Petrova Anna Sergeevna",
        "birth_date": "1988-05-20",
        "phone": "+7-900-222-22-22",
        "email": "petrova@example.com",
        "branch_id": 2,
        "is_deleted": 0,
    },
    {
        "reader_id": 3,
        "full_name": "Sidorov Petr Andreevich",
        "birth_date": "1995-09-10",
        "phone": "+7-900-333-33-33",
        "email": "sidorov@example.com",
        "branch_id": 3,
        "is_deleted": 0,
    },
]


def parse_schema(raw_text: str | None) -> dict[str, Any]:
    if not raw_text or not raw_text.strip():
        return DEFAULT_SCHEMA

    text = raw_text.strip()
    if text.startswith("{"):
        parsed = json.loads(text)
        if parsed.get("table") != "readers":
            raise ValueError("В учебной версии поддерживается таблица readers / Читатели.")
        return parsed

    lowered = text.lower()
    if "create table" in lowered and ("readers" in lowered or "читатели" in lowered):
        schema = DEFAULT_SCHEMA.copy()
        schema["source_sql"] = text
        return schema

    raise ValueError("Файл должен содержать JSON-описание таблицы readers или SQL CREATE TABLE для readers.")


def sql_string(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    escaped = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{escaped}'"


def upsert_sql(row: dict[str, Any]) -> str:
    columns = ["reader_id", "full_name", "birth_date", "phone", "email", "branch_id", "is_deleted"]
    values = ", ".join(sql_string(row[column]) for column in columns)
    updates = ", ".join(f"{column} = VALUES({column})" for column in columns if column != "reader_id")
    return (
        f"INSERT INTO readers ({', '.join(columns)})\n"
        f"VALUES ({values})\n"
        f"ON DUPLICATE KEY UPDATE {updates};"
    )


def write_branch_scripts() -> None:
    branch1 = [
        "USE branch1_db;",
        "-- Филиал 1: обновление существующего читателя.",
        "UPDATE readers SET phone = '+7-900-111-99-99', email = 'ivanov.updated@example.com' WHERE reader_id = 1;",
        "-- Филиал 1: добавление нового читателя.",
        upsert_sql(EXPECTED_CENTER_ROWS[3]),
    ]
    branch2 = [
        "USE branch2_db;",
        "-- Филиал 2: логическое удаление читателя.",
        "UPDATE readers SET is_deleted = TRUE WHERE reader_id = 2;",
        "-- Филиал 2: добавление нового читателя.",
        upsert_sql(EXPECTED_CENTER_ROWS[4]),
    ]
    branch3 = [
        "USE branch3_db;",
        "-- Филиал 3: обновление email существующего читателя.",
        "UPDATE readers SET email = 'sidorov.new@example.com' WHERE reader_id = 3;",
        "-- Филиал 3: добавление нового читателя.",
        upsert_sql(EXPECTED_CENTER_ROWS[5]),
    ]

    (GENERATED_DIR / "branch1_changes.sql").write_text("\n\n".join(branch1) + "\n", encoding="utf-8")
    (GENERATED_DIR / "branch2_changes.sql").write_text("\n\n".join(branch2) + "\n", encoding="utf-8")
    (GENERATED_DIR / "branch3_changes.sql").write_text("\n\n".join(branch3) + "\n", encoding="utf-8")


def write_q0() -> None:
    q0 = """SELECT
    reader_id,
    full_name,
    DATE_FORMAT(birth_date, '%Y-%m-%d') AS birth_date,
    phone,
    email,
    branch_id,
    CAST(is_deleted AS UNSIGNED) AS is_deleted
FROM readers
ORDER BY reader_id;
"""
    (GENERATED_DIR / "Q0.sql").write_text(q0, encoding="utf-8")


def xml_dataset(rows: list[dict[str, Any]]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<dataset>"]
    for row in rows:
        attrs = " ".join(f'{key}="{escape(str(value))}"' for key, value in row.items())
        lines.append(f"    <readers {attrs}/>")
    lines.append("</dataset>")
    return "\n".join(lines) + "\n"


def write_datasets() -> None:
    (DATASETS_DIR / "initial_readers.xml").write_text(xml_dataset(INITIAL_CENTER_ROWS), encoding="utf-8")
    (DATASETS_DIR / "expected_center.xml").write_text(xml_dataset(EXPECTED_CENTER_ROWS), encoding="utf-8")
    (RESULTS_DIR / "expected_q0_result.json").write_text(
        json.dumps(EXPECTED_CENTER_ROWS, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_example_schema(schema: dict[str, Any]) -> None:
    (GENERATED_DIR / "readers_schema.json").write_text(
        json.dumps(schema, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def generate_project_files(raw_schema: str | None = None) -> dict[str, Any]:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    schema = parse_schema(raw_schema)
    write_example_schema(schema)
    write_branch_scripts()
    write_q0()
    write_datasets()

    return {
        "schema": schema,
        "generated_files": [
            "readers_schema.json",
            "branch1_changes.sql",
            "branch2_changes.sql",
            "branch3_changes.sql",
            "Q0.sql",
        ],
        "dataset_files": [
            "initial_readers.xml",
            "expected_center.xml",
        ],
        "result_files": [
            "expected_q0_result.json",
        ],
    }
