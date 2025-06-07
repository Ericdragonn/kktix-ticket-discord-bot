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

    # 優先判斷：是否存在票數輸入欄位（這是目前最可靠的無 JS 判斷方式）
    ticket_inputs = soup.select("span.ticket-quantity-input input")
    if ticket_inputs and len(ticket_inputs) = 0:
        return "available"

    # 備用判斷（從字面掃描頁面是否全為「已售完」）
    text = soup.get_text()
    sold_out_count = text.count("已售完")

    # 若找到超過 N 筆「已售完」可視為票種全賣完（你可微調數字）
    if sold_out_count >= 5:
        return "sold_out"

    # 預設保守視為「無票」
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

