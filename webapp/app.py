from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for

from checker import compare_rows, load_json_rows
from consolidate import consolidate_readers
from db import check_all_connections, fetch_readers_from_center
from generator import DATASETS_DIR, GENERATED_DIR, RESULTS_DIR, generate_project_files


app = Flask(__name__)
app.secret_key = "diplom-secret-key"

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def ensure_generated_files() -> None:
    if not (GENERATED_DIR / "Q0.sql").exists():
        generate_project_files()


@app.route("/", methods=["GET"])
def index():
    ensure_generated_files()
    return render_template(
        "index.html",
        connections=check_all_connections(),
        generated_files=sorted(path.name for path in GENERATED_DIR.iterdir() if path.is_file()),
        dataset_files=sorted(path.name for path in DATASETS_DIR.iterdir() if path.is_file()),
        result_files=sorted(path.name for path in RESULTS_DIR.iterdir() if path.is_file()),
    )


@app.route("/generate", methods=["POST"])
def generate():
    schema_text = request.form.get("schema_text", "")
    uploaded_file = request.files.get("schema_file")
    if uploaded_file and uploaded_file.filename:
        schema_text = uploaded_file.read().decode("utf-8")

    try:
        generation_result = generate_project_files(schema_text)
        flash(f"Файлы успешно сгенерированы: {', '.join(generation_result['generated_files'])}", "success")
    except Exception as exc:
        flash(f"Ошибка генерации файлов: {exc}", "error")
    return redirect(url_for("index"))


@app.route("/download/generated/<path:filename>")
def download_generated(filename: str):
    return send_from_directory(GENERATED_DIR, filename, as_attachment=True)


@app.route("/download/datasets/<path:filename>")
def download_dataset(filename: str):
    return send_from_directory(DATASETS_DIR, filename, as_attachment=True)


@app.route("/download/results/<path:filename>")
def download_result(filename: str):
    return send_from_directory(RESULTS_DIR, filename, as_attachment=True)


@app.route("/consolidate", methods=["POST"])
def consolidate():
    try:
        report = consolidate_readers()
        if report["success"]:
            flash(f"Консолидация выполнена успешно. Обработано записей: {report['processed']}.", "success")
        else:
            flash(f"Консолидация выполнена с ошибками: {report['errors']}", "error")
    except Exception as exc:
        flash(f"Ошибка консолидации: {exc}", "error")
    return redirect(url_for("index"))


@app.route("/run-q0", methods=["POST"])
def run_q0():
    try:
        rows = fetch_readers_from_center()
        result_path = RESULTS_DIR / "q0_result.json"
        result_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        flash("Q0 выполнен на центральной БД. Результат сохранён в results/q0_result.json.", "success")
    except Exception as exc:
        flash(f"Ошибка выполнения Q0: {exc}", "error")
    return redirect(url_for("index"))


@app.route("/check", methods=["POST"])
def check():
    uploaded_file = request.files.get("q0_result_file")
    try:
        if uploaded_file and uploaded_file.filename:
            target_path = RESULTS_DIR / "uploaded_q0_result.json"
            target_path.write_bytes(uploaded_file.read())
            actual_rows = load_json_rows(target_path)
        else:
            target_path = RESULTS_DIR / "q0_result.json"
            actual_rows = load_json_rows(target_path)

        check_result = compare_rows(actual_rows)
        return render_template("check.html", result=check_result)
    except Exception as exc:
        flash(f"Ошибка проверки результата Q0: {exc}", "error")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
