import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI

# 載入 .env 的金鑰
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=api_key)

# 標題與副標
st.title("🤖 複利帥弟 FinBuddy")
st.subheader("幫你模擬投資報酬與複利回報")

# 使用者輸入
user_input = st.text_input("請輸入你的投資問題：", "")

# 當使用者輸入文字並按下 Enter，就送給 GPT
if user_input:
    with st.spinner("FinBuddy 思考中..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一位像朋友的專業理財顧問，擅長股票、房地產、虛擬貨幣等投資回報模擬，語氣輕鬆、比喻清楚，幫用戶生動理解的方式講解。"},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
        st.success(reply)
