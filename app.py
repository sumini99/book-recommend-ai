import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import random

st.set_page_config(page_title="책 시각화 보드", page_icon="📚")

# -------- 한글 폰트 로드 (repo 루트에 위치) --------
font_path = "kyboson.ttf"  # 루트에 넣은 폰트 파일 이름
font_prop = fm.FontProperties(fname=font_path)
fm.fontManager.addfont(font_path)
plt.rc('font', family=font_prop.get_name())
# ---------------------------------------------

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
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    fig_height = max(4, len(st.session_state.books) * 1.5)
    fig, ax = plt.subplots(figsize=(8, fig_height))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(st.session_state.books) * 1.6 + 2)
    ax.invert_yaxis()

    y = 1

    for book in st.session_state.books:
        color = book["color"]

        # 사각형 박스
        rect = plt.Rectangle((1, y), 8, 1.3, color=color, ec="black", linewidth=2)
        ax.add_patch(rect)

        # 텍스트
        ax.text(
            1.4, y + 0.85,
            f"{book['title']} - {book['author']}",
            fontsize=14,
            color="black",
            fontproperties=font_prop,
            fontweight="bold"
        )

        y += 1.6

    ax.axis("off")
    st.pyplot(fig)
