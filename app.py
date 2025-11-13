import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random
from aladin_api import search_books


# -------------------------------
# 1) 한글 폰트 설정
# -------------------------------
font_path = "kyoboson.ttf"  # repo 최상위에 있는 파일
fm.fontManager.addfont(font_path)
plt.rc('font', family='KyoboHandwriting2020A')


# -------------------------------
# 2) 랜덤 색상 생성
# -------------------------------
def random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# -------------------------------
# 3) 페이지수 안전 변환
# -------------------------------
def safe_int(value, default=200):
    try:
        if value is None:
            return default
        value = str(value).strip()
        if value == "":
            return default
        return int(value)
    except:
        return default


# -------------------------------
# 4) Streamlit 기본 설정
# -------------------------------
st.set_page_config(page_title="책 쌓기", layout="wide")

st.title("📚 나만의 책탑 만들기")
st.write("책 제목과 저자를 입력하면 알라딘에서 검색하여 책을 쌓습니다!")


# 세션 초기화
if "books" not in st.session_state:
    st.session_state.books = []

if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# -------------------------------
# 🔍 5) 검색 영역
# -------------------------------
with st.form(key="search_form"):
    title_input = st.text_input("책 제목을 입력하세요")
    author_input = st.text_input("저자를 입력하세요 (선택)")

    submitted = st.form_submit_button("검색하기")

if submitted:
    if title_input:
        results = search_books(title_input)
        st.session_state.search_results = results
    else:
        st.warning("제목은 최소한 입력해야 검색이 가능합니다.")


# -------------------------------
# 📘 6) 검색 결과 출력 + 선택하기
# -------------------------------
if "search_results" in st.session_state:
    results = st.session_state.search_results

    if not results:
        st.error("검색 결과가 없습니다.")
    else:
        st.subheader("📘 이 책이 맞나요?")
        for idx, book in enumerate(results):
            with st.container():
                st.write(f"### {idx + 1}. {book['title']}")
                st.write(f"**저자:** {book['author']}")
                st.write(f"**출판사:** {book.get('publisher', '정보 없음')}")
                st.image(book["cover"], width=120)

                if st.button(f"이 책 선택하기 ({idx+1})"):
                    st.session_state.selected_book = book


# -------------------------------
# 🧱 7) 책 선택 후 쌓기 처리
# -------------------------------
selected = st.session_state.selected_book

if selected:
    st.success(f"'{selected['title']}' 선택됨! 아래에 쌓입니다.")

    pages = safe_int(selected["pages"], default=200)
    height = max(1.2, pages / 180)

    st.session_state.books.append({
        "title": selected["title"],
        "author": selected["author"],
        "pages": pages,
        "color": random_color(),
        "height": height
    })

    st.session_state.selected_book = None


# -------------------------------
# 🏗️ 8) 책 시각화 (위로 쌓이는 구조)
# -------------------------------
if st.session_state.books:
    st.subheader("🏗️ 내가 쌓은 책들")

    fig, ax = plt.subplots(figsize=(6, 12))

    total_height = 0
    for book in reversed(st.session_state.books):
        ax.barh(
            y=total_height,
            width=1,
            height=book["height"],
            color=book["color"],
            edgecolor="black"
        )
        ax.text(
            0.5, total_height + book["height"] / 2,
            f"{book['title']}\n({book['author']})",
            ha="center", va="center", fontsize=10
        )
        total_height += book["height"]

    ax.axis("off")
    st.pyplot(fig)


# -------------------------------
# 🗑️ 9) 책 초기화 버튼
# -------------------------------
if st.button("전체 책 초기화"):
    st.session_state.books = []
    st.experimental_rerun()
