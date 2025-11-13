import streamlit as st
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="책 시각화 보드", page_icon="📚")

st.title("📚 내 책 쌓기(시각화)")

# ---- Session State 초기화 ----
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


# ---- 시각화 영역 ----
st.subheader("📚 내가 쌓은 책들")

if len(st.session_state.books) == 0:
    st.info("아직 책이 없습니다.")
else:
    # 🔥 fig 높이는 책 개수에 따라 증가
    fig_height = max(5, len(st.session_state.books) * 1.5)
    fig, ax = plt.subplots(figsize=(8, fig_height))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(st.session_state.books) * 1.5 + 2)
    ax.invert_yaxis()  # 위에서부터 아래로 쌓이는 느낌

    y = 1  # 첫 박스 y좌표 시작점

    for book in st.session_state.books:
        color = book["color"]

        # 직사각형
        rect = plt.Rectangle((1, y), 8, 1.2, color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        # 텍스트
        ax.text(
            1.4, y + 0.8,
            f"{book['title']} - {book['author']}",
            fontsize=14,
            color="black",
            fontweight="bold"
        )

        y += 1.5  # 다음 박스 아래로 이동

    ax.axis("off")
    st.pyplot(fig)

