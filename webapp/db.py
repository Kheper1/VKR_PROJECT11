from __future__ import annotations

import os
from typing import Any

import mysql.connector


MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "diplom")
MYSQL_USER = os.getenv("MYSQL_USER", "diplom")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")


DB_CONFIGS: dict[str, dict[str, Any]] = {
    "center": {
        "host": MYSQL_HOST,
        "port": int(os.getenv("MYSQL_CENTER_PORT", "3307")),
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": "center_db",
    },
    "branch1": {
        "host": MYSQL_HOST,
        "port": int(os.getenv("MYSQL_BRANCH1_PORT", "3308")),
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": "branch1_db",
    },
    "branch2": {
        "host": MYSQL_HOST,
        "port": int(os.getenv("MYSQL_BRANCH2_PORT", "3309")),
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": "branch2_db",
    },
    "branch3": {
        "host": MYSQL_HOST,
        "port": int(os.getenv("MYSQL_BRANCH3_PORT", "3310")),
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": "branch3_db",
    },
}


def get_connection(node_name: str):
    if node_name not in DB_CONFIGS:
        raise ValueError(f"Unknown database node: {node_name}")
    return mysql.connector.connect(**DB_CONFIGS[node_name])


def check_all_connections() -> dict[str, str]:
    result: dict[str, str] = {}
    for node_name in DB_CONFIGS:
        try:
            conn = get_connection(node_name)
            conn.close()
            result[node_name] = "OK"
        except Exception as exc:
            result[node_name] = f"ERROR: {exc}"
    return result


def fetch_readers_from_center() -> list[dict[str, Any]]:
    query = """
        SELECT
            reader_id,
            full_name,
            DATE_FORMAT(birth_date, '%Y-%m-%d') AS birth_date,
            phone,
            email,
            branch_id,
            CAST(is_deleted AS UNSIGNED) AS is_deleted
        FROM readers
        ORDER BY reader_id
    """
    conn = get_connection("center")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
