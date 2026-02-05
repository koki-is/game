import streamlit as st
import random
from openai import OpenAI
from streamlit_sortables import sort_items

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# プレイヤーごとのカラー（ご提示いただいたリストから各プレイヤーのメイン色を採用）
PLAYER_COLORS = ["#A6D8E4", "#A5BFE8", "#AEBFD3", "#FFB6C1", "#E5B4D6", "#FFC4B8"]

# --- スマホ・カードデザイン用の共通CSS ---
style_code = f"""
    <style>
    /* 共通ボタン設定 */
    .stButton > button {{
        width: 100%;
        height: 60px;
        font-size: 18px !important;
        border-radius: 12px !important;
        margin-top: 10px;
    }}
    
    /* 並べ替えカードの共通スタイル */
    .st-emotion-cache-12w0qpk {{
        padding: 0 !important;
    }}
    
    /* 各プレイヤーカードの色付け（ドラッグ項目用） */
    /* 注: モダンブラウザの :has セレクタを使用して中身のテキストで判定 */
    div[data-testid="stMarkdownContainer"]:has(p:contains("プレイヤー 1")) {{ background-color: {PLAYER_COLORS[0]}; border-radius: 10px; padding: 15px; color: black; font-weight: bold; }}
    div[data-testid="stMarkdownContainer"]:has(p:contains("プレイヤー 2")) {{ background-color: {PLAYER_COLORS[1]}; border-radius: 10px; padding: 15px; color: black; font-weight: bold; }}
    div[data-testid="stMarkdownContainer"]:has(p:contains("プレイヤー 3")) {{ background-color: {PLAYER_COLORS[2]}; border-radius: 10px; padding: 15px; color: black; font-weight: bold; }}
    div[data-testid="stMarkdownContainer"]:has(p:contains("プレイヤー 4")) {{ background-color: {PLAYER_COLORS[3]}; border-radius: 10px; padding: 15px; color: black; font-weight: bold; }}
    div[data-testid="stMarkdownContainer"]:has(p:contains("プレイヤー 5")) {{ background-color: {PLAYER_COLORS[4]}; border-radius: 10px; padding: 15px; color: black; font-weight: bold; }}
    div[data-testid="stMarkdownContainer"]:has(p:contains("プレイヤー 6")) {{ background-color: {PLAYER_COLORS[5]}; border-radius: 10px; padding: 15px; color: black; font-weight: bold; }}

    /* ドラッグ項目の高さを調整 */
    div[data-testid="stMarkdownContainer"] {{
        min-height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 8px;
    }}
    </style>
"""
st.markdown(style_code, unsafe_allow_html=True)

if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""

def generate_ito_theme(category):
    system_prompt = "あなたはボードゲーム『ito』のマスターです。主観によって評価が分かれる面白いお題を1つ生成してください。"
    user_prompt = f"カテゴリー「{category}」で、itoのお題を作成してください。形式：『お題：〇〇（1＝××、100＝△△）』"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.9
    )
    return response.choices[0].message.content

# --- 1. 設定フェーズ ---
if st.session_state.game_status == "setup":
    st.title("🃏 AI ito (Color Ver.)")
    num_players = st.slider("参加人数", 2, 6, 3)
    category = st.selectbox("ジャンル", ["人気・好感度", "強さ・能力", "日常・食べ物", "ロールプレイ"])
    
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
                <div style="background-color:{color}; padding:40px; border-radius:15px; text-align:center; border: 2px solid rgba(0,0,0,0.1);">
                    <h1 style="color:black; margin:0; font-size: 60px;">{st.session_state.numbers[i]}</h1>
                </div>
            """, unsafe_allow_html=True)

    if st.button("並べ替え（回答）へ進む"):
        st.session_state.game_status = "sorting"
        st.rerun()

# --- 3. 回答フェーズ（ドラッグ＆ドロップ） ---
elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替え")
    st.write("小さい順に上から並べてください（スマホは長押しで移動）")

    # 並べ替え用ラベル
    player_labels = [f"プレイヤー {i+1}" for i in range(len(st.session_state.numbers))]
    
    # ドラッグUIの表示
    sorted_labels = sort_items(player_labels, direction="vertical")

    if st.button("これで確定！"):
        final_numbers = []
        for label in sorted_labels:
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
            # 予想にもプレイヤーの色を反映
            orig_idx = st.session_state.numbers.index(val)
            color = PLAYER_COLORS[orig_idx]
            st.markdown(f'<div style="background-color:{color}; padding:10px; border-radius:5px; margin-bottom:5px; color:black; font-weight:bold;">{i}番目: {val}</div>', unsafe_allow_html=True)
            
    with col2:
        st.write("### 正解（小さい順）")
        for i, val in enumerate(correct_order, 1):
            st.write(f"**{i}番目**: {val}")

    if st.session_state.final_order == correct_order:
        st.balloons()
        st.success("完璧です！おめでとうございます！")
    else:
        st.error("残念！失敗です")

    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
