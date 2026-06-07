from db import init_db, save_result, cleanup_old_logs
from jma import fetch_city_warnings

def main():
    init_db()
    cleanup_old_logs()
    result = fetch_city_warnings()
    save_result(result)

if __name__ == "__main__":
    main()