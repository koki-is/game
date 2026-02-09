import streamlit as st
import random
import os
import re
from openai import OpenAI
from streamlit_sortables import sort_items

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏", layout="centered")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# プレイヤーごとのカラー
PLAYER_COLORS = ["#A6D8E4", "#FFB6C1", "#B5EAD7", "#A5BFE8", "#FFF9C4", "#FFC4B8"]

def is_japanese(text):
    return re.fullmatch(r'[ぁ-んァ-ヶー一-龠]+', text) is not None

# --- スタイルの注入 ---
st.markdown(f"""
    <style>
    .stButton > button {{
        width: 100%;
        height: 65px;
        font-size: 20px !important;
        border-radius: 15px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""
    st.session_state.player_names = []
    st.session_state.theme_history = []

# --- 関数群 ---
def load_themes():
    if os.path.exists("themes.txt"):
        with open("themes.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return ["アニメ・漫画の人気（1:人気ない-100:人気ある）"]

def generate_ito_theme(history):
    example_list = load_themes()
    examples_str = "\n".join(example_list)
    history_str = ", ".join(history) if history else "なし"
    
    system_prompt = "あなたはボードゲーム『ito』のマスターです。プレイヤーが盛り上がるお題を作成してください。"
    user_prompt = (
        f"以下の『お手本』の質を参考に、ランダムなジャンルから新しいお題を1つだけ作成してください。\n\n"
        f"【お手本】\n{examples_str}\n\n"
        f"【禁止事項】\n"
        f"以下の「過去に出たお題」とは絶対に内容が被らないようにしてください。\n"
        f"過去に出たお題：{history_str}\n\n"
        "【ルール】\n- 形式は必ず『お題：〇〇（1＝××、100＝△△）』としてください。\n"
        "- 客観的な数値で測れるものは禁止です。"
    )
    response = client.chat.completions.create(
        model="gpt-4.1-nano", 
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.9
    )
    return response.choices[0].message.content

# リセット用のコールバック関数（ボタンが押された瞬間に実行される）
def reset_players_action():
    for i in range(6):
        key = f"pname_{i}"
        if key in st.session_state:
            st.session_state[key] = "" # 直接空文字をセットして入力をクリア
    st.session_state.player_names = []
    st.session_state.theme_history = []

# --- 1. 設定フェーズ ---
if st.session_state.game_status == "setup":
    st.title("🃏 AITO")
    
    current_num = len(st.session_state.player_names) if st.session_state.player_names else 3
    num_players = st.selectbox("参加人数を選んでください", [2, 3, 4, 5, 6], index=[2, 3, 4, 5, 6].index(max(2, current_num)))
    
    st.write("---")
    st.subheader("プレイヤー名を入力")

    new_names = []
    cols = st.columns(2)
    for i in range(num_players):
        default_name = st.session_state.player_names[i] if i < len(st.session_state.player_names) else ""
        with cols[i % 2]:
            name = st.text_input(f"プレイヤー {i+1}", value=default_name, key=f"pname_{i}", placeholder="なまえ")
            new_names.append(name)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("このメンバーで開始！"):
            error_msg = ""
            for n in new_names:
                if not n:
                    error_msg = "全員の名前を入力してください。"
                    break
                if not is_japanese(n):
                    error_msg = f"「{n}」に日本語以外の文字が含まれています。"
                    break
            
            # 重複チェック
            if not error_msg and len(new_names) != len(set(new_names)):
                error_msg = "同じ名前は使用できません。"
            
            if error_msg:
                st.error(error_msg)
            else:
                st.session_state.player_names = new_names
                st.session_state.numbers = random.sample(range(1, 101), num_players)
                with st.spinner("AIがお題を考えています..."):
                    new_theme = generate_ito_theme(st.session_state.theme_history)
                    st.session_state.theme = new_theme
                    st.session_state.theme_history.append(new_theme)
                st.session_state.game_status = "playing"
                st.rerun()
    
    with col_btn2:
        st.button("名前をリセット", on_click=reset_players_action)

# --- 2. プレイフェーズ ---
elif st.session_state.game_status == "playing":
    st.header(f"お題：\n{st.session_state.theme}")
    st.write("---")

    for i, name in enumerate(st.session_state.player_names):
        color = PLAYER_COLORS[i]
        with st.expander(f"👤 {name} さんの数字を確認"):
            st.markdown(f'<div style="background-color:{color}; padding:50px; border-radius:20px; text-align:center;"><h1 style="color:#333; margin:0; font-size: 80px;">{st.session_state.numbers[i]}</h1><p style="color:#333; font-weight:bold;">{name} の数字</p></div>', unsafe_allow_html=True)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("並べ替え（回答）へ進む"):
            st.session_state.game_status = "sorting"
            st.rerun()

    with col2:
        if st.button("🔄 お題を変える"):
            with st.spinner("AIが新しいお題を考えています..."):
                new_theme = generate_ito_theme(st.session_state.theme_history)
                st.session_state.theme = new_theme
                st.session_state.theme_history.append(new_theme)
                st.rerun()

# --- 3. 回答フェーズ ---
elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替え")
    sorted_labels = sort_items(st.session_state.player_names, direction="vertical")

    if st.button("これで確定！"):
        st.session_state.final_order = [st.session_state.numbers[st.session_state.player_names.index(label)] for label in sorted_labels]
        st.session_state.sorted_names_order = sorted_labels
        st.session_state.game_status = "result"
        st.rerun()

# --- 4. 結果発表フェーズ ---
elif st.session_state.game_status == "result":
    st.header("🎉 結果発表")
    st.subheader(f"{st.session_state.theme}")
    correct_order = sorted(st.session_state.numbers)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 予想")
        for i, name in enumerate(st.session_state.sorted_names_order):
            val = st.session_state.final_order[i]
            color = PLAYER_COLORS[st.session_state.player_names.index(name)]
            st.markdown(f'<div style="background-color:{color}; padding:15px; border-radius:10px; margin-bottom:10px; color:#333; font-weight:bold; text-align:center;">{i+1}: {name} ({val})</div>', unsafe_allow_html=True)
            
    with col2:
        st.write("### 正解")
        for i, val in enumerate(correct_order, 1):
            st.markdown(f'<div style="padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #ccc; text-align:center; font-weight:bold; color:#333;">{i}: {val}</div>', unsafe_allow_html=True)

    if st.session_state.final_order == correct_order:
        st.balloons(); st.success("おめでとう！成功😊")
    else:
        st.error("残念！失敗😢")

    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
