import streamlit as st
from dotenv import load_dotenv
import os
import openai

# 載入 .env 的金鑰
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit 頁面標題與副標
st.title("🤖 複利帥弟 FinBuddy")
st.subheader("幫你模擬投資報酬與複利回報")

# 使用者輸入
user_input = st.text_input("請輸入你的投資問題：", "")

# 有輸入時觸發 GPT-3.5 回應
if user_input:
    with st.spinner("FinBuddy 思考中..."):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # ✅ 免費額度可用模型
            messages=[
                {
                    "role": "system",
                    "content": "你是一位像朋友的專業理財顧問，擅長股票、房地產、虛擬貨幣等投資回報模擬，語氣輕鬆、比喻清楚，幫用戶生動理解的方式講解。"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        reply = response.choices[0].message.content
        st.success(reply)
