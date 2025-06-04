import streamlit as st
from dotenv import load_dotenv
import os
import openai

# 載入 .env 的金鑰
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 標題與副標
st.title("🤖 複利帥弟 FinBuddy")
st.subheader("幫你模擬投資報酬與複利回報")

# 使用者輸入欄
user_input = st.text_input("請輸入你的投資問題：", "")

# 當使用者輸入文字並按下 Enter，就發送給 GPT
if user_input:
    with st.spinner("FinBuddy 思考中..."):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 如果你要改成 GPT-4，這裡寫 gpt-4
            messages=[
                {"role": "system", "content": "你是FinBuddy，一位擅長ROI與複利模擬的理財小助手，口吻像朋友一樣親切，會用高中生聽得懂的方式說明。"},
                {"role": "user", "content": user_input}
            ]
        )
        st.success(response.choices[0].message["content"])

