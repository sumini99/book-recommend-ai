import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random
import os

st.set_page_config(page_title="책 시각화 보드", page_icon="📚")

# -------- 한글 폰트 로드 (repo 루트의 kyoboson.ttf) --------
font_path = "kyoboson.ttf"

if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    fm.fontManager.addfont(font_path)
    plt.rc('font', family=font_prop.get_name())
else:
    st.warning("⚠️ 폰트 파일을 찾을 수 없습니다. (kyoboson.ttf)")
    font_prop = None
# ------------------------------------------------------------

st.title("📚 내 책 쌓기(시각화)")

# ---- Session State ----
if "books" not in st.session_state:
    st.session_state.books = []

# ---- 입력 영역 ----
st.subheader("📌 책 정보 입력")

title = st.text_input("책 제목")
author = st.text_input("저자")

if st.button("책 추가하기"):
    if title.strip() and author.strip():
        color = (random.random(), random.random(), random.random())
        st.session_state.books.append({
            "title": title,
            "author": author,
            "color": color
        })
        st.success(f"'{title}' 추가됨!")
    else:
        st.warning("제목과 저자를 모두 입력해주세요.")


# ---- 시각화 ----
# ---- 시각화 ----
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = st.session_state.books

    fig_height = max(5, len(books) * 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 1.7 + 2)
    ax.invert_yaxis()  # 0이 위로 오게 하려면 invert 필요 없음 → 제거해도 됨
    ax.invert_yaxis()  # y축 반전 유지 (캔버스 기준으로 아래→위 느낌)

    y = 1  # 아래부터 시작
    offset_direction = 1  # 좌우 번갈아 이동

    for idx, book in enumerate(books):
        color = book["color"]

        # 계단식 x 좌표
        x_offset = (idx % 3) * 1.2 * offset_direction
        offset_direction *= -1  # 방향 반전 (좌→우→좌→우)

        # 박스
        rect = plt.Rectangle((3 + x_offset, y), 6, 1.5, color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        # 텍스트 (박스 중앙)
        ax.text(
            3 + x_offset + 3,  # 박스 중앙 x
            y + 0.95,          # 박스 중앙 y
            f"{book['title']} - {book['author']}",
            fontsize=13,
            fontproperties=font_prop,
            color="black",
            weight="bold",
            ha="center",
            va="center"
        )

        y += 1.7  # 다음 박스 더 위로 이동

    ax.axis("off")
    st.pyplot(fig)
