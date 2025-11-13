import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random

from aladin_api import search_book_from_aladin   # ⬅ 추가된 부분


# ----------------- 기본 설정 -----------------
st.set_page_config(page_title="AI + 알라딘 독서 탑", layout="wide")

if "books" not in st.session_state:
    st.session_state.books = []

# 한글 폰트 적용
font_path = "kyoboson.ttf"
font_prop = fm.FontProperties(fname=font_path)
fm.fontManager.addfont(font_path)
plt.rc("font", family=font_prop.get_name())


# ----------------- 책 입력 -----------------
st.title("📚 알라딘 기반 독서 탑 쌓기")

col1, col2 = st.columns(2)
with col1:
    title = st.text_input("책 제목 입력")
with col2:
    author = st.text_input("저자 입력")

if st.button("책 추가하기"):
    if not title or not author:
        st.warning("제목과 저자를 모두 입력해주세요.")
    else:
        info = search_book_from_aladin(title, author)

        if info:
            # 랜덤 색상 추가
            info["color"] = random.choice([
                "#F7A8A8", "#A8D1F7", "#A8F7E8",
                "#F7E7A8", "#C7A8F7", "#FFA6D1"
            ])

            st.session_state.books.append(info)
            st.success(f"책 추가 성공! → {info['title']}")
        else:
            st.error("알라딘에서 정보를 찾을 수 없습니다.")


# ----------------- 책탑 시각화 -----------------
st.subheader("📚 내가 쌓은 책들")

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
        height = max(1, book["pages"] / 150)   # 150 페이지 = 1 높이

        x_offset = (idx % 3) * 1.5 * offset_direction
        offset_direction *= -1

        rect = plt.Rectangle((3 + x_offset, y), 6, height,
                             color=book["color"], ec="black", linewidth=2)
        ax.add_patch(rect)

        ax.text(
            3 + x_offset + 3,
            y + height * 0.5,
            f"{book['title']} - {book['author']}",
            fontsize=13,
            fontproperties=font_prop,
            ha="center", va="center"
        )

        y += height + 0.7

    ax.axis("off")
    st.pyplot(fig)


# ----------------- 오른쪽 상세 보기 -----------------
st.subheader("📖 책 상세 정보")

if st.session_state.books:
    selected = st.selectbox(
        "책 선택",
        [b["title"] for b in st.session_state.books]
    )

    book = next(b for b in st.session_state.books if b["title"] == selected)

    st.image(book["cover"], width=160)
    st.write(f"### 제목: {book['title']}")
    st.write(f"**저자:** {book['author']}")
    st.write(f"**페이지:** {book['pages']}쪽")
    st.write("**요약:**")
    st.write(book.get("description", "요약 정보 없음"))
