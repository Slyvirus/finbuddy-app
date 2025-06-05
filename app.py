import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI

import matplotlib.pyplot as plt
import matplotlib

# ✅ 避免中文亂碼
matplotlib.rcParams['font.sans-serif'] = [
    'Taipei Sans TC Beta', 'SimHei', 'Noto Sans CJK TC',
    'Arial Unicode MS', 'DejaVu Sans'
]
matplotlib.rcParams['axes.unicode_minus'] = False

# === 載入 API 金鑰 ===
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# === 頁面設定 ===
st.set_page_config(page_title="FinBuddy", layout="wide")
st.title("🤖 複利帥弟 FinBuddy")
st.subheader("幫你模擬投資報酬與複利回報")

# === 使用者輸入 ===
monthly_investment = st.number_input(
    "每月投資金額（元）", min_value=0, value=10000, step=1000,
    help="輸入預計在每個月固定投入的金額，單位為新台幣。"
)
annual_return_rate = st.number_input(
    "年報酬率（%）", min_value=0.0, max_value=100.0, value=5.0, step=0.1,
    help="輸入預估的年化報酬率（例如 5% 就輸入 5，非 0.05）。若不確定可以先用預設的大盤5%試算。"
)
years = st.number_input(
    "投資期間（年）", min_value=1, max_value=100, value=20, step=1,
    help="輸入計畫持續投入的總年數（例如 20 年）"
)

# === 側邊欄 ===
st.sidebar.markdown("# 🛠 操作選項")
if "history" not in st.session_state:
    st.session_state.history = []

if st.sidebar.button("🧹 清除輸入內容"):
    monthly_investment = 10000
    annual_return_rate = 5.0
    years = 20
    st.experimental_rerun()

st.sidebar.markdown("### 📒 歷史試算紀錄")
if st.session_state.history:
    for i, record in enumerate(reversed(st.session_state.history), 1):
        st.sidebar.markdown(f"**第 {i} 筆**\n\n{record}")
else:
    st.sidebar.caption("目前尚沒有試算紀錄")

# === 模擬區塊 ===
if st.button("送出模擬"):
    with st.spinner("FinBuddy 思考中..."):

        # ✅ GPT 中文回應
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

        reply = response.choices[0].message.content
        st.session_state.history.append(
            f"每月投資：{monthly_investment} 元，年報酬率：{annual_return_rate}% ，年數：{years} 年 → 已完成試算"
        )

        # ✅ 複利計算邏輯
        n = years * 12
        r = annual_return_rate / 100 / 12
        total = 0
        growth = []
        for i in range(1, n + 1):
            total = total * (1 + r) + monthly_investment
            growth.append(total)

        # ✅ 顯示計算結果
        st.markdown(
            f"""
            <div style="background-color:#e0f7fa;padding:15px;border-radius:10px">
            <h3 style="color:#00796b;">📈 定期定額投資總金額：約 <span style="color:#d32f2f;">{int(total):,} 元</span></h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ✅ 顯示 GPT 解釋
        st.success(reply)

        # ✅ 圖表繪製
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(range(1, n + 1), growth, color="#1976D2", linewidth=2.5, label="Cumulative Value")

        ax.annotate(f"Final: {int(total):,} TWD", xy=(n, growth[-1]),
                    xytext=(n - 30, growth[-1] * 1.05),
                    arrowprops=dict(facecolor='gray', arrowstyle='->'),
                    fontsize=10, color="black")

        ax.set_title("Investment Value Growth Over Time")
        ax.set_xlabel("Month")
        ax.set_ylabel("Accumulated Value (TWD)")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)

        st.pyplot(fig)

