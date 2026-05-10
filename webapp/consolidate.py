from __future__ import annotations

from typing import Any

from db import get_connection


BRANCHES = [
    ("branch1", 1),
    ("branch2", 2),
    ("branch3", 3),
]


def fetch_branch_rows(branch_name: str) -> list[dict[str, Any]]:
    conn = get_connection(branch_name)
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                reader_id,
                full_name,
                birth_date,
                phone,
                email,
                branch_id,
                CAST(is_deleted AS UNSIGNED) AS is_deleted
            FROM readers
            ORDER BY reader_id
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def upsert_center_row(center_cursor, row: dict[str, Any]) -> None:
    center_cursor.execute(
        """
        INSERT INTO readers
            (reader_id, full_name, birth_date, phone, email, branch_id, is_deleted)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            full_name = VALUES(full_name),
            birth_date = VALUES(birth_date),
            phone = VALUES(phone),
            email = VALUES(email),
            branch_id = VALUES(branch_id),
            is_deleted = VALUES(is_deleted)
        """,
        (
            row["reader_id"],
            row["full_name"],
            row["birth_date"],
            row["phone"],
            row["email"],
            row["branch_id"],
            row["is_deleted"],
        ),
    )


def log_consolidation(center_cursor, branch_id: int, reader_id: int, status: str, message: str) -> None:
    center_cursor.execute(
        """
        INSERT INTO consolidation_log
            (source_branch_id, reader_id, operation_type, status, message)
        VALUES
            (%s, %s, %s, %s, %s)
        """,
        (branch_id, reader_id, "UPSERT", status, message),
    )


def consolidate_readers() -> dict[str, Any]:
    report: dict[str, Any] = {
        "processed": 0,
        "branches": {},
        "errors": [],
    }

    center_conn = get_connection("center")
    try:
        center_cursor = center_conn.cursor()
        for branch_name, branch_id in BRANCHES:
            branch_report = {"processed": 0, "errors": []}
            try:
                rows = fetch_branch_rows(branch_name)
                for row in rows:
                    try:
                        upsert_center_row(center_cursor, row)
                        log_consolidation(
                            center_cursor,
                            branch_id,
                            row["reader_id"],
                            "OK",
                            f"Запись reader_id={row['reader_id']} перенесена из {branch_name}.",
                        )
                        branch_report["processed"] += 1
                        report["processed"] += 1
                    except Exception as exc:
                        error = f"{branch_name}, reader_id={row.get('reader_id')}: {exc}"
                        branch_report["errors"].append(error)
                        report["errors"].append(error)
                        log_consolidation(
                            center_cursor,
                            branch_id,
                            row.get("reader_id", -1),
                            "ERROR",
                            str(exc),
                        )
            except Exception as exc:
                error = f"Ошибка чтения из {branch_name}: {exc}"
                branch_report["errors"].append(error)
                report["errors"].append(error)
            report["branches"][branch_name] = branch_report
        center_conn.commit()
    except Exception:
        center_conn.rollback()
        raise
    finally:
        center_conn.close()

    report["success"] = not report["errors"]
    return report


if __name__ == "__main__":
    result = consolidate_readers()
    print(result)
