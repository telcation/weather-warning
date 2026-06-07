from dotenv import load_dotenv
from db import init_db, save_result
from jma import fetch_city_warnings

load_dotenv()
init_db()
result = fetch_city_warnings()
save_result(result)
print(result["checked_at"], result["city_name"], [w["name"] for w in result["active_warnings"]])
