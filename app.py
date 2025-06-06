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

# === A6.2 單筆投入 vs 定期定額 模擬比較區段 ===
if st.button("送出模擬"):
    with st.spinner("FinBuddy 思考中..."):

        # 基本參數設定
        n = years * 12
        monthly_rate = annual_return_rate / 100 / 12

        # ✅ 定期定額模擬（每月投入 for 迴圈）
        dca_growth_value = 0
        dca_growth = []
        for _ in range(n):
            dca_growth_value = dca_growth_value * (1 + monthly_rate) + monthly_investment
            dca_growth.append(dca_growth_value)

        # ✅ 單筆投入模擬（同樣本金、年複利）
        total_principal = monthly_investment * 12 * years
        lump_sum = total_principal * (1 + annual_return_rate / 100) ** years

        # ✅ 差異比較
        diff = lump_sum - dca_growth_value

        # ✅ 條列顯示比較結果（不使用表格）
        st.markdown(f"""
        ### 💡 投資方式比較結果

        - 定期定額最終金額：約 NT$ {dca_growth_value:,.0f} 元  
        - 單筆投入（一次投入相同本金）最終金額：約 NT$ {lump_sum:,.0f} 元  
        - 總本金投入：NT$ {total_principal:,.0f} 元  
        - 單筆投入比定期定額多賺：約 NT$ {diff:,.0f} 元  
        """)

        # === 儲存歷史試算紀錄 ===
        st.session_state.history.append(
            f"每月投資：{monthly_investment} 元，年報酬率：{annual_return_rate}% ，年數：{years} 年 → 已完成試算"
        )

        # === 圖表繪製區（英文標示，保持與邏輯一致）===
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(range(1, n + 1), dca_growth, color="teal", linewidth=2, label="Dollar-Cost Averaging")
        ax.axhline(y=lump_sum, color="orange", linestyle="--", label="Lump-Sum Investment")
        ax.annotate(f"DCA Final\nNT$ {int(dca_growth_value):,}", xy=(n, dca_growth[-1]),
                    xytext=(n - 20, dca_growth[-1] * 1.05),
                    arrowprops=dict(facecolor='black', shrink=0.05), fontsize=10, color="black")
        ax.set_title("Investment Value Comparison")
        ax.set_xlabel("Month")
        ax.set_ylabel("Accumulated Value (TWD)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # === GPT 中文說明區 ===
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
