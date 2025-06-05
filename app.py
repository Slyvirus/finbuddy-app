import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI  # ✅ 新版 SDK

import matplotlib.pyplot as plt

# ✅ 英文字體設定，避免中文亂碼
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False  # 避免負號亂碼

# === 讀入 .env 的金鑰 ===
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# === Streamlit 頁面標題與副標題 ===
st.title("🤖 FinBuddy - Your Compound Growth Simulator")
st.subheader("Simulate your ROI based on monthly investment, return rate, and duration")
st.markdown("Please enter the following investment parameters:")

# === 使用者輸入區 ===
monthly_investment = st.number_input(
    "Monthly Investment (TWD)", min_value=0, value=10000, step=1000,
    help="The fixed amount you plan to invest monthly, in New Taiwan Dollars."
)

annual_return_rate = st.number_input(
    "Annual Return Rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1,
    help="The expected annual return rate (e.g., enter 5 for 5%)."
)

years = st.number_input(
    "Investment Duration (years)", min_value=1, max_value=100, value=20, step=1,
    help="Total duration you plan to invest (e.g., 20 years)."
)

# === 側邊欄：清除與歷史記錄 ===
st.sidebar.markdown("## 🛠️ Options")

if "history" not in st.session_state:
    st.session_state.history = []

if st.sidebar.button("🧹 Clear Inputs"):
    monthly_investment = 10000
    annual_return_rate = 5.0
    years = 20
    st.experimental_rerun()

st.sidebar.markdown("### 📒 Simulation History")
if st.session_state.history:
    for i, record in enumerate(reversed(st.session_state.history), 1):
        st.sidebar.markdown(f"**{i}.**\n\n{record}")
else:
    st.sidebar.caption("No records yet.")

# === 有輸入就送給 GPT 模擬分析 ===
if st.button("Submit Simulation"):
    with st.spinner("FinBuddy is thinking..."):

        # 儲存記錄
        st.session_state.history.append(
            f"Invest: {monthly_investment} TWD, Return Rate: {annual_return_rate}%, Duration: {years} years → Simulation done."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly financial advisor who explains investment returns "
                        "like compound interest, stocks, real estate, and crypto. Use clear logic, "
                        "conversational tone, vivid metaphors, and easy-to-understand steps with formulas and sanity checks."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"I plan to invest {monthly_investment} TWD per month for {years} years "
                        f"with an annual return rate of {annual_return_rate}%. "
                        f"Please calculate the final amount and explain the calculation logic."
                    ),
                },
            ],
        )

        reply = response.choices[0].message.content
        st.success(reply)

        # === 報酬率趨勢圖表 ===
        n = years * 12
        r = annual_return_rate / 100 / 12
        total = 0
        growth = []

        for i in range(1, n + 1):
            total = total * (1 + r) + monthly_investment
            growth.append(total)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(range(1, n + 1), growth, color="teal", linewidth=2, label="Cumulative Value")

        ax.annotate(f"Final: {int(total):,} TWD",
                    xy=(n, growth[-1]),
                    xytext=(n - 30, growth[-1] * 1.1),
                    arrowprops=dict(facecolor='black', shrink=0.05),
                    fontsize=10, color="black")

        ax.set_title("Investment Value Growth Over Time", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Accumulated Value (TWD)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)
