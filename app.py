import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI  # ✅ 新版 SDK

# 載入 .env 的金鑰
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)  # ✅ 建立 client

# Streamlit 頁面標題與副標題
st.title("🤖 複利帥弟 FinBuddy")
st.subheader("幫你模擬投資報酬與複利回報")
st.markdown("請輸入以下投資參數：")

# ==== 使用者輸入區 ====
monthly_investment = st.number_input(
    "每月投資金額（元）", min_value=0, value=10000, step=1000,
    help="輸入預計在每個月固定投入的金額，單位為新台幣。"
)

annual_return_rate = st.number_input(
    "年報酬率（％）", min_value=0.0, max_value=100.0, value=5.0, step=0.1,
    help="輸入預估的年化報酬率（例如 5% 就輸入 5，非 0.05）。若不確定可以先用預設的大盤5%進行試算。"
)

years = st.number_input(
    "投資期間（年）", min_value=1, max_value=100, value=20, step=1,
    help="輸入計畫持續投入的總年數（例如 20 年）"
)

# ==== 側邊欄功能 ====
st.sidebar.markdown("# 🛠️ 操作選項")

# 初始化歷史紀錄
if "history" not in st.session_state:
    st.session_state.history = []

# 清除按鈕
if st.sidebar.button("🧹 清除輸入內容"):
    monthly_investment = 0
    annual_return_rate = 5.0
    years = 20
    st.experimental_rerun()

# 顯示歷史紀錄
st.sidebar.markdown("### 📒 歷史試算紀錄")
if st.session_state.history:
    for i, record in enumerate(reversed(st.session_state.history), 1):
        st.sidebar.markdown(f"**第 {i} 筆**\n\n{record}")
else:
    st.sidebar.caption("目前尚沒有試算紀錄")

# ==== 有輸入就送給 GPT 模擬分析 ====
if st.button("送出模擬"):
    with st.spinner("FinBuddy 思考中..."):

        # 紀錄輸入參數
        st.session_state.history.append(
            f"每月投資：{monthly_investment} 元，年報酬率：{annual_return_rate}% ，年數：{years} 年 → 結果：系統已完成試算"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # ✅ 使用免費額度模型
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
            ]
        )

        reply = response.choices[0].message.content
        st.success(reply)


# === 📈 報酬率趨勢圖表區塊 ===
import matplotlib.pyplot as plt

# 每月複利試算
n = years * 12
r = annual_return_rate / 100 / 12
total = 0
growth = []

for i in range(1, n + 1):
    total = total * (1 + r) + monthly_investment
    growth.append(total)

# 畫圖
fig, ax = plt.subplots()
ax.plot(range(1, n + 1), growth, color="teal")
ax.set_xlabel("投資期間（月）")
ax.set_ylabel("累積資產金額（元）")
ax.set_title("📈 投資累積金額趨勢圖")

# 顯示終點註記
final_amount = growth[-1]
ax.annotate(f"最終金額：{int(final_amount):,} 元",
            xy=(n, final_amount), xytext=(n * 0.7, final_amount * 0.8),
            arrowprops=dict(arrowstyle="->"))

st.pyplot(fig)
