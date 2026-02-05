import streamlit as st
import random
from openai import OpenAI

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# セッション状態の初期化
if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""

def generate_theme(category):
    """OpenAIにお題を生成させる関数"""
    prompt = (
        f"ボードゲーム『ito』のお題を1つ考えてください。\n"
        f"カテゴリーは「{category}」にしてください。\n"
        f"1から100の数字がそれぞれ何を表すか（例：1が最弱、100が最強）を明確にし、\n"
        f"『お題：〇〇（1＝××、100＝△△）』という形式で短く答えてください。"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

st.title("🃏 AI ito (イト)")

# --- 1. 設定フェーズ ---
if st.session_state.game_status == "setup":
    num_players = st.slider("参加人数", 2, 6, 3)
    category = st.selectbox("お題のジャンル", ["日常・食べ物", "ファンタジー・魔法", "恋愛・人間関係", "シュール・難しい"])
    
    if st.button("ゲーム開始＆お題生成"):
        # 1〜100から数字をランダムに配布
        st.session_state.numbers = random.sample(range(1, 101), num_players)
        # OpenAIでお題を生成
        with st.spinner("AIがお題を考えています..."):
            st.session_state.theme = generate_theme(category)
        st.session_state.game_status = "playing"
        st.rerun()

# --- 2. プレイフェーズ ---
elif st.session_state.game_status == "playing":
    st.header(f"今回のお題：\n{st.session_state.theme}")
    
    if st.button("別のお題にする（AIで再生成）"):
        st.session_state.theme = generate_theme("ランダム")
        st.rerun()
    
    st.write("---")
    for i, num in enumerate(st.session_state.numbers):
        with st.expander(f"プレイヤー {i+1} の数字を見る"):
            st.markdown(f"## あなたの数字は **{num}** です")
    
    if st.button("全員出し終わった（結果発表）"):
        st.session_state.game_status = "result"
        st.rerun()

# --- 3. 結果発表フェーズ ---
elif st.session_state.game_status == "result":
    st.header("🎉 結果発表")
    st.write(f"お題：{st.session_state.theme}")
    
    # 実際に出すべきだった順番（昇順）
    sorted_nums = sorted(st.session_state.numbers)
    
    for i, num in enumerate(st.session_state.numbers):
        st.write(f"プレイヤー {i+1}: **{num}**")
        
    if st.session_state.numbers == sorted_nums:
        st.success("成功！小さい順に出せました！")
    else:
        st.error("失敗... 順番が違ったようです。")

    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
