
import streamlit as st
import openai
import os

# 🔐 환경변수에서 API key 읽기 (코드에 키 직접 넣지 않음)
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI 도서 추천 챗봇", page_icon="📚")

st.title("📚 AI 도서 추천 챗봇")
st.write("키워드를 입력하면 AI가 관련 도서를 추천해드립니다.")

keyword = st.text_input("키워드를 입력하세요 (예: 빅데이터, AI, 힐링, 자기계발 등)")

if st.button("도서 추천 받기"):
    if keyword.strip():
        with st.spinner("AI가 추천 도서를 분석 중..."):
            prompt = f"추천 도서 3권을 알려줘. 키워드: '{keyword}'. 각 도서마다 이유를 한 문장씩 설명해줘."
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user", "content": prompt}],
                temperature=0.7
            )
            result = response.choices[0].message.content
            st.success("추천 완료!")
            st.write(result)
    else:
        st.warning("키워드를 입력해주세요!")
