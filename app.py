import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
import random
from aladin_api import search_books


# ================================================================
# Custom CSS
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
# Load Font
# ================================================================
font_path = "kyoboson.ttf"
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)


# ================================================================
# Utility
# ================================================================
PALETTE = [
    "#FFCDD2", "#F8BBD0", "#E1F5FE",
    "#E8F5E9", "#FFF9C4", "#D1C4E9",
    "#FFE0B2"
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
# Pretty Rounded Book Drawing Function
# ================================================================
from matplotlib.path import Path
from matplotlib.patches import PathPatch

def rounded_rect(ax, x, y, width, height, radius, color, edgecolor):
    # 코너 반지름 제한 (너무 크면 터짐 방지)
    radius = min(radius, width/2, height/2)

    # Path 정의
    verts = [
        (x + radius, y),
        (x + width - radius, y),
        (x + width, y),
        (x + width, y + radius),
        (x + width, y + height - radius),
        (x + width, y + height),
        (x + width - radius, y + height),
        (x + radius, y + height),
        (x, y + height),
        (x, y + height - radius),
        (x, y + radius),
        (x, y),
        (x + radius, y),
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

    path = Path(verts, codes)
    patch = PathPatch(path, facecolor=color, edgecolor=edgecolor, linewidth=2, zorder=3)
    ax.add_patch(patch)


def draw_pretty_book(ax, x, y, width, height, color, title, font_prop):

    # 그림자
    rounded_rect(ax, x+0.15, y+0.12, width, height, radius=12,
                 color=(0,0,0,0.15), edgecolor=(0,0,0,0))

    # 본체
    rounded_rect(ax, x, y, width, height, radius=12,
                 color=color, edgecolor="#333333")

    # 텍스트
    ax.text(
        x + width/2,
        y + height/2,
        title,
        ha="center",
        va="center",
        fontproperties=font_prop,
        fontsize=14,
        color="black",
        weight="bold",
        zorder=4
    )

# ================================================================
# Streamlit Config
# ================================================================
st.set_page_config(page_title="책 쌓기", layout="wide")
st.markdown("<h1 class='page-title'>📚 AI 기반 알라딘 책검색 + 예쁜 책탑 쌓기</h1>", unsafe_allow_html=True)

if "books" not in st.session_state:
    st.session_state.books = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# ================================================================
# 검색 UI
# ================================================================
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

# ================================================================
# 검색 결과
# ================================================================
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


# ================================================================
# 책 선택 → 책탑에 추가
# ================================================================
sel = st.session_state.selected_book
if sel:
    st.success(f"'{sel['title']}' 책탑에 추가!")

    pages = safe_int(sel["pages"])
    height = 1.4 + min(pages / 1500, 0.6)

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


# ================================================================
# 책탑 시각화
# ================================================================
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
            width=6.5,
            height=book["height"],
            color=book["color"],
            title=shorten_title(book["title"])
        )

        y += book["height"] + 0.4

    ax.axis("off")
    st.pyplot(fig)


# ================================================================
# 초기화
# ================================================================
if st.button("모든 책 초기화"):
    st.session_state.books = []
    st.experimental_rerun()
