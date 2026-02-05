import streamlit as st
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI
import io
import base64
from PIL import Image

# 1. APIの設定（OpenAIを例に）
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🎨 AIお絵描きクイズ")
st.write("スマホで絵を描いて「AIに聞いてみる」を押してね！")

# 2. キャンバスの設定（スマホ対応を意識してサイズ調整）
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # 塗りつぶし色
    stroke_width=5,                       # 線の太さ
    stroke_color="#000000",               # 線の色
    background_color="#ffffff",           # 背景色
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
)

# 3. AIに画像を投げる関数
def analyze_image(image):
    # PIL画像をBase64に変換
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "この下手な絵は何を描いたものか、一言でズバリ答えてください。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                ],
            }
        ],
    )
    return response.choices[0].message.content

# 4. 判定ボタン
if st.button("AIに聞いてみる"):
    if canvas_result.image_data is not None:
        # キャンバスのデータを画像に変換
        img_data = canvas_result.image_data
        img = Image.fromarray(img_data.astype('uint8'), 'RGBA').convert('RGB')
        
        with st.spinner('AIが考えています...'):
            answer = analyze_image(img)
            st.subheader(f"🤔 AIの答え: {answer}")
    else:
        st.warning("まずは何か描いてみて！")
