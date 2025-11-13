import streamlit as st
import matplotlib.pyplot as plt
import random
import matplotlib.font_manager as fm
from aladin_api import search_books

# -----------------------------
# 한글 폰트 적용
# -----------------------------
font_path = "kyoboson.ttf"
font_prop = fm.FontProperties(fname=font_path)

# -----------------------------
# 세션 초기화
# -----------------------------
if "books" not in st.session_state:
    st.session_state.books = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []

st.title("📚 책 쌓기 프로젝트")

# -----------------------------
# 🔍 검색 입력
# -----------------------------
title_input = st.text_input("책 제목 입력")
author_input = st.text_input("저자 입력 (선택)")

if st.button("🔎 알라딘에서 검색"):
    query = title_input.strip()

    if author_input.strip():
        query += " " + author_input.strip()

    results = search_books(query)

    if results:
        st.session_state.search_results = results
    else:
        st.error("검색 결과가 없습니다.")

# -----------------------------
# 🔽 검색된 책 리스트 표시
# -----------------------------
if st.session_state.search_results:
    st.subheader("📘 검색된 책 중 선택하세요")

    for i, book in enumerate(st.session_state.search_results):
        with st.container():
            cols = st.columns([1, 3])

            with cols[0]:
                st.image(book["image"], width=120)  # ⭐ 책 표지 이미지 추가

            with cols[1]:
                st.write(f"**{i+1}. {book['title']}**")
                st.write(f"저자: {book['author']}")
                st.write(f"출판사: {book['publisher']}")

                if st.button(f"➕ 이 책 쌓기", key=f"add_{i}"):
                    st.session_state.books.append(book)
                    st.success(f"'{book['title']}' 쌓였습니다!")
                    st.session_state.search_results = []
                    st.rerun()   # ⭐ 최신 Streamlit용 rerun

# -----------------------------
# 📚 쌓인 책 시각화
# -----------------------------
st.subheader("📚 내가 쌓은 책들")

books = st.session_state.books

if not books:
    st.info("아직 쌓인 책이 없습니다.")
else:

    fig_height = max(5, len(books) * 1.5)
    fig, ax = plt.subplots(figsize=(12, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 1.7 + 2)
    ax.invert_yaxis()
    ax.axis("off")

    y = 1
    offset_pattern = [0, 1, -1]  # 고정된 패턴 → 책 흔들리지 않음

    for idx, book in enumerate(books):
        color = book.get("color", f"#{random.randint(0, 0xFFFFFF):06x}")
        book["color"] = color

        # -------------------
        # 제목 길면 "..."
        # -------------------
        title = book["title"]
        if len(title) > 25:
            title = title[:25] + "..."

        x_offset = offset_pattern[idx % 3] * 1.0

        # 페이지 관련
        pages = book.get("pages", 180)
        height = 1.5 + (pages / 800)

        rect = plt.Rectangle((3 + x_offset, y), 6, height,
                             color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        # 텍스트
        ax.text(
            3 + x_offset + 3,
            y + height / 2,
            title,
            ha="center",
            va="center",
            fontsize=14,
            fontproperties=font_prop,
            weight="bold",
        )

        y += height + 0.1  # 책 사이 딱 붙게

    st.pyplot(fig)
