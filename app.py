import os
from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv

from db import (
    init_db,
    latest_logs,
    save_result,
    cleanup_old_logs,
)
from jma import fetch_city_warnings

load_dotenv()

BASE_PATH = os.getenv("APP_BASE_PATH", "").rstrip("/")

app = Flask(__name__)


def warnings_to_text_list(warnings: list[dict]) -> list[str]:
    """warningsの辞書リストをDB保存用の文字列リストに変換する。
    {"name": "大雨危険警報", "level": "4"} -> "レベル4 大雨危険警報"
    {"name": "雷注意報",     "level": None} -> "雷注意報"
    """
    result = []
    for w in warnings:
        if w["level"]:
            result.append(f"レベル{w['level']} {w['name']}")
        else:
            result.append(w["name"])
    return result


@app.before_request
def redirect_without_base_path():
    if BASE_PATH and request.path == BASE_PATH:
        return redirect(BASE_PATH + "/")


@app.route("/")
def index():
    try:
        result = fetch_city_warnings()
        error = None
    except Exception as e:
        result = None
        error = str(e)
    return render_template("index.html", result=result, logs=latest_logs(), error=error, base_path=BASE_PATH)


@app.route("/fetch", methods=["POST"])
def fetch_and_save():
    result = fetch_city_warnings()
    result["warnings"] = warnings_to_text_list(result["warnings"])
    save_result(result, source="manual")

    if BASE_PATH:
        return redirect(BASE_PATH + "/")
    return redirect(url_for("index"))


@app.route("/healthz")
def healthz():
    return "ok"


init_db()
cleanup_old_logs()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5010, debug=True)
