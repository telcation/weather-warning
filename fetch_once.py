from db import init_db, save_result, cleanup_old_logs
from jma import fetch_city_warnings


def main():
    init_db()
    cleanup_old_logs()

    result = fetch_city_warnings()

    # systemdタイマーなどの自動実行で保存された行
    save_result(result, source="auto")


if __name__ == "__main__":
    main()