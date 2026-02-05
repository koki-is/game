import streamlit as st
import random
from openai import OpenAI
from streamlit_sortables import sort_items

# 初期設定
st.set_page_config(page_title="AI ito Game", page_icon="🃏", layout="centered")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# プレイヤーごとのカラー（いただいた24色から代表色を抽出）
PLAYER_COLORS = ["#A6D8E4", "#A5BFE8", "#AEBFD3", "#FFB6C1", "#E5B4D6", "#FFC4B8"]

# --- 強力なCSS注入（ライブラリの赤色を完全に消し去る） ---
st.markdown(f"""
    <style>
    /* 全体的なボタンのサイズアップ */
    .stButton > button {{
        width: 100%;
        height: 65px;
        font-size: 20px !important;
        border-radius: 15px !important;
        background-color: #f0f2f6;
    }}

    /* 回答フェーズ：ドラッグカードの赤色背景を完全に上書き */
    div[data-testid="stMarkdownContainer"] {{
        background-color: transparent !important;
    }}
    
    /* 正方形のデカカード設定 */
    div:has(> p:contains("プレイヤー")) {{
        width: 180px !important;
        height: 180px !important;
        min-height: 180px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 15px auto !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        border: 4px solid white !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #333 !important;
        cursor: grab !important;
    }}

    /* プレイヤーごとの背景色指定（!importantでライブラリのスタイルを無視） */
    div:has(> p:contains("プレイヤー 1")) {{ background-color: {PLAYER_COLORS[0]} !important; }}
    div:has(> p:contains("プレイヤー 2")) {{ background-color: {PLAYER_COLORS[1]} !important; }}
    div:has(> p:contains("プレイヤー 3")) {{ background-color: {PLAYER_COLORS[2]} !important; }}
    div:has(> p:contains("プレイヤー 4")) {{ background-color: {PLAYER_COLORS[3]} !important; }}
    div:has(> p:contains("プレイヤー 5")) {{ background-color: {PLAYER_COLORS[4]} !important; }}
    div:has(> p:contains("プレイヤー 6")) {{ background-color: {PLAYER_COLORS[5]} !important; }}

    /* sortablesのデフォルト枠を透明化 */
    .st-emotion-cache-12w0qpk {{
        background-color: transparent !important;
        border: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

if 'game_status' not in st.session_state:
    st.session_state.game_status = "setup"
    st.session_state.numbers = []
    st.session_state.theme = ""

def generate_ito_theme(category):
    """ito-theme-makerの傾向（具体的・主観的・ニッチ）を学習したプロンプト"""
    
    # サイトの傾向を学習させたFew-Shot
    learned_examples = """
    - 異世界転生した時に持っていたい初期スキル (1:ゴミスキル - 100:チートスキル)
    - 恋人と初デート。相手がやってきたら『おっ』と思う行動 (1:冷める - 100:結婚を意識する)
    - コンビニでこれ売ってたら絶対二度見する商品 (1:普通 - 100:伝説)
    - 自分が透明人間になったらやりたいことのワクワク度 (1:地味 - 100:大胆)
    """

    system_prompt = (
        "あなたはボードゲーム『ito』のマスターです。ito-theme-makerにあるような、"
        "主観的で、具体的で、かつプレイヤー同士の議論が止まらなくなる面白いお題を生成してください。"
    )
    user_prompt = (
        f"カテゴリー「{category}」に基づいた新しいお題を作成してください。\n"
        f"【お手本】\n{learned_examples}\n\n"
        "【ルール】\n"
        "- 必ず『お題：〇〇（1＝××、100＝△△）』の形式で出力してください。\n"
        "- 誰にでも答えがわかる客観的な事柄（値段、重さ、身長など）は厳禁です。"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.95
    )
    return response.choices[0].message.content

# --- 1. 設定フェーズ ---
if st.session_state.game_status == "setup":
    st.title("🃏 AI ito - Theme Maker Ver.")
    
    # プルダウンに変更
    num_players = st.selectbox("参加人数", [2, 3, 4, 5, 6], index=1)
    # 恋愛ジャンルを追加
    category = st.selectbox("ジャンル", ["恋愛", "人気・好感度", "強さ・能力", "日常・食べ物", "人生・価値観", "修学旅行・学校"])
    
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
                    <h1 style="color:#333; margin:0; font-size: 80px;">{st.session_state.numbers[i]}</h1>
                </div>
            """, unsafe_allow_html=True)

    if st.button("並べ替え（回答）へ進む"):
        st.session_state.game_status = "sorting"
        st.rerun()

# --- 3. 回答フェーズ（ドラッグ＆ドロップ） ---
elif st.session_state.game_status == "sorting":
    st.header("🃏 カードを並べ替え")
    st.write("小さい順（1に近い順）に上から並べてください。")

    player_labels = [f"プレイヤー {i+1}" for i in range(len(st.session_state.numbers))]
    
    # 改良されたドラッグUI（CSSでプレイヤーごとの色を適用）
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
            orig_idx = st.session_state.numbers.index(val)
            color = PLAYER_COLORS[orig_idx]
            st.markdown(f'<div style="background-color:{color}; padding:15px; border-radius:10px; margin-bottom:10px; color:#333; font-weight:bold; text-align:center;">{i}番目: {val}</div>', unsafe_allow_html=True)
            
    with col2:
        st.write("### 正解（小さい順）")
        for i, val in enumerate(correct_order, 1):
            st.markdown(f'<div style="padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #ccc; text-align:center;">{i}番目: **{val}**</div>', unsafe_allow_html=True)

    if st.session_state.final_order == correct_order:
        st.balloons()
        st.success("成功！完璧な連携でした！")
    else:
        st.error("残念！価値観のズレが発生しました。")

    if st.button("もう一度遊ぶ"):
        st.session_state.game_status = "setup"
        st.rerun()
