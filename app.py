import streamlit as st
import random
import os
from openai import OpenAI
from streamlit_sortables import sort_items

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏", layout="centered")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

PLAYER_COLORS = ["#A6D8E4", "#A5BFE8", "#AEBFD3", "#FFB6C1", "#E5B4D6", "#FFC4B8"]

# --- お題ファイルを読み込む関数 ---
def load_themes():
    if os.path.exists("themes.txt"):
        with open("themes.txt", "r", encoding="utf-8") as f:
            # 空行を除いてリスト化
            return [line.strip() for line in f.readlines() if line.strip()]
    return ["標準のお題 (1:低い - 100:高い)"] # ファイルがない場合の予備

# スタイルの注入（変更なし）
st.markdown(f"""
    <style>
    .stButton > button {{ width: 100%; height: 65px; font-size: 20px !important; border-radius: 15px !important; }}
    div[data-testid="stMarkdownContainer"] {{ background-color: transparent !important; }}
    div:has(> p:contains("プレイヤー")) {{
        width: 180px !important; height: 180px !important; min-height: 180px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        margin: 15px auto !important; border-radius: 20px !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important; border: 4px solid white !important;
        font-size: 26px !important; font-weight: 900 !important; color: #333 !important;
    }}
    div:has(> p:contains("プレイヤー 1")) {{ background-color: {PLAYER_COLORS[0]} !important; }}
    div:has(> p:contains("プレイヤー 2")) {{ background-color: {PLAYER_COLORS[1]} !important; }}
    div:has(> p:contains("プレイヤー 3")) {{ background-color: {PLAYER_COLORS[2]} !important; }}
    div:has(> p:contains("プレイヤー 4")) {{ background-color: {PLAYER_COLORS[3]} !important; }}
    div:has(> p:contains("プレイヤー 5")) {{ background-color: {PLAYER_COLORS[4]} !important; }}
    div:has(> p:contains("プレイヤー 6")) {{ background-color: {PLAYER_COLORS[5]} !important; }}
    .st-emotion-cache-12w0qpk {{ background-color: transparent !important; border: none !important; }}
    </style>
""", unsafe_allow_html=True)

if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""

# --- お題生成ロジックの改善 ---
def generate_ito_theme(category):
    # 手本となるお題を読み込む
    example_list = load_themes()
    examples_str = "\n".join(example_list)

    system_prompt = (
        "あなたはボードゲーム『ito』のマスターです。プレイヤーの価値観がズレて議論が盛り上がる、"
        "最高に面白いお題を生成してください。提供する『お手本』の質とユーモアを完全に模倣してください。"
    )
    user_prompt = (
        f"カテゴリー「{category}」に基づいた新しいお題を作成してください。\n\n"
        f"【お手本（この質を維持してください）】\n{examples_str}\n\n"
        "【ルール】\n"
        "- お手本にあるような具体的で、少し極端なシチュエーションにしてください。\n"
        "- 必ず『お題：〇〇（1＝××、100＝△△）』の形式で出力してください。"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o", # 質を重視する場合はgpt-4oを推奨
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.8
    )
    return response.choices[0].message.content

# --- 以下、ゲーム進行ロジック（変更なし） ---
if st.session_state.game_status == "setup":
    st.title("🃏 AI ito - High Quality Ver.")
    num_players = st.selectbox("参加人数", [2, 3, 4, 5, 6], index=1)
    category = st.selectbox("ジャンル", ["恋愛", "修学旅行", "異世界・ファンタジー", "日常・食べ物", "人生・価値観"])
    
    if st.button("ゲーム開始！"):
        st.session_state.numbers = random.sample(range(1, 101), num_players)
        with st.spinner("高品質なお題を生成中..."):
            st.session_state.theme = generate_ito_theme(category)
        st.session_state.game_status = "playing"
        st.rerun()

elif st.session_state.game_status == "playing":
    st.header(f"お題：\n{st.session_state.theme}")
    for i in range(len(st.session_state.numbers)):
        color = PLAYER_COLORS[i]
        with st.expander(f"👤 プレイヤー {i+1} の数字を確認"):
            st.markdown(f'<div style="background-color:{color}; padding:50px; border-radius:20px; text-align:center;"><h1 style="font-size: 80px;">{st.session_state.numbers[i]}</h1></div>', unsafe_allow_html=True)
    if st.button("回答（並べ替え）へ"):
        st.session_state.game_status = "sorting"
        st.rerun()

elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替え")
    labels = [f"プレイヤー {i+1}" for i in range(len(st.session_state.numbers))]
    sorted_labels = sort_items(labels, direction="vertical")
    if st.button("これで確定！"):
        st.session_state.final_order = [st.session_state.numbers[int(l.replace("プレイヤー ", ""))-1] for l in sorted_labels]
        st.session_state.game_status = "result"
        st.rerun()

elif st.session_state.game_status == "result":
    st.header("🎉 結果発表")
    st.subheader(st.session_state.theme)
    correct = sorted(st.session_state.numbers)
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 予想")
        for i, val in enumerate(st.session_state.final_order, 1):
            c = PLAYER_COLORS[st.session_state.numbers.index(val)]
            st.markdown(f'<div style="background-color:{c}; padding:10px; border-radius:10px; margin-bottom:10px; color:#333; font-weight:bold; text-align:center;">{i}番目: {val}</div>', unsafe_allow_html=True)
    with col2:
        st.write("### 正解")
        for i, val in enumerate(correct, 1):
            st.write(f"**{i}番目**: {val}")
    if st.session_state.final_order == correct:
        st.balloons(); st.success("成功！")
    else:
        st.error("失敗...")
    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"; st.rerun()
