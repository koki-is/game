{\rtf1\ansi\ansicpg932\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
from openai import OpenAI\
\
st.title("ChatGPT Web\uc0\u12469 \u12540 \u12499 \u12473 ")\
\
# API\uc0\u12461 \u12540 \u12398 \u35373 \u23450 \u65288 GitHub\u12395 \u20844 \u38283 \u12377 \u12427 \u38555 \u12399 \u32118 \u23550 \u12371 \u12371 \u12408 \u30452 \u25509 \u26360 \u12363 \u12394 \u12356 \u12391 \u12367 \u12384 \u12373 \u12356 \u65281 \u65289 \
client = OpenAI(api_key="\uc0\u12354 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")\
\
# \uc0\u12518 \u12540 \u12470 \u12540 \u20837 \u21147 \
user_input = st.text_input("ChatGPT\uc0\u12395 \u30456 \u35527 \u12377 \u12427 \u65306 ", placeholder="\u20170 \u26085 \u12398 \u29486 \u31435 \u12434 \u32771 \u12360 \u12390 ")\
\
if st.button("\uc0\u36865 \u20449 "):\
    if user_input:\
        # API\uc0\u21628 \u12403 \u20986 \u12375 \
        response = client.chat.completions.create(\
            model="gpt-4o-mini",  # \uc0\u39640 \u24615 \u33021 \u12391 \u23433 \u20385 \u12394 \u12514 \u12487 \u12523 \
            messages=[\
                \{"role": "user", "content": user_input\}\
            ]\
        )\
        \
        # \uc0\u32080 \u26524 \u12434 \u34920 \u31034 \
        st.write("### AI\uc0\u12398 \u22238 \u31572 ")\
        st.write(response.choices[0].message.content)\
    else:\
        st.warning("\uc0\u12513 \u12483 \u12475 \u12540 \u12472 \u12434 \u20837 \u21147 \u12375 \u12390 \u12367 \u12384 \u12373 \u12356 ")}