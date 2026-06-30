from __future__ import annotations

import json
import os
import urllib.request
import urllib.error

LINE_NOTIFY_ENABLED = os.getenv("LINE_NOTIFY_ENABLED", "0").strip() == "1"
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
LINE_NOTIFY_TO = os.getenv("LINE_NOTIFY_TO", "").strip()
LINE_NOTIFY_PREFIX = os.getenv("LINE_NOTIFY_PREFIX", "【警報通知】").strip()


def _line_push(text: str) -> None:
    """LINE Messaging API push。失敗しても例外は飲み込む。"""
    if not LINE_NOTIFY_ENABLED:
        return
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_NOTIFY_TO:
        return

    tos = [t.strip() for t in LINE_NOTIFY_TO.split(",") if t.strip()]
    if not tos:
        return

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }

    for to in tos:
        body = {
            "to": to,
            "messages": [{"type": "text", "text": text}],
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if getattr(resp, "status", 200) >= 300:
                    print(f"[LINE] push failed status={resp.status}", flush=True)
        except urllib.error.HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            print(f"[LINE] HTTPError {e.code}: {e.reason} body={body_text}", flush=True)
        except Exception as e:
            print(f"[LINE] push exception: {e}", flush=True)


def notify_api_error(error: Exception) -> None:
    """APIの取得・パース失敗を通知する（エンドポイント変更など）。"""
    text = "\n".join([
        "【気象庁API異常】",
        "weather-warning: データ取得に失敗しました。",
        "APIのエンドポイントや構造が変更された可能性があります。",
        f"エラー: {str(error)[:200]}",
    ])
    _line_push(text)


def notify_unknown_codes(unknown_codes: list[str]) -> None:
    """不明コードが含まれている場合に通知する（コード体系変更など）。"""
    text = "\n".join([
        "【気象庁API異常】",
        "weather-warning: 不明な警報コードを受信しました。",
        "WARNING_NAMES の更新が必要な可能性があります。",
        f"不明コード: {', '.join(unknown_codes)}",
    ])
    _line_push(text)
