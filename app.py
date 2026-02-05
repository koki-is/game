import streamlit as st
import random
from openai import OpenAI
from streamlit_sortables import sort_items

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏", layout="centered")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# あなたが選んだプレイヤーカラー
PLAYER_COLORS = ["#A6D8E4", "#A5BFE8", "#AEBFD3", "#FFB6C1", "#E5B4D6", "#FFC4B8"]

# --- 【ここが肝】デフォルトスタイルを破壊して上書きするCSS ---
st.markdown(f"""
    <style>
    /* 1. ライブラリが作る「赤い枠」やデフォルト背景を透明化して無効にする */
    div[data-testid="stMarkdownContainer"] {{
        background-color: transparent !important;
    }}
    
    /* 2. ドラッグするカード全体の親要素の設定（正方形にするための土台） */
    .st-emotion-cache-12w0qpk {{
        background-color: transparent !important;
        border: none !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }}

    /* 3. 各プレイヤーカードの個別色設定（正方形デザイン） */
    /* セレクタを長くして優先順位を最大まで上げています */
    div[data-testid="stVerticalBlock"] > div:has(p:contains("プレイヤー 1")) {{ background-color: {PLAYER_COLORS[0]} !important; }}
    div[data-testid="stVerticalBlock"] > div:has(p:contains("プレイヤー 2")) {{ background-color: {PLAYER_COLORS[1]} !important; }}
    div[data-testid="stVerticalBlock"] > div:has(p:contains("プレイヤー 3")) {{ background-color: {PLAYER_COLORS[2]} !important; }}
    div[data-testid="stVerticalBlock"] > div:has(p:contains("プレイヤー 4")) {{ background-color: {PLAYER_COLORS[3]} !important; }}
    div[data-testid="stVerticalBlock"] > div:has(p:contains("プレイヤー 5")) {{ background-color: {PLAYER_COLORS[4]} !important; }}
    div[data-testid="stVerticalBlock"] > div:has(p:contains("プレイヤー 6")) {{ background-color: {PLAYER_COLORS[5]} !important; }}

    /* 4. カードの形状を「正方形」かつ「デカく」する */
    div:has(> p:contains("プレイヤー")) {{
        width: 180px !important;
        height: 180px !important;
        min-height: 180px !important;
        margin: 15px auto !important;
        border-radius: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #333 !important; /* 文字色は濃いグレーで視認性アップ */
        font-size: 24px !important;
        font-weight: 900 !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1) !important;
        border: 4px solid white !important; /* カード感が出る白枠 */
        cursor: grab !important;
    }}
    </style>
""", unsafe_allow_html=True)

# (以下、これまでのロジック部分は変更ありませんが、そのまま貼り付けられるよう整理しています)
if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""

def generate_ito_theme(category):
    prompt = f"ボードゲーム『ito』の「{category}」に関する主観的なお題を1つ。『お題：〇〇（1＝××、100＝△△）』形式で。"
    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    return res.choices[0].message.content

if st.session_state.game_status == "setup":
    st.title("🃏 AI ito - Color Card")
    num_p = st.selectbox("参加人数", [2, 3, 4, 5, 6], index=1)
    cate = st.selectbox("ジャンル", ["恋愛", "人気・好感度", "強さ・能力", "日常・食べ物", "人生・価値観"])
    if st.button("ゲーム開始！"):
        st.session_state.numbers = random.sample(range(1, 101), num_p)
        st.session_state.theme = generate_ito_theme(cate)
        st.session_state.game_status = "playing"
        st.rerun()

elif st.session_state.game_status == "playing":
    st.header(f"お題：\n{st.session_state.theme}")
    for i in range(len(st.session_state.numbers)):
        with st.expander(f"👤 プレイヤー {i+1} の数字を確認"):
            st.markdown(f'<div style="background-color:{PLAYER_COLORS[i]}; padding:40px; border-radius:20px; text-align:center;"><h1 style="font-size:80px; color:#333;">{st.session_state.numbers[i]}</h1></div>', unsafe_allow_html=True)
    if st.button("並べ替え（回答）へ"):
        st.session_state.game_status = "sorting"
        st.rerun()

elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替え")
    st.write("小さい順に上から並べてください。")
    labels = [f"プレイヤー {i+1}" for i in range(len(st.session_state.numbers))]
    sorted_labels = sort_items(labels, direction="vertical")
    if st.button("これで確定！"):
        st.session_state.final_order = [st.session_state.numbers[int(l.replace("プレイヤー ", ""))-1] for l in sorted_labels]
        st.session_state.game_status = "result"
        st.rerun()

elif st.session_state.game_status == "result":
    st.header("🎉 結果発表")
    st.write(f"お題：{st.session_state.theme}")
    correct = sorted(st.session_state.numbers)
    col1, col2 = st.columns(2)
    with col1:
        st.write("### あなたたちの予想")
        for i, val in enumerate(st.session_state.final_order, 1):
            c = PLAYER_COLORS[st.session_state.numbers.index(val)]
            st.markdown(f'<div style="background-color:{c}; padding:10px; border-radius:10px; margin-bottom:5px; text-align:center; color:#333; font-weight:bold;">{i}番目: {val}</div>', unsafe_allow_html=True)
    with col2:
        st.write("### 正解")
        for i, val in enumerate(correct, 1):
            st.write(f"**{i}番目**: {val}")
    if st.session_state.final_order == correct:
        st.balloons()
        st.success("大成功！")
    else:
        st.error("ズレ発生！")
    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
