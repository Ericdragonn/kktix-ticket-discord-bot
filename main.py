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

    page_text = soup.get_text()

    # ✅ 第一優先：頁面顯示「沒有票」的警示文字
    if "目前沒有任何可以購買的票券" in page_text:
        return "sold_out"

    # ✅ 第二優先：頁面是否出現輸入票數的 input 欄位
    ticket_inputs = soup.select("span.ticket-quantity-input input")
    if ticket_inputs:
        return "available"

    # ✅ 第三優先：如果全部都是「已售完」的字眼，也推論為賣完
    sold_out_count = page_text.count("已售完")
    if sold_out_count >= 5:
        return "sold_out"

    # ❓如果以上皆未命中，保守視為「尚有票」
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
                send_discord(f"✅ @everyone【{name}】有票啦！快衝 👉 {url}")

            last_status[name] = status
        except Exception as e:
            print(f"[{name}] 發生錯誤：{e}")
    time.sleep(300)

