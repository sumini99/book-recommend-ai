import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
import random
from aladin_api import search_books


# ================================================================
# 0) 기본 UI 스타일
# ================================================================
def local_css(css_text: str):
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
.stTextInput>div>div>input {
    background: #2c2c2c !important;
    color: white !important;
    border-radius: 8px;
    padding: 10px;
}
""")


# ================================================================
# 1) 한글 폰트 로드
# ================================================================
font_path = "kyoboson.ttf"
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)


# ================================================================
# 2) 유틸 함수들
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

def pastel_color() -> str:
    return random.choice(PALETTE)

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

def shorten_title(title: str, max_len: int = 24) -> str:
    return title if len(title) <= max_len else title[:max_len] + "..."


# ================================================================
# 3) 책 하나 그리는 함수 (사각형 + 살짝 라운드 + 그림자)
# ================================================================
def draw_book(ax, x, y, width, height, color, title):
    """
    살짝 둥근 사각형 + 얇은 그림자.
    모양 이상해지는 거 방지하려고 라운드는 아주 작게만 줌.
    """

    # 그림자 (뒤쪽, 약간 아래/오른쪽으로)
    shadow = FancyBboxPatch(
        (x + 0.1, y + 0.1),
        width,
        height,
        boxstyle="round,pad=0,rounding_size=2",  # 거의 사각형
        linewidth=0,
        facecolor=(0, 0, 0, 0.18),
        zorder=1,
    )
    ax.add_patch(shadow)

    # 책 본체
    body = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0,rounding_size=2",  # 살짝 둥근 정도만
        linewidth=1.5,
        edgecolor="#333333",
        facecolor=color,
        zorder=2,
    )
    ax.add_patch(body)

    # 제목 텍스트
    ax.text(
        x + width / 2,
        y + height / 2,
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
# 4) Streamlit 기본 설정 (⚠ wide 모드 끔!)
# ================================================================
st.set_page_config(page_title="책 쌓기", layout="centered")
st.markdown("<h1 class='page-title'>📚 AI 기반 알라딘 책검색 + 책탑 쌓기</h1>", unsafe_allow_html=True)

# 세션 상태 초기화
if "books" not in st.session_state:
    st.session_state.books = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# ================================================================
# 5) 검색 UI
# ================================================================
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
        st.warning("책 제목을 입력해야 검색됩니다.")


# ================================================================
# 6) 검색 결과 표시
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
            st.image(book["cover"], width=140)

            if st.button(f"이 책 선택하기 ({idx+1})"):
                st.session_state.selected_book = book

            st.markdown("</div>", unsafe_allow_html=True)


# ================================================================
# 7) 책 선택 → 책탑에 추가
# ================================================================
selected = st.session_state.selected_book

if selected:
    st.success(f"'{selected['title']}'를 책탑에 추가합니다!")

    pages = safe_int(selected.get("pages"))
    # 너무 차이나지 않게 두께 범위 제한
    height = 0.9 + min(pages / 1200, 0.7)   # 0.9 ~ 1.6 정도

    idx = len(st.session_state.books)
    direction = 1 if idx % 2 == 0 else -1
    x_offset = (idx % 3) * 0.8 * direction   # 좌우 살짝만 움직이게

    st.session_state.books.append({
        "title": selected["title"],
        "height": height,
        "color": pastel_color(),
        "x_offset": x_offset,
    })

    st.session_state.selected_book = None


# ================================================================
# 8) 책탑 시각화 (책 사이 간격 0으로 쌓기)
# ================================================================
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    # 최근 책이 위로 오도록
    books = list(reversed(st.session_state.books))

    # 전체 높이 계산 → 그래프가 잘리지 않도록
    total_height = sum(book["height"] for book in books) + 1

    fig_height = max(4, total_height * 0.6)  # 책 많을수록 자동으로 세로 길어짐
    fig, ax = plt.subplots(figsize=(8, fig_height))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, total_height + 0.5)
    ax.invert_yaxis()

    # 책 사이 간격 0 → 바로바로 위에 쌓기
    y = 0.5
    for book in books:
        draw_book(
            ax,
            x=2 + book["x_offset"],
            y=y,
            width=6,
            height=book["height"],
            color=book["color"],
            title=shorten_title(book["title"]),
        )
        y += book["height"]  # ✅ 추가 간격 없이 딱 붙이기

    ax.axis("off")
    st.pyplot(fig, use_container_width=True)


# ================================================================
# 9) 전체 초기화 버튼
# ================================================================
if st.button("모든 책 초기화"):
    st.session_state.books = []
    st.experimental_rerun()
