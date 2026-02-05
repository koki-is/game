import streamlit as st
import random
from openai import OpenAI
from streamlit_sortables import sort_items

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""

def generate_ito_theme(category):
    """学習したサイトの傾向を元に、質の高いitoのお題を生成"""
    
    # サイトから学習した「良いお題」の例をAIに提示
    examples = """
    - 恋人にしたい職業の人気 (1:人気ない - 100:人気ある)
    - ゾンビの世界で役立つ持ち物 (1:役に立たない - 100:超役立つ)
    - 魔王になって考えよう。こんな勇者は嫌だ (1:余裕 - 100:絶望的に嫌だ)
    - 言われたら嬉しい言葉 (1:どうでもいい - 100:最高に嬉しい)
    - 一生に一度はやってみたい奇跡の体験 (1:地味な奇跡 - 100:歴史に残る奇跡)
    - タイムトラベラーになって過去から持って帰りたいもの (1:いらない - 100:絶対持ち帰りたい)
    """

    system_prompt = (
        "あなたはボードゲーム『ito』のマスターです。以下の例のような、"
        "主観によって評価が分かれ、会話が盛り上がるお題を1つだけ生成してください。\n"
        f"【お題の例】\n{examples}"
    )
    
    user_prompt = (
        f"カテゴリー「{category}」に基づいた新しいお題を作成してください。\n"
        "【ルール】\n"
        "- 「1＝〇〇、100＝△△」という評価基準を必ず含めてください。\n"
        "- 身長や値段など、数字で正解が決まっている客観的なお題は禁止です。\n"
        "- 形式：『お題：〇〇（1＝××、100＝△△）』"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.9
    )
    return response.choices[0].message.content

# --- 1. 設定フェーズ ---
if st.session_state.game_status == "setup":
    st.title("🃏 AI ito (本格お題Ver.)")
    num_players = st.slider("参加人数", 2, 6, 3)
    category = st.selectbox("ジャンル", ["人気・好感度", "強さ・能力", "日常・食べ物", "人生・価値観", "ロールプレイ（魔王、修学旅行など）"])
    
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
        with st.expander(f"プレイヤー {i+1} の数字"):
            st.markdown(f"## {st.session_state.numbers[i]}")

    if st.button("並べ替え（回答）へ進む"):
        st.session_state.game_status = "sorting"
        st.rerun()

# --- 3. 回答フェーズ（ドラッグ＆ドロップ） ---
elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替え")
    st.write("小さい順（1に近い順）に上から並べてください。")

    player_labels = [f"プレイヤー {i+1}" for i in range(len(st.session_state.numbers))]
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
            st.write(f"{i}番目: **{val}**")
            
    with col2:
        st.write("### 正解（小さい順）")
        for i, val in enumerate(correct_order, 1):
            st.write(f"{i}番目: **{val}**")

    if st.session_state.final_order == correct_order:
        st.balloons()
        st.success("ナイス連携！脱出成功です！")
    else:
        st.error("残念！価値観のズレが発生しました。")

    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
