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
PLAYER_COLORS = ["#A6D8E4", "#A5BFE8", "#AEBFD3", "#FFB6C1", "#E5B4D6", "#FFC4B8"]

# 日本語チェック用関数（ひらがな、カタカナ、漢字のみ許可）
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
    /* カードのスタイル設定（名前表示に対応） */
    div:has(> p:contains("の数字")) {{
        width: 180px !important;
        height: 180px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 15px auto !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        border: 4px solid white !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        color: #333 !important;
    }}
    </style>
""", unsafe_allow_html=True)

if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""
    st.session_state.player_names = []

# --- themes.txt を読み込む ---
def load_themes():
    if os.path.exists("themes.txt"):
        with open("themes.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return ["アニメ・漫画の人気（1:人気ない-100:人気ある）"]

def generate_ito_theme():
    example_list = load_themes()
    examples_str = "\n".join(example_list)
    system_prompt = "あなたはボードゲーム『ito』のマスターです。プレイヤーが盛り上がるお題を作成してください。"
    user_prompt = (
        f"以下の『お手本』の質を参考に、ランダムなジャンルから新しいお題を1つだけ作成してください。\n\n"
        f"【お手本】\n{examples_str}\n\n"
        "【ルール】\n- 形式は必ず『お題：〇〇（1＝××、100＝△△）』としてください。\n"
        "- 客観的な数値で測れるものは禁止です。"
    )
    
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.9
    )
    return response.choices[0].message.content

# --- 1. 設定フェーズ ---
if st.session_state.game_status == "setup":
    st.title("🃏 AITO - 設定")
    
    num_players = st.selectbox("参加人数を選んでください", [2, 3, 4, 5, 6], index=1)
    
    st.write("---")
    st.subheader("プレイヤー名を入力してください（日本語のみ）")
    
    names = []
    cols = st.columns(2)
    for i in range(num_players):
        with cols[i % 2]:
            name = st.text_input(f"プレイヤー {i+1}", key=f"pname_{i}", placeholder="なまえ")
            names.append(name)

    if st.button("ゲーム開始！"):
        # バリデーションチェック
        error_msg = ""
        for i, n in enumerate(names):
            if not n:
                error_msg = "全員の名前を入力してください。"
                break
            if not is_japanese(n):
                error_msg = f"「{n}」に日本語以外の文字が含まれています。ひらがな・カタカナ・漢字で入力してください。"
                break
        
        if error_msg:
            st.error(error_msg)
        else:
            st.session_state.player_names = names
            st.session_state.numbers = random.sample(range(1, 101), num_players)
            with st.spinner("AIがお題を考えています..."):
                st.session_state.theme = generate_ito_theme()
            st.session_state.game_status = "playing"
            st.rerun()

# --- 2. プレイフェーズ ---
elif st.session_state.game_status == "playing":
    st.header(f"お題：\n{st.session_state.theme}")
    st.write("---")
    
    for i, name in enumerate(st.session_state.player_names):
        color = PLAYER_COLORS[i]
        with st.expander(f"👤 {name} さんの数字を確認"):
            st.markdown(f"""
                <div style="background-color:{color}; padding:50px; border-radius:20px; text-align:center;">
                    <h1 style="color:#333; margin:0; font-size: 80px;">{st.session_state.numbers[i]}</h1>
                    <p style="color:#333; font-weight:bold;">{name} の数字</p>
                </div>
            """, unsafe_allow_html=True)

    if st.button("並べ替え（回答）へ進む"):
        st.session_state.game_status = "sorting"
        st.rerun()

# --- 3. 回答フェーズ ---
elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替え")
    st.write("小さい順に上から並べてください。")

    sorted_labels = sort_items(st.session_state.player_names, direction="vertical")

    if st.button("これで確定！"):
        final_numbers = []
        for label in sorted_labels:
            idx = st.session_state.player_names.index(label)
            final_numbers.append(st.session_state.numbers[idx])
        
        st.session_state.final_order = final_numbers
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
        st.write("### あなたたちの予想")
        for i, val in enumerate(st.session_state.final_order, 1):
            name = st.session_state.sorted_names_order[i-1]
            orig_idx = st.session_state.player_names.index(name)
            color = PLAYER_COLORS[orig_idx]
            st.markdown(f'<div style="background-color:{color}; padding:15px; border-radius:10px; margin-bottom:10px; color:#333; font-weight:bold; text-align:center;">{i}番目: {name} ({val})</div>', unsafe_allow_html=True)
            
    with col2:
        st.write("### 正解")
        for i, val in enumerate(correct_order, 1):
            st.markdown(f'<div style="padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #ccc; text-align:center; font-weight:bold; color:#333;">{i}番目: {val}</div>', unsafe_allow_html=True)

    if st.session_state.final_order == correct_order:
        st.balloons(); st.success("おめでとう！成功😊")
    else:
        st.error("残念！失敗😢")

    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
