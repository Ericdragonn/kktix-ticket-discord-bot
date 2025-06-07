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

    # 嘗試尋找票數輸入欄位（若有 input 且沒 disabled，即為有票）
    ticket_blocks = soup.select("div.display-table")

    for block in ticket_blocks:
        # 檢查這塊是否含有 "已售完" 的字眼
        if "已售完" not in block.get_text():
            return "available"

    # 若全部都顯示已售完，則視為無票
    return "sold_out"


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
                send_discord(f"✅ @everyone【{name}】有票啦！快衝 👉 {url}")

            last_status[name] = status
        except Exception as e:
            print(f"[{name}] 發生錯誤：{e}")
    time.sleep(300)

