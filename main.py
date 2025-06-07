
import requests
from bs4 import BeautifulSoup
import time
import os

# 從環境變數讀取 Webhook 和網址列表
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# 多個活動網址，可透過環境變數設定（TARGET_URL_1, TARGET_URL_2, ...）
URLS = {}
for key, value in os.environ.items():
    if key.startswith("TARGET_URL_"):
        URLS[key] = value

print("✅ 環境變數網址：", URLS)

# 狀態紀錄避免重複通知
last_status = {k: "unknown" for k in URLS}

def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

def check_availability(name, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    ticket_inputs = soup.select("span.ticket-quantity-input input")
    if ticket_inputs:
        return "available"

    if "目前沒有任何可以購買的票券" in soup.get_text():
        return "sold_out"

    sold_out_count = soup.get_text().count("已售完")
    if sold_out_count > 5:
        return "sold_out"

    return "available"

while True:
    print("▶ 正在檢查票務狀態...")
    for name, url in URLS.items():
        try:
            status = check_availability(name, url)
            print(f"🎫 {name}：{status}")

            if last_status[name] != "available" and status == "available":
                send_discord(f"✅【{name}】有票了！快搶 👉 {url}")

            last_status[name] = status
        except Exception as e:
            print(f"[{name}] 發生錯誤：{e}")
    time.sleep(300)
