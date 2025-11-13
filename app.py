import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random
from matplotlib.patches import FancyBboxPatch
from aladin_api import search_books



# ================================================================
# 0) Custom CSS – UI 예쁘게 만들기
# ================================================================
def local_css(css_text):
    st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)

local_css("""
/* 페이지 전체 패딩 제거 */
.main {
    padding: 0px !important;
}

/* 제목 스타일 */
.page-title {
    text-align: center;
    font-weight: 800;
    font-size: 32px;
    margin-top: 20px;
    margin-bottom: 30px;
}

/* 카드 UI */
.search-card, .book-card {
    background: #1e1e1e;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #333;
    margin-bottom: 25px;
}

/* 버튼 둥글게 + 사이즈 */
.stButton>button {
    width: 180px;
    height: 42px;
    border-radius: 8px;
    font-weight: 600;
}

/* 입력창 스타일 */
.stTextInput>div>div>input {
    background: #2c2c2c !important;
    color: white !important;
    border-radius: 8px;
    padding: 10px;
}

/* 텍스트 색상 */
h3, h2, h1, label {
    color: #ffffff !important;
}
""")


# ================================================================
# 1) 한글 폰트 로드
# ================================================================
font_path = "kyoboson.ttf"
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)


# ================================================================
# 2) Utility functions
# ================================================================
PALETTE = [
    "#FFCDD2",  # pink
    "#F8BBD0",  # light pink
    "#E1F5FE",  # sky blue
    "#E8F5E9",  # mint
    "#FFF9C4",  # yellow
    "#D1C4E9",  # lavender
    "#FFE0B2",  # peach
]

def pastel_color():
    return random.choice(PALETTE)

def safe_int(value, default=200):
    try:
        if not value:
            return default
        return int(str(value).strip())
    except:
        return default

def shorten_title(title, max_len=20):
    if len(title) <= max_len:
        return title
    return title[:max_len] + "..."


# ================================================================
# 3) 감성 파스텔 책 그리는 함수
# ================================================================
def draw_pretty_book(ax, x, y, width, height, color, title, font_prop):

    # 그림자 (아래 얇게)
    shadow = FancyBboxPatch(
        (x, y + height - 0.12),
        width,
        0.12,
        boxstyle="round,pad=0.05,rounding_size=12",
        linewidth=0,
        facecolor="rgba(0,0,0,0.15)"
    )
    ax.add_patch(shadow)

    # 책 본체 (라운드 박스)
    book_patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.2,rounding_size=12",
        linewidth=1.5,
        edgecolor="#444444",
        facecolor=color
    )
    ax.add_patch(book_patch)

    # 제목 텍스트
    ax.text(
        x + width / 2,
        y + height / 2,
        title,
        ha="center",
        va="center",
        fontproperties=font_prop,
        fontsize=13,
        color="black",
        weight="bold"
    )



# ================================================================
# Streamlit 기본 설정
# ================================================================
st.set_page_config(page_title="책 쌓기", layout="wide")
st.markdown("<h1 class='page-title'>📚 AI 기반 알라딘 책검색 + 책탑 쌓기</h1>", unsafe_allow_html=True)


# 세션 초기화
if "books" not in st.session_state:
    st.session_state.books = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None



# ================================================================
# 4) 검색 UI (카드형)
# ================================================================
st.markdown("<div class='search-card'>", unsafe_allow_html=True)

with st.form(key="search_form"):
    title_input = st.text_input("📘 책 제목 입력 (필수)")
    author_input = st.text_input("✍️ 저자 입력 (선택)")
    submitted = st.form_submit_button("검색하기")

st.markdown("</div>", unsafe_allow_html=True)


if submitted:
    if title_input:
        st.session_state.search_results = search_books(title_input)
    else:
        st.warning("책 제목을 입력해야 검색됩니다.")



# ================================================================
# 5) 검색 결과 UI (카드형)
# ================================================================
if "search_results" in st.session_state:
    results = st.session_state.search_results

    st.subheader("📘 이 책이 맞나요?")

    if not results:
        st.error("검색 결과를 찾을 수 없습니다.")
    else:
        for idx, book in enumerate(results):
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)

            st.write(f"### {idx+1}. {book['title']}")
            st.write(f"**저자:** {book['author']}")
            st.write(f"**출판사:** {book.get('publisher', '정보 없음')}")

            st.image(book["cover"], width=150)

            if st.button(f"이 책 선택하기 ({idx+1})"):
                st.session_state.selected_book = book

            st.markdown("</div>", unsafe_allow_html=True)



# ================================================================
# 6) 책 선택 → 책탑 추가
# ================================================================
selected = st.session_state.selected_book

if selected:
    st.success(f"'{selected['title']}' 선택됨! 아래 책탑에 쌓습니다.")

    pages = safe_int(selected["pages"])
    height = 1.2 + min(pages / 1500, 0.5)

    idx = len(st.session_state.books)
    direction = 1 if idx % 2 == 0 else -1
    x_offset = (idx % 3) * 1.2 * direction

    st.session_state.books.append({
        "title": selected["title"],
        "pages": pages,
        "height": height,
        "color": pastel_color(),
        "x_offset": x_offset
    })

    st.session_state.selected_book = None



# ================================================================
# 7) 책 시각화 (파스텔 책탑)
# ================================================================
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = list(reversed(st.session_state.books))

    fig_height = max(5, len(books) * 1.4)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 2 + 1)
    ax.invert_yaxis()

    y = 1

    for idx, book in enumerate(books):
        draw_pretty_book(
            ax,
            x=3 + book["x_offset"],
            y=y,
            width=6,
            height=book["height"],
            color=book["color"],
            title=shorten_title(book["title"]),
            font_prop=font_prop
        )

        y += book["height"] + 0.15

    ax.axis("off")
    st.pyplot(fig)



# ================================================================
# 8) 초기화 버튼
# ================================================================
if st.button("모든 책 초기화"):
    st.session_state.books = []
    st.experimental_rerun()

