import requests
from bs4 import BeautifulSoup
import time
import os

# 從環境變數手動取網址，並給它們「清楚的名字」
URLS = {
    "演唱會1": os.environ.get("TARGET_URL_1"),
    "演唱會2": os.environ.get("TARGET_URL_2")
}
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

print("✅ 環境變數網址：", URLS)

# 避免重複通知
last_status = {k: "unknown" for k in URLS}

def send_discord(msg):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg})
    else:
        print("⚠️ 未設定 WEBHOOK_URL")

def check_availability(name, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False)
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
        if not url:
            print(f"❌ 跳過 {name}（未提供網址）")
            continue

        try:
            status = check_availability(name, url)
            print(f"🎫 {name}：{status}")

            if last_status[name] != "available" and status == "available":
                send_discord(f"✅【{name}】有票啦！快衝 👉 {url}")

            last_status[name] = status
        except Exception as e:
            print(f"[{name}] 發生錯誤：{e}")
    time.sleep(300)

