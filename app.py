import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random
from aladin_api import search_books

# ------------------------------------
# ✔ 캐시 비활성화 (알라딘API 최신버전 로드 문제 해결)
# ------------------------------------
st.cache_data.clear()
st.cache_resource.clear()

# ------------------------------------
# ✔ 앱 제목
# ------------------------------------
st.title("📚 나만의 독서 책탑 만들기")

# ------------------------------------
# ✔ 세션 상태 초기화
# ------------------------------------
if "books" not in st.session_state:
    st.session_state.books = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

# ------------------------------------
# ✔ 검색 입력 UI
# ------------------------------------
st.subheader("🔍 책 검색")

title_input = st.text_input("📘 책 제목 입력")
author_input = st.text_input("✏️ 저자 입력 (선택)")

col_search = st.columns([1, 2, 1])
search_btn = st.button("검색하기")

# ------------------------------------
# ✔ 검색 처리
# ------------------------------------
if search_btn and title_input.strip():
    st.session_state.search_results = search_books(title_input, author_input)
    st.session_state.selected_book = None

# ------------------------------------
# ✔ 검색 결과 표시
# ------------------------------------
if st.session_state.search_results:
    st.subheader("📚 검색된 책 중 선택하세요")

    for i, book in enumerate(st.session_state.search_results):
        with st.container():
            cols = st.columns([1, 3])

            # 표지
            with cols[0]:
                cover = book.get("image") or book.get("cover") or ""
                if cover:
                    st.image(cover, width=110)
                else:
                    st.write("📕 (이미지 없음)")

            # 정보
            with cols[1]:
                st.write(f"**{i+1}. {book['title']}**")
                st.write(f"저자: {book['author']}")
                st.write(f"출판사: {book['publisher']}")

                if st.button(f"📌 이 책 선택", key=f"select_{i}"):
                    st.session_state.selected_book = book
                    st.session_state.search_results = []
                    st.experimental_rerun()

# ------------------------------------
# ✔ 선택된 책 정보
# ------------------------------------
if st.session_state.selected_book:
    book = st.session_state.selected_book

    st.subheader("📌 선택한 책")

    cols = st.columns([1, 3])
    with cols[0]:
        if book.get("image"):
            st.image(book["image"], width=140)
    with cols[1]:
        st.write(f"### {book['title']}")
        st.write(f"저자: {book['author']}")
        st.write(f"출판사: {book['publisher']}")
        st.write(f"페이지: {book['pages']}")

    if st.button("📚 책 쌓기"):
        # 저장 구조
        st.session_state.books.append({
            "title": book["title"],
            "author": book["author"],
            "pages": book["pages"],
            "color": "#" + ("%06x" % random.randint(0, 0xFFFFFF)),
        })

        st.session_state.selected_book = None
        st.experimental_rerun()

# ------------------------------------
# ✔ 책탑 시각화
# ------------------------------------
st.subheader("🏗️ 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = list(reversed(st.session_state.books))  # 위로 쌓기

    # 책 간 간격 제거
    fig_height = max(5, len(books) * 1.3)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 1.4 + 2)
    ax.invert_yaxis()

    y = 1  # 시작 높이

    for idx, book in enumerate(books):
        height = max(0.7, book["pages"] / 600)  # 페이지 수 기반 높이
        color = book["color"]

        # 책 블록
        rect = plt.Rectangle((3, y), 6, height, color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        # 제목 (길면 … 처리)
        title = book["title"]
        if len(title) > 15:
            title = title[:13] + "..."

        ax.text(
            6, y + height / 2,
            title,
            fontsize=13,
            ha="center",
            va="center",
            color="black",
        )

        y += height  # 책이 딱 붙도록 함

    ax.axis("off")
    st.pyplot(fig)
