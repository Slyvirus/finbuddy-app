# app.py

import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
import matplotlib.pyplot as plt
import matplotlib

# ✅ 設定圖表為英文（防止中文亂碼）
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

# === 載入環境變數 ===
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# === 頁面設定 ===
st.set_page_config(page_title="FinBuddy", layout="wide")
st.title("🤖 複利帥弟 FinBuddy")
st.subheader("幫你模擬投資報酬與複利回報")

# === 模式選單（中文）===
mode = st.selectbox("選擇模擬模式：", ["定期定額", "單筆投入"], index=0)

# === 輸入欄位 ===
monthly_investment = st.number_input("每月投資金額（元）", min_value=0, value=10000, step=1000)
annual_return_rate = st.number_input("年報酬率（%）", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
years = st.number_input("投資期間（年）", min_value=1, max_value=100, value=20, step=1)

# === 清除按鈕 & 歷史區塊 ===
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

# === 試算主體 ===
if st.button("送出模擬"):
    with st.spinner("FinBuddy 思考中..."):
        # 參數設定
        n = years * 12
        monthly_rate = annual_return_rate / 100 / 12

        # 定期定額計算
        total_dca = 0
        dca_growth = []
        for _ in range(n):
            total_dca = total_dca * (1 + monthly_rate) + monthly_investment
            dca_growth.append(total_dca)

        # 單筆投入
        total_principal = monthly_investment * 12 * years
        lump_sum = total_principal * (1 + annual_return_rate / 100) ** years

        diff = lump_sum - total_dca

        # 顯示摘要比較結果
        st.markdown(f"""
        ### 💡 投資方式比較結果
        - **定期定額最終總金額**：約 NT${total_dca:,.0f} 元
        - **單筆投入（一次投入相同本金）最終金額**：約 NT${lump_sum:,.0f} 元
        - **總投入本金**：NT${total_principal:,.0f} 元
        - **單筆投入最終金額比定期定額多賺**：約 NT${diff:,.0f} 元
        """)

        st.markdown(f"""
        📌 根據你的設定，每月投入 NT${monthly_investment:,} 元、年報酬率 {annual_return_rate:.1f}%、投資 {years} 年後：

        1. 總投入本金為：NT${monthly_investment} × 12 × {years} = NT${total_principal:,.0f} 元  
        2. 若採「定期定額」投資方式，預估資產可累積為：約 NT${total_dca:,.0f} 元  
        3. 若改為「一次性投入」相同本金並持有 {years} 年，預估資產可累積至：約 NT${lump_sum:,.0f} 元  
        4. 兩者相較，單筆投入獲得的預估報酬，多出約 NT${diff:,.0f} 元於同樣期間  

        🧠 計算公式：FV = P × (1 + r)^t，其中 P 為投入本金、r 為年報酬率、t 為年數。
        ⚠️ 本模擬僅為參考用途，實際報酬可能受市場波動與風險影響。
        """)

        # === 繪製圖表 ===
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(range(1, n + 1), dca_growth, color="teal", linewidth=2, label="Dollar-Cost Averaging")
        ax.axhline(y=lump_sum, color="orange", linestyle="--", label="Lump-Sum Investment")
        ax.annotate(f"DCA Final\nNT${int(total_dca):,}", xy=(n, dca_growth[-1]),
                    xytext=(n - 20, dca_growth[-1] * 1.05),
                    arrowprops=dict(facecolor='black', shrink=0.05),
                    fontsize=10, color="black")
        ax.set_title("Investment Value Comparison")
        ax.set_xlabel("Month")
        ax.set_ylabel("Accumulated Value (TWD)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # === 補充 GPT 中文說明（保留 AI 溫度）===
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

        st.session_state.history.append(
            f"每月投資：{monthly_investment} 元，年報酬率：{annual_return_rate}% ，年數：{years} 年 → 已完成試算"
        )
