import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random

from aladin_api import search_books   # 알라딘 API 모듈


# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="📚 알라딘 독서 탑", layout="wide")

if "books" not in st.session_state:
    st.session_state.books = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []


# -----------------------------
# 한글 폰트 적용
# -----------------------------
font_path = "kyoboson.ttf"
font_prop = fm.FontProperties(fname=font_path)
fm.fontManager.addfont(font_path)
plt.rc("font", family=font_prop.get_name())


# -----------------------------
# 메인 화면 제목
# -----------------------------
st.title("📚 알라딘 기반 독서 탑 쌓기 (AI + Cloud 프로젝트)")


# -----------------------------
# 책 검색 섹션
# -----------------------------
st.subheader("🔍 책 검색하기")

title_input = st.text_input("책 제목을 입력하세요 (저자 입력 필요 없음!)")

if st.button("검색하기"):
    if not title_input:
        st.warning("책 제목을 입력해주세요.")
    else:
        results = search_books(title_input)
        st.session_state.search_results = results

        if not results:
            st.error("검색 결과를 찾을 수 없습니다.")


# -----------------------------
# 검색 결과 표시 (최대 5개)
# -----------------------------
if st.session_state.search_results:
    st.subheader("📘 이 책이 맞나요?")

    for idx, book in enumerate(st.session_state.search_results):

        with st.container(border=True):
            cols = st.columns([1, 3])

            with cols[0]:
                st.image(book["cover"], width=90)

            with cols[1]:
                st.write(f"### {book['title']}")
                st.write(f"**저자:** {book['author']}")
                st.write(f"**출판사:** {book['publisher']}")
                st.write(f"**페이지:** {book['pages']}쪽")

                # 책 선택 버튼
                if st.button(f"이 책 선택하기 #{idx}"):
                    new_book = book.copy()
                    new_book["color"] = random.choice([
                        "#F7A8A8", "#A8D1F7", "#A8F7E8",
                        "#F7E7A8", "#C7A8F7", "#FFA6D1"
                    ])
                    st.session_state.books.append(new_book)
                    st.success(f"'{book['title']}' 추가됨!")

                    # 선택 후 검색결과 초기화
                    st.session_state.search_results = []


# -----------------------------
# 책탑 시각화
# -----------------------------
st.subheader("🏗️ 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = st.session_state.books
    fig_height = max(5, len(books) * 2)

    fig, ax = plt.subplots(figsize=(11, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 2 + 3)
    ax.invert_yaxis()

    y = 1
    offset_direction = 1

    for idx, book in enumerate(books):
        # 페이지수 기반 높이 설정
        height = max(1.2, book["pages"] / 180)

        x_offset = (idx % 3) * 1.5 * offset_direction
        offset_direction *= -1

        rect = plt.Rectangle(
            (3 + x_offset, y), 6, height,
            color=book["color"], ec="black", linewidth=2
        )
        ax.add_patch(rect)

        ax.text(
            3 + x_offset + 3,
            y + height * 0.5,
            f"{book['title']} - {book['author']}",
            fontsize=13,
            fontproperties=font_prop,
            ha="center", va="center"
        )

        y += height + 0.8

    ax.axis("off")
    st.pyplot(fig)


# -----------------------------
# 책 상세 정보 (선택)
# -----------------------------
st.subheader("📖 책 상세 정보")

if st.session_state.books:
    selected_title = st.selectbox(
        "책을 선택하세요",
        [b["title"] for b in st.session_state.books]
    )

    book = next(b for b in st.session_state.books if b["title"] == selected_title)

    cols = st.columns([1, 3])

    with cols[0]:
        st.image(book["cover"], width=180)

    with cols[1]:
        st.write(f"## {book['title']}")
        st.write(f"**저자:** {book['author']}")
        st.write(f"**페이지:** {book['pages']}쪽")
        st.write(f"🔗 [알라딘 상세보기]({book['link']})")
        st.write("### 📘 책 설명")
        st.write(book.get("description", "설명 없음"))
