import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import random
import io
from aladin_api import search_books

# -------------------------------------------
# 0) Streamlit 기본 설정 (wide 모드 끔)
# -------------------------------------------
st.set_page_config(page_title="책 쌓기", layout="centered")

# -------------------------------------------
# 1) 한글 폰트 로드
# -------------------------------------------
font_path = "kyoboson.ttf"  # repo 최상단에 위치
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)

# -------------------------------------------
# 2) 색상 팔레트 (다양 + 살짝 진한 톤 포함)
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
# 3) 유틸 함수
# -------------------------------------------
def safe_int(value, default=200):
    try:
        v = int(str(value).strip())
        return v if v > 0 else default
    except:
        return default

def shorten_title(title, max_len=22):
    return title if len(title) <= max_len else title[:max_len] + "..."

# 책(완전 직사각형 + 그림자) 그리기
def draw_book(ax, x, y, width, height, color, title):
    # 그림자
    shadow = patches.Rectangle(
        (x + 0.12, y - 0.12),
        width,
        height,
        linewidth=0,
        facecolor="black",
        alpha=0.22,
        zorder=1,
    )
    ax.add_patch(shadow)

    # 본체
    rect = patches.Rectangle(
        (x, y),
        width,
        height,
        linewidth=2,
        edgecolor="black",
        facecolor=color,
        zorder=2,
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
        zorder=3,
    )

# -------------------------------------------
# 4) 세션 초기화
# -------------------------------------------
if "books" not in st.session_state:
    # books: [{title, pages, height, color, x_offset}, ...]
    st.session_state.books = []

if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

# -------------------------------------------
# 5) 검색 UI
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
# 6) 검색 결과 Compact 카드 UI
# -------------------------------------------
if "search_results" in st.session_state:
    results = st.session_state.search_results

    if not results:
        st.error("검색 결과를 찾을 수 없습니다.")
    else:
        st.subheader("📘 검색 결과")

        # Compact 카드 CSS
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

                # 표지
                st.image(book["cover"], width=70)

                # 텍스트 영역
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
# 7) 책 선택 → 책탑 데이터에 추가
# -------------------------------------------
selected = st.session_state.selected_book

if selected:
    pages = safe_int(selected.get("pages"))
    height = 1.0 + min(pages / 1500, 0.6)  # 1.0 ~ 1.6 사이 두께

    # 이 시점의 index 기준으로 x_offset 딱 한 번만 계산해서 저장
    idx = len(st.session_state.books)
    direction = 1 if idx % 2 == 0 else -1
    x_offset = (idx % 3) * 0.6 * direction  # 좌우 살짝 번갈아

    st.session_state.books.append({
        "title": selected["title"],
        "pages": pages,
        "height": height,
        "color": random.choice(PALETTE),
        "x_offset": x_offset,
    })

    # 선택 상태 초기화
    st.session_state.selected_book = None

# -------------------------------------------
# 8) 책탑 시각화 (책 위치/색상 고정)
# -------------------------------------------
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = st.session_state.books  # ⬅ 순서 그대로: 첫 책이 맨 아래, 새 책은 위로

    # 전체 높이 계산 (아래로 쌓이게)
    total_height = sum(b["height"] for b in books) + 1.5
    fig_height = max(5, total_height * 0.6)

    fig, ax = plt.subplots(figsize=(8, fig_height))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, total_height)
    ax.axis("off")

    # 맨 아래에서부터 위로 쌓기
    y = 0.5
    for b in books:
        draw_book(
            ax,
            x=2 + b["x_offset"],   # ⬅ 저장된 x_offset 그대로 사용 (절대 안 바뀜)
            y=y,
            width=6,
            height=b["height"],
            color=b["color"],      # ⬅ 저장된 색 그대로
            title=shorten_title(b["title"])
        )
        y += b["height"] + 0.1    # 책 사이 거의 붙게

    # PNG로 렌더링 → 화면에서 안 잘리게
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches=None, pad_inches=0)

    buf.seek(0)
    st.image(buf)

# -------------------------------------------
# 9) 전체 초기화 버튼
# -------------------------------------------
if st.button("모든 책 초기화"):
    st.session_state.books.clear()
    st.session_state.selected_book = None
    st.stop()
