import streamlit as st
from openai import OpenAI

# タイトル
st.title("ChatGPT Webサービス")

# SecretsからAPIキーを取得
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

user_input = st.text_input("ChatGPTに相談する：", placeholder="今日の献立を考えて")

if st.button("送信"):
    if user_input:
        # OpenAI APIを呼び出し
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}]
        )
        st.write("### AIの回答")
        st.write(response.choices[0].message.content)
    else:
        st.warning("メッセージを入力してください")
