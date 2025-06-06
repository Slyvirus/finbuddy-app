import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
import matplotlib.pyplot as plt
import matplotlib

# ✅ 中文顯示設定（fallback 字體組合）
matplotlib.rcParams['font.sans-serif'] = [
    'Taipei Sans TC Beta', 'SimHei', 'Noto Sans CJK TC',
    'Arial Unicode MS', 'DejaVu Sans'
]
matplotlib.rcParams['axes.unicode_minus'] = False

# === 載入金鑰 ===
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# === 頁面標題 ===
st.set_page_config(page_title="FinBuddy", layout="wide")
st.title("🤖 複利帥弟 FinBuddy")
st.subheader("幫你模擬投資報酬與複利回報")

# === 模式選單 ===
mode = st.selectbox("選擇模擬模式：", ["定期定額", "單筆投入"], index=0)

# === 使用者輸入 ===
monthly_investment = st.number_input("每月投資金額（元）", min_value=0, value=10000, step=1000)
annual_return_rate = st.number_input("年報酬率（%）", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
years = st.number_input("投資期間（年）", min_value=1, max_value=100, value=20)

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

        # === A6.2 單筆 vs 定期定額邏輯 ===
        n = years * 12
        monthly_rate = annual_return_rate / 100 / 12

        # ✅ 定期定額模擬（實際累積）
        total_dca = 0
        dca_growth = []
        for _ in range(n):
            total_dca = total_dca * (1 + monthly_rate) + monthly_investment
            dca_growth.append(total_dca)

        # ✅ 單筆投入模擬（用相同總本金試算）
        total_principal = monthly_investment * 12 * years
        lump_sum = total_principal * (1 + annual_return_rate / 100) ** years

        # ✅ 差異比較
        diff = lump_sum - total_dca

        # ✅ 條列呈現
        st.markdown(f"""
        ### 💡 投資方式比較結果
        - **定期定額最終金額**：約 NT${total_dca:,.0f} 元
        - **單筆投入（一次投入相同本金）最終金額**：約 NT${lump_sum:,.0f} 元
        - **總本金投入**：NT${total_principal:,.0f} 元
        - **單筆投入最後金額，比定期定額多賺**：約 NT${diff:,.0f} 元

        ✅ 根據你的設定，每月投入 NT${monthly_investment} 元，年報酬率 {annual_return_rate:.1f}%、投資 {years} 年後：

        1. 總投入本金為：NT${monthly_investment} × 12 × {years} = NT${total_principal:,.0f} 元
        2. 若採「定期定額」投資方式，預估資產可累積為：**NT${total_dca:,.0f} 元**
        3. 若為「一次性投入」相同本金並持有 20 年，預估資產可累積至：**NT${lump_sum:,.0f} 元**
        4. 若對照，單筆投入總報酬將比定期定額多賺：約 NT${diff:,.0f} 元 🔍 可考慮配置回報

        🧮 計算公式：FV = P × (1 + r)^t，其中 P 為投入本金、r 為年報酬率、t 為年數。
        """)

        # === 紀錄歷史 ===
        st.session_state.history.append(
            f"每月投資：{monthly_investment} 元，年報酬率：{annual_return_rate}% ，年數：{years} 年 → 已完成試算"
        )

      # === 圖表區（修正為英文字體） ===
fig, ax = plt.subplots(figsize=(8, 5))

# 設定英文字體
ax.set_title("Investment Value Comparison", fontname="DejaVu Sans")
ax.set_xlabel("Month", fontname="DejaVu Sans")
ax.set_ylabel("Accumulated Value (TWD)", fontname="DejaVu Sans")

# 畫出兩種投資曲線
ax.plot(range(1, n + 1), dca_growth, color="teal", linewidth=2, label="Dollar-Cost Averaging")
ax.axhline(y=lump_sum, color="orange", linestyle="--", label="Lump-Sum Investment")

# 加上定期定額終點註解
ax.annotate(
    f"DCA Final\n{int(total_dca):,} TWD",
    xy=(n, dca_growth[-1]),
    xytext=(n - 20, dca_growth[-1] * 1.05),
    arrowprops=dict(facecolor='black', shrink=0.05),
    fontsize=10,
    fontname="DejaVu Sans",
    color="black"
)

ax.grid(True)
ax.legend(prop={"family": "DejaVu Sans"})
st.pyplot(fig)


        # === GPT 中文解說 ===
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

