import openai

# TODO：請將下方金鑰換成你自己的 OpenAI API Key
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print("👋 嗨，我是複利帥弟 FinBuddy！請問你想模擬哪一種投資方式？")
print("(1) 單筆投入模擬  (2) 定期定額模擬")
choice = input("請輸入 1 或 2：")

if choice == "1":
    principal = float(input("請輸入投入金額（例如 100000）："))
    rate = float(input("請輸入年報酬率（%）：")) / 100
    years = int(input("請輸入投資年數："))
    
    future_value = principal * (1 + rate) ** years

    prompt = f"我投資 {principal} 元，年報酬率假設 {rate*100:.2f}%，投資 {years} 年。請幫我用深入淺出的方式解釋這樣的複利效果，並提供觀察與提醒。"

elif choice == "2":
    monthly = float(input("請輸入每月投入金額（例如 5000）："))
    rate = float(input("請輸入年報酬率（%）：")) / 100
    years = int(input("請輸入投資年數："))
    
    months = years * 12
    monthly_rate = rate / 12
    future_value = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)

    prompt = f"我每月投入 {monthly} 元，年報酬率假設 {rate*100:.2f}%，投資 {years} 年。請幫我用深入淺出的方式解釋這樣的複利效果，並提供觀察與提醒。"

else:
    print("請輸入正確選項（1或2）")
    exit()

# 顯示計算結果
print(f"\n📈 模擬結果：最終金額約為 {future_value:,.0f} 元\n")

# 傳送給 GPT 並請他解釋
print("🤖 正在請 FinBuddy 幫你分析...\n")

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是一位像朋友的專業理財顧問，專長在股票、房地產、虛擬貨幣與複利投資，風格是深入淺出、比喻清楚，會大膽假設、小心求證，重視數據與風險。使用者可能會問還本型保單，你不會亂下結論，但會解釋概念並引導對方思考。請以繁體中文回答。"},
        {"role": "user", "content": prompt}
    ]
)

reply = response["choices"][0]["message"]["content"]
print("💬 FinBuddy 回覆：\n")
print(reply)
