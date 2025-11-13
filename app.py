import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle
import io
import random
from aladin_api import search_books


# ================================================================
# 0) Streamlit config (⚠ 맨 위에서 바로 적용해야 wide OFF 가능)
# ================================================================
st.set_page_config(page_title="책 쌓기", layout="centered")


# ================================================================
# 1) Custom CSS
# ================================================================
def local_css(text):
    st.markdown(f"<style>{text}</style>", unsafe_allow_html=True)

local_css("""
.page-title {
    text-align: center;
    font-weight: 800;
    font-size: 32px;
    margin-top: 10px;
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
    border-radius: 6px;
    font-weight: 600;
}
""")


# ================================================================
# 2) Font Load
# ================================================================
font_path = "kyoboson.ttf"
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)


# ================================================================
# 3) Utils
# ================================================================
PALETTE = [
    # Pastel
    "#FFCDD2", "#F8BBD0", "#E1BEE7",
    "#D1C4E9", "#C5CAE9", "#BBDEFB",
    "#B3E5FC", "#B2EBF2", "#B2DFDB",
    "#C8E6C9", "#DCEDC8", "#F0F4C3",

    # Vivid
    "#FFAB91", "#FF8A65", "#FF7043",
    "#FFCC80", "#FFD54F", "#FFE082",
    "#80CBC4", "#4DB6AC", "#26A69A",
    "#64B5F6", "#42A5F5", "#1E88E5",

    # Neutral
    "#F5E0C3", "#E8D1A1", "#D7C0AE",
    "#C1B4A3", "#B8A590", "#A1887F",
]


def pastel_color():
    return random.choice(PALETTE)

def safe_int(v, default=200):
    try:
        return int(v)
    except:
        return default

def shorten_title(t, max_len=22):
    return t if len(t) <= max_len else t[:max_len] + "..."


# ================================================================
# 4) 완전 사각형 + 그림자 책 그리기
# ================================================================
def draw_book(ax, x, y, w, h, color, title):
    # 그림자 (회색)
    ax.add_patch(Rectangle(
        (x + 0.12, y + 0.12),
        w, h,
        linewidth=0,
        facecolor=(0, 0, 0, 0.25),
        zorder=1,
    ))

    # 본체 (사각형)
    ax.add_patch(Rectangle(
        (x, y),
        w, h,
        linewidth=1.8,
        edgecolor="#333333",
        facecolor=color,
        zorder=2,
    ))

    # 제목
    ax.text(
        x + w/2,
        y + h/2,
        title,
        ha="center",
        va="center",
        fontsize=13,
        color="black",
        fontproperties=font_prop,
        weight="bold",
        zorder=3,
    )


# ================================================================
# 5) 앱 상태 초기화
# ================================================================
if "books" not in st.session_state:
    st.session_state.books = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# ================================================================
# 6) UI — 검색 영역
# ================================================================
st.markdown("<h1 class='page-title'>📚 AI 기반 알라딘 책검색 + 책탑 쌓기</h1>", unsafe_allow_html=True)
st.markdown("<div class='search-card'>", unsafe_allow_html=True)

with st.form("search_form"):
    title_input = st.text_input("📗 책 제목 입력 (필수)")
    author_input = st.text_input("✍️ 저자 (선택)")
    submitted = st.form_submit_button("검색하기")

st.markdown("</div>", unsafe_allow_html=True)


if submitted:
    if title_input:
        st.session_state.search_results = search_books(title_input)
    else:
        st.warning("책 제목을 입력해야 합니다!")


# ================================================================
# 7) 검색 결과 표시
# ================================================================
if "search_results" in st.session_state:
    results = st.session_state.search_results
    st.subheader("📘 이 책이 맞나요?")

    if not results:
        st.error("검색 결과 없음")
    else:
        for idx, book in enumerate(results):
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)

            st.write(f"### {idx+1}. {book['title']}")
            st.write(f"**저자:** {book['author']}")
            st.image(book["cover"], width=120)

            if st.button(f"이 책 선택 ({idx+1})"):
                st.session_state.selected_book = book

            st.markdown("</div>", unsafe_allow_html=True)


# ================================================================
# 8) 책 선택 → 책탑에 추가
# ================================================================
sel = st.session_state.selected_book
if sel:
    st.success(f"'{sel['title']}' 추가됨!")

    pages = safe_int(sel.get("pages"))
    height = 0.9 + min(pages / 1500, 0.7)  # 0.9 ~ 1.6

    idx = len(st.session_state.books)
    direction = 1 if idx % 2 == 0 else -1
    x_offset = (idx % 3) * 0.8 * direction

    st.session_state.books.append({
        "title": sel["title"],
        "height": height,
        "color": pastel_color(),
        "x_offset": x_offset,
    })

    st.session_state.selected_book = None


# ================================================================
# 9) 책탑 시각화 (이미지 → 절대 안 잘리고 스크롤됨)
# ================================================================
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 책이 없습니다.")
else:
    books = list(reversed(st.session_state.books))

    total_h = sum(b["height"] for b in books) + 1
    fig_h = max(5, total_h * 0.7)

    fig, ax = plt.subplots(figsize=(8, fig_h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, total_h)
    ax.invert_yaxis()

    y = 0.3
    for b in books:
        draw_book(
            ax,
            x=2 + b["x_offset"],
            y=y,
            w=6,
            h=b["height"],
            color=b["color"],
            title=shorten_title(b["title"])
        )
        y += b["height"]  # 간격 0 → 딱 붙기

    ax.axis("off")

    # PNG로 저장 후 st.image로 출력 (스크롤 가능)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    st.image(buf)


# ================================================================
# 10) 초기화 버튼
# ================================================================
if st.button("모든 책 초기화"):
    st.session_state.books = []
    st.experimental_rerun()
