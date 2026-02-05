import streamlit as st
import random
from openai import OpenAI
from streamlit_sortables import sort_items # 新しいライブラリ

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = [] # [数字1, 数字2, ...]
    st.session_state.theme = ""

# --- 1. 設定フェーズ ---
if st.session_state.game_status == "setup":
    st.title("🃏 AI ito")
    num_players = st.slider("参加人数", 2, 6, 3)
    category = st.selectbox("お題のジャンル", ["日常・食べ物", "ファンタジー", "恋愛", "シュール"])
    
    if st.button("ゲーム開始！"):
        st.session_state.numbers = random.sample(range(1, 101), num_players)
        prompt = f"ボードゲーム『ito』の「{category}」に関するお題を1つ。1=最悪、100=最高として『お題：〇〇』の形式で。"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        st.session_state.theme = response.choices[0].message.content
        st.session_state.game_status = "playing"
        st.rerun()

# --- 2. プレイフェーズ（数字確認） ---
elif st.session_state.game_status == "playing":
    st.header(f"お題：\n{st.session_state.theme}")
    st.info("自分の番号を確認してください。確認後、相談タイム！")
    
    for i in range(len(st.session_state.numbers)):
        with st.expander(f"プレイヤー {i+1} の数字"):
            st.markdown(f"## {st.session_state.numbers[i]}")

    if st.button("並べ替え（回答）へ進む"):
        st.session_state.game_status = "sorting"
        st.rerun()

# --- 3. 回答フェーズ（ドラッグ＆ドロップ） ---
elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替えよう")
    st.write("小さいと思う順に上からドラッグして並べてください（スマホは長押し）")

    # 並べ替え用のリストを作成（表示用）
    player_labels = [f"プレイヤー {i+1}" for i in range(len(st.session_state.numbers))]
    
    # ドラッグ＆ドロップ UI
    sorted_labels = sort_items(player_labels, direction="vertical")

    if st.button("これで確定！"):
        # 並べ替えられた結果を元に、実際の数字のリストを作る
        # 例：['プレイヤー2', 'プレイヤー1'] -> [数字2, 数字1]
        final_numbers = []
        for label in sorted_labels:
            index = int(label.split(" ")[1]) - 1
            final_numbers.append(st.session_state.numbers[index])
        
        st.session_state.final_order = final_numbers
        st.session_state.game_status = "result"
        st.rerun()

# --- 4. 結果発表 ---
elif st.session_state.game_status == "result":
    st.header("🎉 結果発表")
    
    # 正解（昇順）
    correct_order = sorted(st.session_state.numbers)
    
    st.write("あなたの並び:", st.session_state.final_order)
    st.write("正解（小さい順）:", correct_order)

    if st.session_state.final_order == correct_order:
        st.balloons()
        st.success("完璧！脱出成功です！")
    else:
        st.error("残念！順番が違いました。")

    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
