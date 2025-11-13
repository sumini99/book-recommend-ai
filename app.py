import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random
from aladin_api import search_books


# -------------------------------
# 1) 한글 폰트 로드
# -------------------------------
font_path = "kyoboson.ttf"  # repo 최상위에 업로드한 폰트
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)


# -------------------------------
# 2) 랜덤 색상 생성
# -------------------------------
def random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# -------------------------------
# 3) 페이지수 안전 처리
# -------------------------------
def safe_int(value, default=200):
    try:
        if value is None:
            return default
        v = str(value).strip()
        if v == "":
            return default
        return int(v)
    except:
        return default


# -------------------------------
# Streamlit 기본 설정
# -------------------------------
st.set_page_config(page_title="책 쌓기", layout="wide")

st.title("📚 AI 기반 알라딘 책검색 + 책탑 쌓기")
st.write("책 제목을 입력하면 알라딘에서 정보를 가져와 책을 쌓습니다!")


# 세션 초기화
if "books" not in st.session_state:
    st.session_state.books = []

if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# -------------------------------
# 🔍 4) 검색 영역
# -------------------------------
with st.form(key="search_form"):
    title_input = st.text_input("책 제목 입력 (필수)")
    author_input = st.text_input("저자 입력 (선택)")
    submitted = st.form_submit_button("검색하기")

if submitted:
    if title_input:
        st.session_state.search_results = search_books(title_input)
    else:
        st.warning("책 제목을 입력해야 검색됩니다.")


# -------------------------------
# 📘 5) 검색 결과 보여주기
# -------------------------------
if "search_results" in st.session_state:
    results = st.session_state.search_results

    if not results:
        st.error("검색 결과를 찾을 수 없습니다.")
    else:
        st.subheader("📘 이 책이 맞나요?")

        for idx, book in enumerate(results):
            with st.container():
                st.write(f"### {idx+1}. {book['title']}")
                st.write(f"**저자:** {book['author']}")
                st.write(f"**출판사:** {book.get('publisher', '정보 없음')}")
                st.image(book["cover"], width=120)

                if st.button(f"이 책 선택하기 ({idx+1})"):
                    st.session_state.selected_book = book


# -------------------------------
# 🧱 6) 책 선택 후 → 책탑에 쌓기
# -------------------------------
selected = st.session_state.selected_book

if selected:
    st.success(f"'{selected['title']}' 선택됨! 아래에 쌓입니다.")

    pages = safe_int(selected["pages"])
    height = 1.5 + min(pages / 1500, 0.6)  
    # → 기본 1.5 ~ 최대 2.1 (두꺼워지되 너무 과하지 않음)

    st.session_state.books.append({
        "title": selected["title"],
        "author": selected["author"],
        "pages": pages,
        "height": height,
        "color": random_color()
    })

    st.session_state.selected_book = None


# -------------------------------
# 🏗️ 7) 책 시각화 (계단식 + 위로 쌓임)
# -------------------------------
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = list(reversed(st.session_state.books))  # 최근 책이 위로 가게

    fig_height = max(5, len(books) * 1.7)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 2 + 2)
    ax.invert_yaxis()

    y = 1
    offset_direction = 1

    for idx, book in enumerate(books):
        color = book["color"]
        thickness = book["height"]

        # 좌우 계단식 x offset
        x_offset = (idx % 3) * 1.2 * offset_direction
        offset_direction *= -1

        # 책 박스
        rect = plt.Rectangle((3 + x_offset, y), 6, thickness,
                             color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        # 책 제목 + 저자 (가운데 정렬)
        ax.text(
            3 + x_offset + 3,
            y + thickness / 2,
            f"{book['title']} - {book['author']}",
            fontsize=13,
            color="black",
            fontproperties=font_prop,
            weight="bold",
            ha="center",
            va="center"
        )

        y += thickness + 0.6  # 다음 책 위로 이동

    ax.axis("off")
    st.pyplot(fig)


# -------------------------------
# 🗑️ 전체 초기화
# -------------------------------
if st.button("모든 책 초기화"):
    st.session_state.books = []
    st.experimental_rerun()
