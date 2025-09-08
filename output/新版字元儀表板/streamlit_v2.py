import streamlit as st
import pandas as pd
import altair as alt

# 1. 頁面設定 (Page Configuration)
# -----------------------------------------------------------------------------
# 使用 st.set_page_config() 來設定頁面標題、圖示和佈局。這必須是第一個執行的 Streamlit 命令。
st.set_page_config(
    page_title="字元儀表板 V2 - Streamlit 實作版",
    layout="wide"  # "wide" 佈局可以更好地利用螢幕空間
)


# 2. 自訂 CSS 樣式 (Custom CSS Injection)
# -----------------------------------------------------------------------------
# 為了達到 dashboard_v2.html 的視覺效果，我們需要注入自訂的 CSS。
# 這包括深色主題的背景色、進度條樣式等。
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 理想情況下，你會將CSS放在一個 .css 檔案中。為了方便展示，我們這裡直接使用 Markdown。
st.markdown("""
<style>
    /* 全域字體與背景色 */
    .stApp {
        background-color: #0f172a;
    }
    /* Streamlit元件的文字顏色 */
    .stApp, .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp .stMarkdown, .stApp .stDateInput > label, .stApp .stSelectbox > label {
        color: #cbd5e1; /* text-slate-300 */
    }
    /* 針對 progress bar 的樣式 */
    .progress-bar-bg {
        background-color: #334155; /* bg-slate-700 */
        border-radius: 9999px;
        height: 0.65rem;
        width: 100%;
    }
    .progress-bar-fill {
        background-color: #22d3ee; /* bg-cyan-400 */
        border-radius: 9999px;
        height: 100%;
    }
    .progress-bar-fill.green {
        background-color: #22c55e; /* bg-green-500 */
    }
</style>
""", unsafe_allow_html=True)


# 3. 儀表板內容 (Dashboard Content)
# -----------------------------------------------------------------------------

# --- 標題 ---
st.title("政府AI應用實驗站 測試(lab32)")
st.write("字元使用量監控儀表板")

# --- 日期篩選與環境資訊 ---
with st.expander("日期範圍設定與環境資訊"):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日期")
    with col2:
        end_date = st.date_input("結束日期")
    
    st.text("機關代碼: A123 | 機關名稱: 數位發展部 | 主機名稱: prod-server-01")


# --- (新) 三區字元額度總覽 ---
st.header("字元額度總覽")

# 這是實現客製化卡片的關鍵：使用 st.markdown 搭配 unsafe_allow_html=True
# 我們將 HTML 結構寫好，並用 Python 的 f-string 將動態數據填入。

# 模擬數據
quota_data = {
    "year1": {"used": 3500000, "total": 5000000, "reset_date": "115/1/1 (2026/1/1)", "color_class": ""},
    "year2": {"used": 500000, "total": 6000000, "reset_date": "116/1/1 (2027/1/1)", "color_class": "green"},
    "self_purchase": {"used": 1200000, "total": 2000000, "reset_date": "無歸零期限", "color_class": ""}
}

def create_quota_card(title, data):
    """一個輔助函數，用於生成單個額度卡的 HTML。"""
    used = data["used"]
    total = data["total"]
    remaining = total - used
    percentage = (used / total) * 100
    
    card_html = f"""
    <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 0.5rem; padding: 1.25rem; height: 100%; display: flex; flex-direction: column;">
        <h3 style="font-weight: 600; font-size: 1.125rem; color: white; margin-bottom: 1rem;">{title}</h3>
        <div style="margin-bottom: 1rem; font-size: 0.875rem; display: grid; gap: 0.75rem;">
            <div style="display: flex; justify-content: space-between;"><span>已使用</span><span style="font-weight: 500; color: white;">{used:,}</span></div>
            <div style="display: flex; justify-content: space-between;"><span>剩餘</span><span style="font-weight: 500; color: white;">{remaining:,}</span></div>
            <div style="display: flex; justify-content: space-between;"><span>總額度</span><span style="font-weight: 500; color: white;">{total:,}</span></div>
        </div>
        <div class="progress-bar-bg"><div class="progress-bar-fill {data['color_class']}" style="width: {percentage:.1f}%;"></div></div>
        <p style="text-align: right; font-size: 1.125rem; font-weight: 700; color: {'#34d399' if data['color_class'] else '#22d3ee'}; margin-top: 0.5rem; margin-bottom: 1rem;">{percentage:.1f}%</p>
        <div style="margin-top: auto; font-size: 0.75rem; color: #64748b; text-align: center; padding-top: 0.5rem; border-top: 1px solid #334155;">
            {data['reset_date']}
        </div>
    </div>
    """
    return card_html

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(create_quota_card("第一年度額度", quota_data["year1"]), unsafe_allow_html=True)
with col2:
    st.markdown(create_quota_card("第二年度額度 (含獎勵)", quota_data["year2"]), unsafe_allow_html=True)
with col3:
    st.markdown(create_quota_card("自購額度", quota_data["self_purchase"]), unsafe_allow_html=True)


# --- 使用量深度分析 ---
st.header("使用量深度分析")
source_option = st.selectbox(
    "數據來源:",
    ("總用量", "第一年度", "第二年度", "自購")
)

# --- 圖表與摘要 ---
left_column, right_column = st.columns([1, 2]) # 1:2 的比例佈局

with left_column:
    st.subheader("使用者排行榜")
    # 這裡可以用 st.bar_chart 或其他圖表庫 (Altair, Plotly)
    # 範例：使用 Altair 製作橫向長條圖
    user_data = pd.DataFrame({
        '使用者': ['王小明', '陳大文', '林美麗', '黃國倫', '張雅婷'],
        '使用字元數': [120000, 98000, 76000, 54000, 32000]
    })
    user_chart = alt.Chart(user_data).mark_bar().encode(
        x='使用字元數',
        y=alt.Y('使用者', sort='-x')
    ).properties(height=300)
    st.altair_chart(user_chart, use_container_width=True)

    st.subheader("AI Bots 使用量排行榜")
    st.bar_chart(pd.DataFrame({
        'AI Bot': ['文件摘要', '郵件草稿', '智能客服', '文章潤飾'],
        '使用量': [250000, 180000, 150000, 110000]
    }).set_index('AI Bot'))


with right_column:
    st.subheader("字元數使用量變化趨勢")
    # Streamlit 原生的 st.line_chart
    trend_data = pd.DataFrame({
        '日期': pd.to_datetime(['2025-09-01', '2025-09-02', '2025-09-03', '2025-09-04', '2025-09-05']),
        '每日使用字元數': [8500, 9200, 10500, 9800, 15000]
    }).set_index('日期')
    st.line_chart(trend_data)

    st.subheader("使用量統計摘要")
    # 使用 st.metric 來呈現統計數據
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("期間總用量", "5.2 M")
    m_col2.metric("期間平均日用量", "12,380")
    m_col3.metric("期間高峰日", "2025-09-05")

    st.info("""
    **分析結論**
    
    目前總體用量主要來自「第一年度額度」，已消耗70%，需開始注意用量。建議優先使用「第二年度額度」，目前尚有超過90%的餘裕。自購額度使用率為60%，可作為備援。
    """)
