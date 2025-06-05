import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI

import matplotlib.pyplot as plt
import matplotlib

# ✅ 字體設定：避免亂碼
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# === 載入金鑰 ===
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# === 頁面設定 ===
st.set_page_config(page_title="FinBuddy", layout="wide")
st.title("🤖 FinBuddy - Investment ROI Simulator")
st.subheader("Simulate investment growth with compounding interest")

# === 模式選擇（預設為定期定額）===
mode = st.selectbox("Choose investment mode:", ["DCA (Monthly Investment)", "Lump Sum Investment"], index=0)

# === 輸入區 ===
monthly_investment = st.number_input(
    "Monthly Investment (TWD)", min_value=0, value=10000, step=1000,
    help="Enter the fixed amount you plan to invest each month."
)
annual_return_rate = st.number_input(
    "Annual Return Rate (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1,
    help="Enter the estimated annual return rate (e.g., enter 5 for 5%)."
)
years = st.number_input(
    "Investment Period (Years)", min_value=1, max_value=100, value=20, step=1,
    help="Enter the total number of years you plan to invest."
)

# === 側邊欄功能 ===
st.sidebar.markdown("# 🛠 Options")
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
        st.sidebar.markdown(f"**#{i}**\n\n{record}")
else:
    st.sidebar.caption("No simulations yet.")

# === 模擬區 ===
if st.button("Run Simulation"):
    with st.spinner("FinBuddy is thinking..."):

        n = years * 12
        r = annual_return_rate / 100 / 12

        # DCA 模擬
        total_dca = 0
        dca_growth = []
        for _ in range(n):
            total_dca = total_dca * (1 + r) + monthly_investment
            dca_growth.append(total_dca)

        # Lump Sum 模擬
        lump_sum = monthly_investment * n * (1 + r) ** n
        diff = total_dca - lump_sum

        # 結果摘要
        st.markdown(f"""
        ### 💰 **Result Summary**
        - **DCA Final Amount**: ${total_dca:,.0f}
        - **Lump Sum Final Amount**: ${lump_sum:,.0f}
        - 📌 **DCA earns more by**: ${diff:,.0f}
        """)

        # 紀錄
        st.session_state.history.append(
            f"Monthly: {monthly_investment}, Rate: {annual_return_rate}%, Years: {years} → Done"
        )

        # 圖表
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(range(1, n + 1), dca_growth, color="teal", linewidth=2, label="DCA")
        ax.axhline(y=lump_sum, color="orange", linestyle="--", label="Lump Sum")
        ax.annotate(f"DCA\n${int(total_dca):,}", xy=(n, dca_growth[-1]),
                    xytext=(n - 20, dca_growth[-1] * 1.05),
                    arrowprops=dict(facecolor='black', shrink=0.05), fontsize=10, color="black")
        ax.set_title("Investment Value Over Time")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Value (TWD)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # GPT 中文回應
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位像朋友的專業理財顧問，擅長解釋股票、房地產、虛擬貨幣等投資回報模擬。"
                        "請用輕鬆、清楚、有條理的方式回應。使用繁體中文講解，語氣親切，邏輯分明，"
                        "並提供清楚的計算步驟、複利公式與驗算思維，讓高中生也能理解。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"我每月投資 {monthly_investment} 元，年報酬率 {annual_return_rate}%、投入 {years} 年，"
                        "請幫我計算定期定額的最終金額，並以清楚條列的方式解釋計算過程。"
                    ),
                },
            ],
        )
        st.success(response.choices[0].message.content)
