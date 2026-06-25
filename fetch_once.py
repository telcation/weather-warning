from db import init_db, save_result, cleanup_old_logs
from jma import fetch_city_warnings


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

    result = fetch_city_warnings()
    result["warnings"] = warnings_to_text_list(result["warnings"])

    save_result(result, source="auto")


if __name__ == "__main__":
    main()
