import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random
from aladin_api import search_books

# ============================
# 🔤 폰트 설정
# ============================
FONT_PATH = "kyoboson.ttf"   # 리포지토리에 올라간 파일명
fm.fontManager.addfont(FONT_PATH)
font_prop = fm.FontProperties(fname=FONT_PATH)


# ============================
# 🔧 세션 초기화
# ============================
if "books" not in st.session_state:
    st.session_state.books = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []


# ============================
# 🔍 검색 입력 UI
# ============================
st.title("📚 책 쌓기 프로젝트")

title_input = st.text_input("책 제목을 입력하세요")
author_input = st.text_input("저자 입력 (선택)")

if st.button("🔍 검색하기"):
    results = search_books(title_input, author_input)
    st.session_state.search_results = results


# ============================
# 📌 검색 결과 UI
# ============================
if st.session_state.search_results:
    st.subheader("📘 검색된 책 중 선택하세요")

    for i, book in enumerate(st.session_state.search_results):
        with st.container():
            cols = st.columns([1, 3])

            # ====== 표지 이미지 처리 ======
            cover = book.get("image") or book.get("cover") or ""
            if cover:
                with cols[0]:
                    st.image(cover, width=120)
            else:
                with cols[0]:
                    st.write("📕 (이미지 없음)")

            # ====== 텍스트 정보 ======
            with cols[1]:
                st.write(f"### {book['title']}")
                st.write(f"저자: {book['author']}")
                st.write(f"출판사: {book['publisher']}")
                st.write(f"페이지 수: {book['pages']}")

                if st.button(f"📚 이 책 선택하기 #{i}", key=f"select_{i}"):
                    st.session_state.books.append(book)
                    st.success("✔ 책이 쌓였습니다!")
                    st.session_state.search_results = []
                    st.experimental_rerun()


# ============================
# 📚 쌓인 책 시각화
# ============================
st.subheader("🏗️ 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다!")
else:
    books = st.session_state.books

    # 쌓인 책 그래프
    fig_height = max(6, len(books) * 1.3)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 1.3 + 2)
    ax.invert_yaxis()  # 위로 쌓이게 만들기

    y = 0.5  # 아래 시작점

    for idx, book in enumerate(books):

        # 🔹 길이 제한된 제목(20자 넘어가면 …)
        title_short = (
            book["title"] if len(book["title"]) <= 20 
            else book["title"][:20] + "…"
        )

        # 🔹 책 높이 = 페이지 수에 비례 (최소 1)
        height = max(1.0, book["pages"] / 250)

        # 랜덤 색상
        color = book.get("color")
        if not color:
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            book["color"] = color

        # 책 박스
        rect = plt.Rectangle((3, y), 6, height, color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        # 텍스트 (중앙)
        ax.text(
            3 + 3, y + height / 2,
            title_short,
            fontsize=13,
            fontproperties=font_prop,
            color="black",
            weight="bold",
            ha="center", va="center"
        )

        y += height + 0.1  # 🔥 간격 거의 없이 붙임

    ax.axis("off")
    st.pyplot(fig)
