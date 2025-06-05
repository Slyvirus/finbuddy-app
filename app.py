import streamlit as st
from dotenv import load_dotenv
import os
import openai

# 載入 .env 金鑰
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit 標題區塊
st.title("🤖 複利帥弟 FinBuddy")
st.subheader("幫你模擬投資報酬與複利回報")

# 使用者輸入區
st.markdown("請輸入以下投資參數：")

monthly_investment = st.number_input(
    "每月投資金額（元）", min_value=0, value=10000, step=1000
)

annual_return_rate = st.number_input(
    "年報酬率（％）", min_value=0.0, max_value=100.0, value=5.0, step=0.1
)

years = st.number_input(
    "投資期間（年）", min_value=1, max_value=100, value=20, step=1
)

# 有輸入就送給 GPT 模擬分析
if st.button("送出模擬"):
    with st.spinner("FinBuddy 思考中..."):

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 使用免費額度模型
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位像朋友的專業理財顧問，擅長股票、房地產、虛擬貨幣等投資回報模擬，"
                        "語氣輕鬆、比喻清楚，會用深入淺出連高中生都能聽懂的方式，"
                        "幫用戶生動理解的方式講解跟舉例說明，也會提供明確的計算公式與思維鏈讓用戶驗算。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"我打算每月投入 {monthly_investment} 元，"
                        f"年報酬率 {annual_return_rate}%，時間為 {years} 年，"
                        "請幫我計算最終金額，並解釋計算過程。"
                    ),
                },
            ],
        )

        reply = response.choices[0].message.content
        st.success(reply)
