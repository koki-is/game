import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image

# ページ設定を「ワイド」にする
st.set_page_config(layout="wide")

st.title("🎨 デカめのお絵描きクイズ")

# サイドバーに設定をまとめる（メイン画面を広く使うため）
with st.sidebar:
    st.header("設定")
    stroke_width = st.slider("線の太さ: ", 1, 25, 10)
    if st.button("キャンバスをリセット"):
        st.rerun()

# キャンバスを中央寄せっぽく配置
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#ffffff",
        height=500, # スマホでも見やすい高さ
        width=700,  # スマホの横向きやタブレットでも十分な広さ
        drawing_mode="freedraw",
        key="canvas",
    )

    if st.button("🚀 AIに判定してもらう", use_container_width=True):
        if canvas_result.image_data is not None:
            st.info("AIが画像を解析中...")
            # ここにAI判定のロジックを入れる
        else:
            st.warning("何か描いてからボタンを押してね！")
