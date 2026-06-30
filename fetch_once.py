from dotenv import load_dotenv
load_dotenv()

from db import init_db, save_result, cleanup_old_logs
from jma import fetch_city_warnings
from line_notify import notify_api_error, notify_unknown_codes


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


def main():
    init_db()
    cleanup_old_logs()

    # --- APIデータ取得 ---
    try:
        result = fetch_city_warnings()
    except Exception as e:
        # エンドポイント変更・ネットワークエラー等
        print(f"[ERROR] fetch_city_warnings failed: {e}", flush=True)
        notify_api_error(e)
        return

    # --- 不明コード検知 ---
    unknown_codes = [
        w["name"] for w in result["warnings"]
        if w["name"].startswith("不明コード:")
    ]
    if unknown_codes:
        print(f"[WARN] unknown codes detected: {unknown_codes}", flush=True)
        notify_unknown_codes(unknown_codes)

    # --- DB保存 ---
    result["warnings"] = warnings_to_text_list(result["warnings"])
    save_result(result, source="auto")


if __name__ == "__main__":
    main()
