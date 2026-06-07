import requests
from datetime import datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")

PREF_CODE = "270000"
CITY_CODE = "2710000"
CITY_NAME = "大阪市"

WARNING_NAMES = {
    "03": "大雨警報",
    "04": "洪水警報",
    "05": "暴風警報",
    "06": "暴風雪警報",
    "07": "大雪警報",
    "10": "大雨注意報",
    "12": "大雪注意報",
    "13": "風雪注意報",
    "14": "雷注意報",
    "15": "強風注意報",
    "16": "波浪注意報",
    "18": "濃霧注意報",
    "20": "乾燥注意報",
    "21": "なだれ注意報",
    "22": "低温注意報",
    "23": "霜注意報",
    "24": "着氷注意報",
    "25": "着雪注意報",
    "26": "融雪注意報",
    "32": "洪水注意報",
}

ACTIVE_STATUSES = {"発表", "継続"}


def fetch_city_warnings():
    url = f"https://www.jma.go.jp/bosai/warning/data/warning/{PREF_CODE}.json"

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    for area_type in data.get("areaTypes", []):
        for area in area_type.get("areas", []):
            if area.get("code") == CITY_CODE:
                warnings = []

                for warning in area.get("warnings", []):
                    code = warning.get("code")
                    status = warning.get("status")

                    if status in ACTIVE_STATUSES:
                        warnings.append(
                            WARNING_NAMES.get(code, f"不明コード:{code}")
                        )

                return {
                    "city_name": CITY_NAME,
                    "checked_at": datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"),
                    "warnings": warnings,
                }

    raise ValueError(f"{CITY_NAME}コード({CITY_CODE})が見つかりません")