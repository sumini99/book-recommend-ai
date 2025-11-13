import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import random
from aladin_api import search_books


# ================================================================
# UI 스타일 (CSS)
# ================================================================
def local_css(css_text):
    st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)

local_css("""
.page-title {
    text-align: center;
    font-weight: 800;
    font-size: 32px;
    margin-top: 20px;
    margin-bottom: 30px;
}
.search-card, .book-card {
    background: #1e1e1e;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #333;
    margin-bottom: 25px;
}
.stButton>button {
    width: 180px;
    height: 42px;
    border-radius: 8px;
    font-weight: 600;
}
""")


# ================================================================
# 한글 폰트 로드
# ================================================================
font_path = "kyoboson.ttf"
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)


# ================================================================
# 파스텔 컬러 팔레트
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


def safe_int(v, default=200):
    try:
        return int(v)
    except:
        return default


def shorten_title(t, max_len=24):
    return t if len(t) <= max_len else t[:max_len] + "..."


# ================================================================
# "절대 깨지지 않는" 둥근 직사각형 함수
# ================================================================
def rounded_rect(ax, x, y, w, h, r, color, edgecolor, zorder):

    # 반지름 제한 (너무 크면 자동 감소)
    r = min(r, w/2, h/2)

    verts = [
        (x+r, y),                 # start
        (x+w-r, y),
        (x+w, y),                 # corner 1
        (x+w, y+r),
        (x+w, y+h-r),
        (x+w, y+h),               # corner 2
        (x+w-r, y+h),
        (x+r, y+h),
        (x, y+h),                 # corner 3
        (x, y+h-r),
        (x, y+r),
        (x, y),                   # corner 4
        (x+r, y)
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
    ]

    patch = PathPatch(
        Path(verts, codes),
        facecolor=color,
        edgecolor=edgecolor,
        linewidth=2,
        zorder=zorder,
    )
    ax.add_patch(patch)


# ================================================================
# 예쁜 책 그리기 함수
# ================================================================
def draw_pretty_book(ax, x, y, width, height, color, title, font_prop):

    # 그림자
    rounded_rect(
        ax,
        x + 0.1, y + 0.1,
        width, height,
        r=6,
        color=(0, 0, 0, 0.18),
        edgecolor=(0, 0, 0, 0),
        zorder=1
    )

    # 책 본체
    rounded_rect(
        ax,
        x, y,
        width, height,
        r=6,                      # ✔ 모서리 둥근 정도 감소 → 책처럼 보임
        color=color,
        edgecolor="#333333",
        zorder=2
    )

    # 제목
    ax.text(
        x + width/2,
        y + height/2,
        title,
        ha="center",
        va="center",
        fontsize=13,
        color="black",
        fontproperties=font_prop,
        weight="bold",
        zorder=3
    )

# ================================================================
# Streamlit 앱 구성
# ================================================================
st.set_page_config(page_title="책 쌓기", layout="wide")
st.markdown("<h1 class='page-title'>📚 예쁜 파스텔 책탑 쌓기</h1>", unsafe_allow_html=True)

if "books" not in st.session_state:
    st.session_state.books = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# ----------------------------------------------------------
# 검색 UI
# ----------------------------------------------------------
st.markdown("<div class='search-card'>", unsafe_allow_html=True)

with st.form("search_form"):
    title_input = st.text_input("📗 책 제목 입력")
    author_input = st.text_input("✍️ 저자(선택)")
    do_search = st.form_submit_button("검색하기")

st.markdown("</div>", unsafe_allow_html=True)

if do_search:
    if title_input:
        st.session_state.search_results = search_books(title_input)
    else:
        st.warning("책 제목은 필수입니다.")


# ----------------------------------------------------------
# 검색 결과 표시
# ----------------------------------------------------------
if "search_results" in st.session_state:
    results = st.session_state.search_results
    st.subheader("📘 이 책이 맞나요?")

    if not results:
        st.error("검색 결과 없음")
    else:
        for i, book in enumerate(results):
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            st.write(f"### {i+1}. {book['title']}")
            st.write(f"**저자:** {book['author']}")
            st.image(book["cover"], width=150)

            if st.button(f"이 책 선택하기 ({i+1})"):
                st.session_state.selected_book = book

            st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------
# 선택된 책을 책탑에 추가
# ----------------------------------------------------------
sel = st.session_state.selected_book
if sel:
    st.success(f"'{sel['title']}' 책탑에 추가!")

    pages = safe_int(sel["pages"])
    height = 2.2 + min(pages / 1200, 1.0)

    idx = len(st.session_state.books)
    direction = 1 if idx % 2 == 0 else -1
    x_offset = (idx % 3) * 1.2 * direction

    st.session_state.books.append({
        "title": sel["title"],
        "height": height,
        "color": pastel_color(),
        "x_offset": x_offset
    })

    st.session_state.selected_book = None


# ----------------------------------------------------------
# 책탑 시각화
# ----------------------------------------------------------
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 책이 없습니다!")
else:
    books = list(reversed(st.session_state.books))

    fig, ax = plt.subplots(figsize=(12, max(6, len(books) * 1.7)))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, len(books) * 2 + 3)
    ax.invert_yaxis()

    y = 1

    for book in books:
        draw_pretty_book(
            ax,
            x=4 + book["x_offset"],
            y=y,
            width=7.0,
            height=book["height"],
            color=book["color"],
            title=shorten_title(book["title"]),
            font_prop=font_prop
        )
        y += book["height"] + 0.4

    ax.axis("off")
    st.pyplot(fig)


# ----------------------------------------------------------
# 초기화 버튼
# ----------------------------------------------------------
if st.button("모든 책 초기화"):
    st.session_state.books = []
    st.experimental_rerun()

