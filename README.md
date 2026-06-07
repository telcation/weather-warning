# 大阪市 警報・注意報 Webアプリ

## ローカル実行

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env
python app.py
```

ブラウザで http://127.0.0.1:5010/ を開きます。

## サーバー初回設定

```bash
sudo mkdir -p /var/www/weather-warning-app
sudo chown -R $USER:$USER /var/www/weather-warning-app
```

リポジトリを配置後：

```bash
cd /var/www/weather-warning-app
cp .env.example .env
sudo bash scripts/install_server.sh
sudo cp systemd-weather-warning-web.service /etc/systemd/system/weather-warning-web.service
sudo cp systemd-weather-warning-fetch.service /etc/systemd/system/weather-warning-fetch.service
sudo cp systemd-weather-warning-fetch.timer /etc/systemd/system/weather-warning-fetch.timer
sudo systemctl daemon-reload
sudo systemctl enable --now weather-warning-web.service
sudo systemctl enable --now weather-warning-fetch.timer
```

Nginx設定例は `nginx-weather-warning.conf` を `telcation.com` の server ブロック内に追加します。

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## GitHub Secrets

- SERVER_HOST
- SERVER_USER
- SERVER_SSH_KEY
