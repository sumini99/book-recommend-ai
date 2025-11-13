import streamlit as st
import matplotlib.pyplot as plt
import random
import matplotlib.font_manager as fm
import os
import requests

st.set_page_config(page_title="책 시각화 보드", page_icon="📚")

# ---- 한글 폰트 다운로드 및 등록 ----
font_path = "NanumGothic.ttf"

if not os.path.exists(font_path):
    url = "https://github.com/naver/nanumfont/blob/master/ttf/NanumGothic.ttf?raw=true"
    r = requests.get(url)
    with open(font_path, "wb") as f:
        f.write(r.content)

fontprop = fm.FontProperties(fname=font_path)

# ---- 제목 ----
st.title("📚 내 책 쌓기(시각화)")

# ---- Session State ----
if "books" not in st.session_state:
    st.session_state.books = []


# ---- 입력 영역 ----
st.subheader("📌 책 정보 입력")

title = st.text_input("책 제목")
author = st.text_input("저자")

if st.button("책 추가하기"):
    if title.strip() and author.strip():
        color = (random.random(), random.random(), random.random())

        st.session_state.books.append({
            "title": title,
            "author": author,
            "color": color,
        })

        st.success(f"'{title}' 추가됨!")
    else:
        st.warning("제목과 저자를 입력해주세요.")


# ---- 시각화 ----
st.subheader("📚 내가 쌓은 책들")

if len(st.session_state.books) == 0:
    st.info("아직 책이 없습니다.")
else:
    fig_height = max(5, len(st.session_state.books) * 1.5)
    fig, ax = plt.subplots(figsize=(8, fig_height))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(st.session_state.books) * 1.5 + 2)
    ax.invert_yaxis()

    y = 1

    for book in st.session_state.books:
        color = book["color"]

        rect = plt.Rectangle((1, y), 8, 1.2, color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        ax.text(
            1.4, y + 0.8,
            f"{book['title']} - {book['author']}",
            fontsize=14,
            fontproperties=fontprop,
            color="black",
            fontweight="bold"
        )

        y += 1.5

    ax.axis("off")
    st.pyplot(fig)

