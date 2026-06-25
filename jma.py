import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

JST = ZoneInfo("Asia/Tokyo")

PREF_CODE = "270000"
CITY_CODE = "2710000"
CITY_NAME = "大阪市"

TEST_DATA_FILE = Path.cwd() / "TestData.txt"

# 令和8年5月29日 新体系対応
WARNING_NAMES = {
    # レベルなし（従来通り）
    "14": "雷注意報",
    "15": "強風注意報",
    "16": "波浪注意報",
    "17": "波浪警報",
    "18": "濃霧注意報",
    "20": "乾燥注意報",
    "21": "なだれ注意報",
    "22": "低温注意報",
    "23": "霜注意報",
    "24": "着氷注意報",
    "25": "着雪注意報",
    "26": "融雪注意報",
    # レベル2注意報
    "10": "大雨注意報",
    "12": "大雪注意報",
    "13": "風雪注意報",
    "19": "高潮注意報",
    "29": "土砂災害注意報",
    "32": "洪水注意報",
    # レベル3警報
    "03": "大雨警報",
    "05": "暴風警報",
    "06": "暴風雪警報",
    "07": "大雪警報",
    "08": "高潮警報",
    "09": "土砂災害警報",
    # レベル4危険警報（令和8年新設）
    "43": "大雨危険警報",
    "44": "土砂災害危険警報",
    "45": "高潮危険警報",
    "48": "高潮危険警報",
    # レベル5特別警報
    "33": "大雨特別警報",
    "36": "大雪特別警報",
    "37": "波浪特別警報",
    "38": "高潮特別警報",
    "39": "土砂災害特別警報",
    "49": "氾濫特別警報",
}

ACTIVE_STATUSES = {"発表", "継続"}


def get_level(kind: dict) -> str | None:
    """kindsエントリからレベル番号を取得する。
    significancyPart.locals[].code の先頭1文字がレベル番号。
    例: "41" -> "4"、"21" -> "2"
    レベル情報がない種別（雷注意報等）はNoneを返す。
    """
    try:
        code = kind["properties"][0]["significancyPart"]["locals"][0]["code"]
        return code[0]
    except (KeyError, IndexError, TypeError):
        return None


def load_warning_data():
    if TEST_DATA_FILE.exists():
        with TEST_DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

    url = f"https://www.jma.go.jp/bosai/warning/data/r8/{PREF_CODE}.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_city_warnings():
    data = load_warning_data()

    # data はリスト。先頭要素（最新）を使う
    latest = data[0]

    for area in latest["warning"].get("class20Items", []):
        if area.get("areaCode") == CITY_CODE:
            warnings = []
            for kind in area.get("kinds", []):
                code = kind.get("code")
                status = kind.get("status")
                if status in ACTIVE_STATUSES:
                    warnings.append({
                        "name": WARNING_NAMES.get(code, f"不明コード:{code}"),
                        "level": get_level(kind),  # "2","3","4","5" or None
                    })
            return {
                "city_name": CITY_NAME,
                "checked_at": datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"),
                "warnings": warnings,
            }

    raise ValueError(f"{CITY_NAME}コード({CITY_CODE})が見つかりません")
