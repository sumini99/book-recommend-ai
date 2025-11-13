import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import random
import io
from aladin_api import search_books

# -------------------------------------------
# Streamlit 기본 설정 (⚠ 첫 줄 바로 아래에 위치해야 wide OFF 유지!)
# -------------------------------------------
st.set_page_config(page_title="책 쌓기", layout="centered")

# -------------------------------------------
# 폰트 로드
# -------------------------------------------
font_path = "kyoboson.ttf"  # GitHub repo 최상위에 있어야 함
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)

# -------------------------------------------
# 색상 팔레트 (Ultra Palette - 다양함 + 진함)
# -------------------------------------------
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


# -------------------------------------------
# 페이지 수 안전 변환
# -------------------------------------------
def safe_int(value, default=200):
    try:
        v = int(str(value).strip())
        return v if v > 0 else default
    except:
        return default


# -------------------------------------------
# 제목 너무 길면 줄이기
# -------------------------------------------
def shorten_title(title, max_len=22):
    return title if len(title) <= max_len else title[:max_len] + "..."


# -------------------------------------------
# 책(직사각형) 그리기
# -------------------------------------------
def draw_book(ax, x, y, width, height, color, title):
    # 그림자 (아래)
    shadow = patches.Rectangle(
        (x + 0.15, y - 0.15),
        width,
        height,
        linewidth=0,
        facecolor="black",
        alpha=0.20,
    )
    ax.add_patch(shadow)

    # 책 본체
    rect = patches.Rectangle(
        (x, y),
        width,
        height,
        linewidth=2,
        edgecolor="black",
        facecolor=color
    )
    ax.add_patch(rect)

    # 제목
    ax.text(
        x + width / 2,
        y + height / 2,
        title,
        ha="center",
        va="center",
        fontsize=13,
        fontproperties=font_prop,
    )


# -------------------------------------------
# 세션 초기화
# -------------------------------------------
if "books" not in st.session_state:
    st.session_state.books = []

if "selected_book" not in st.session_state:
    st.session_state.selected_book = None


# -------------------------------------------
# 검색 UI
# -------------------------------------------
st.title("📚 AI 기반 알라딘 책검색 + 책탑 쌓기")

with st.form(key="search_form"):
    title_input = st.text_input("책 제목 입력 (필수)")
    author_input = st.text_input("저자 입력 (선택)")
    submitted = st.form_submit_button("검색하기")

if submitted:
    if title_input:
        st.session_state.search_results = search_books(title_input)
    else:
        st.warning("책 제목을 입력해야 검색됩니다.")


# -------------------------------------------
# 검색 결과 Compact 카드 UI
# -------------------------------------------
if "search_results" in st.session_state:
    results = st.session_state.search_results
    st.subheader("📘 검색 결과")

    # CSS 정의
    st.markdown("""
    <style>
        .compact-card {
            background-color: #2b2b2b;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.25);
        }
        .compact-text {
            padding-left: 14px;
        }
        .compact-title {
            font-size: 16px;
            font-weight: 600;
        }
        .compact-author {
            font-size: 13px;
            opacity: 0.85;
            margin-top: 3px;
        }
    </style>
    """, unsafe_allow_html=True)

    for idx, book in enumerate(results):
        with st.container():
            st.markdown('<div class="compact-card">', unsafe_allow_html=True)

            # 작은 표지 이미지
            st.image(book["cover"], width=70)

            # 텍스트
            st.markdown(f"""
            <div class="compact-text">
                <div class="compact-title">{idx+1}. {book['title']}</div>
                <div class="compact-author">{book['author']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # 선택 버튼
            if st.button(f"이 책 선택 ({idx+1})", key=f"select_{idx}"):
                st.session_state.selected_book = book


# -------------------------------------------
# 선택한 책 → 리스트에 추가
# -------------------------------------------
selected = st.session_state.selected_book

if selected:
    pages = safe_int(selected["pages"])
    height = 1.0 + min(pages / 1500, 0.5)

    st.session_state.books.append({
        "title": selected["title"],
        "pages": pages,
        "height": height,
        "color": random.choice(PALETTE)
    })

    st.session_state.selected_book = None


# -------------------------------------------
# 책탑 시각화 (PNG로 렌더링 → 절대 화면에서 안 짤림)
# -------------------------------------------
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = list(reversed(st.session_state.books))

    fig_height = max(5, len(books) * 1.4)
    fig, ax = plt.subplots(figsize=(8, fig_height))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(books) * 2)
    ax.axis("off")

    y = 1

    for idx, book in enumerate(books):
        x = 2 + (idx % 3) * 0.5  # 좌우 약간 흔들림
        draw_book(
            ax,
            x,
            y,
            width=6,
            height=book["height"],
            color=book["color"],
            title=shorten_title(book["title"])
        )
        y += book["height"] + 0.1

    # PNG로 변환
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    buf.seek(0)

    st.image(buf)


# -------------------------------------------
# 전체 초기화
# -------------------------------------------
if st.button("모든 책 초기화"):
    st.session_state.books = []
    st.experimental_rerun()
