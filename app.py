import streamlit as st
import random
from openai import OpenAI
from streamlit_sortables import sort_items

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# プレイヤーごとのカラー（ご提示のリストから抽出した6色）
PLAYER_COLORS = ["#A6D8E4", "#A5BFE8", "#AEBFD3", "#FFB6C1", "#E5B4D6", "#FFC4B8"]

# --- スマホ・カードデザイン用のCSS（赤背景を完全に除去） ---
style_code = f"""
    <style>
    /* 基本ボタンの設定 */
    .stButton > button {{
        width: 100%;
        height: 60px;
        font-size: 18px !important;
        border-radius: 12px !important;
    }}
    
    /* 【最重要】ドラッグ＆ドロップ項目のスタイル書き換え */
    /* デフォルトの赤背景やスタイルを強制上書き */
    div[data-testid="stMarkdownContainer"] {{
        background-color: transparent !important;
    }}

    /* プレイヤーごとのカード色設定（1番目から6番目まで） */
    div:has(> p:contains("プレイヤー 1")) {{ background-color: {PLAYER_COLORS[0]} !important; }}
    div:has(> p:contains("プレイヤー 2")) {{ background-color: {PLAYER_COLORS[1]} !important; }}
    div:has(> p:contains("プレイヤー 3")) {{ background-color: {PLAYER_COLORS[2]} !important; }}
    div:has(> p:contains("プレイヤー 4")) {{ background-color: {PLAYER_COLORS[3]} !important; }}
    div:has(> p:contains("プレイヤー 5")) {{ background-color: {PLAYER_COLORS[4]} !important; }}
    div:has(> p:contains("プレイヤー 6")) {{ background-color: {PLAYER_COLORS[5]} !important; }}

    /* ドラッグカードの共通形状設定（正方形に近い大きなカード） */
    div:has(> p:contains("プレイヤー")) {{
        color: black !important;
        font-weight: bold !important;
        width: 90% !important;
        min-height: 120px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 10px auto !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        font-size: 22px !important;
        border: none !important;
    }}

    /* sortablesのデフォルト枠線を消す */
    .st-emotion-cache-12w0qpk {{
        background-color: transparent !important;
        border: none !important;
    }}
    </style>
"""
st.markdown(style_code, unsafe_allow_html=True)

if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""

def generate_ito_theme(category):
    system_prompt = "あなたはボードゲーム『ito』のマスターです。主観によって評価が分かれる、会話が弾む面白いお題を1つ生成してください。"
    user_prompt = f"カテゴリー「{category}」で、itoのお題を作成してください。\n形式：『お題：〇〇（1＝××、100＝△△）』"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.9
    )
    return response.choices[0].message.content

# --- 1. 設定フェーズ ---
if st.session_state.game_status == "setup":
    st.title("🃏 AI ito (Custom UI)")
    
    num_players = st.selectbox("参加人数", [2, 3, 4, 5, 6], index=1)
    category = st.selectbox("ジャンル", ["人気・好感度", "恋愛", "強さ・能力", "日常・食べ物", "人生・価値観"])
    
    if st.button("ゲーム開始！"):
        st.session_state.numbers = random.sample(range(1, 101), num_players)
        with st.spinner("AIがお題を生成中..."):
            st.session_state.theme = generate_ito_theme(category)
        st.session_state.game_status = "playing"
        st.rerun()

# --- 2. プレイフェーズ ---
elif st.session_state.game_status == "playing":
    st.header(f"お題：\n{st.session_state.theme}")
    st.write("---")
    
    for i in range(len(st.session_state.numbers)):
        color = PLAYER_COLORS[i]
        with st.expander(f"👤 プレイヤー {i+1} の数字を確認"):
            st.markdown(f"""
                <div style="background-color:{color}; padding:50px; border-radius:20px; text-align:center; border: 2px solid rgba(0,0,0,0.1);">
                    <h1 style="color:black; margin:0; font-size: 80px;">{st.session_state.numbers[i]}</h1>
                </div>
            """, unsafe_allow_html=True)

    if st.button("並べ替え（回答）へ進む"):
        st.session_state.game_status = "sorting"
        st.rerun()

# --- 3. 回答フェーズ（ドラッグ＆ドロップ） ---
elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替え")
    st.write("小さい順に上から並べてください。")

    # 並べ替え用ラベル
    player_labels = [f"プレイヤー {i+1}" for i in range(len(st.session_state.numbers))]
    
    # 改良されたドラッグUI
    sorted_labels = sort_items(player_labels, direction="vertical")

    if st.button("これで確定！"):
        final_numbers = []
        for label in sorted_labels:
            # ラベルからプレイヤー番号を抽出
            idx = int(label.replace("プレイヤー ", "")) - 1
            final_numbers.append(st.session_state.numbers[idx])
        st.session_state.final_order = final_numbers
        st.session_state.game_status = "result"
        st.rerun()

# --- 4. 結果発表フェーズ ---
elif st.session_state.game_status == "result":
    st.header("🎉 結果発表")
    st.subheader(f"{st.session_state.theme}")
    correct_order = sorted(st.session_state.numbers)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### あなたたちの予想")
        for i, val in enumerate(st.session_state.final_order, 1):
            orig_idx = st.session_state.numbers.index(val)
            color = PLAYER_COLORS[orig_idx]
            st.markdown(f'<div style="background-color:{color}; padding:15px; border-radius:10px; margin-bottom:10px; color:black; font-weight:bold; text-align:center;">{i}番目: {val}</div>', unsafe_allow_html=True)
            
    with col2:
        st.write("### 正解（小さい順）")
        for i, val in enumerate(correct_order, 1):
            st.markdown(f'<div style="padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #ccc; text-align:center;">{i}番目: **{val}**</div>', unsafe_allow_html=True)

    if st.session_state.final_order == correct_order:
        st.balloons()
        st.success("完璧です！おめでとうございます！")
    else:
        st.error("残念！価値観のズレが発生しました。")

    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
