import streamlit as st
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="책 시각화 보드", page_icon="📚")

st.title("📚 내 책 쌓기(시각화)")

# ---- Session State 초기화 ----
if "books" not in st.session_state:
    st.session_state.books = []   # 책들을 여기 저장


# ---- 입력 영역 ----
st.subheader("📌 책 정보 입력")

title = st.text_input("책 제목")
author = st.text_input("저자")

if st.button("책 추가하기"):
    if title.strip() and author.strip():

        # 랜덤 색상 생성
        color = (
            random.random(),
            random.random(),
            random.random()
        )

        # 책 데이터 저장
        st.session_state.books.append({
            "title": title,
            "author": author,
            "color": color,
        })

        st.success(f"'{title}' 추가됨!")
    else:
        st.warning("제목과 저자를 모두 입력해주세요!")



# ---- 시각화 영역 ----
st.subheader("📚 내가 쌓은 책들")

if len(st.session_state.books) == 0:
    st.info("아직 책이 없습니다. 입력 후 추가해보세요!")
else:
    fig, ax = plt.subplots(figsize=(6, len(st.session_state.books) * 1.2))
    ax.set_xlim(0, 10)

    # Y축 뒤집기 (위에서 아래로 쌓이게)
    ax.invert_yaxis()

    y = 1  # 첫 번째 사각형의 위치

    for book in st.session_state.books:
        color = book["color"]

        # 사각형(책 블록)
        rect = plt.Rectangle((1, y), 8, 1, color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        # 텍스트 표시
        ax.text(
            1.4, y + 0.65,
            f"{book['title']} - {book['author']}",
            fontsize=12,
            color="black"
        )

        y += 1.3  # 다음 책 블록 아래에 배치

    ax.axis("off")
    st.pyplot(fig)
