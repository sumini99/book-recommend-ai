import streamlit as st
import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import random

# -----------------------------
# 1) 폰트 설정 (경로는 리포에 올린 kyoboson.ttf)
# -----------------------------
FONT_PATH = "kyoboson.ttf"
font_prop = fm.FontProperties(fname=FONT_PATH)

# -----------------------------
# 2) 알라딘 API 검색 함수
# -----------------------------
def search_books(title, author=None):
    TTBKEY = st.secrets["aladin"]["aladin_key"]

    query = title
    if author and len(author.strip()) > 0:
        query += " " + author

    url = (
        "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
        f"?ttbkey={TTBKEY}"
        f"&Query={query}"
        "&QueryType=Keyword"
        "&MaxResults=5"
        "&start=1"
        "&SearchTarget=Book"
        "&output=xml"
        "&Version=20131101"
    )

    res = requests.get(url)

    if res.status_code != 200:
        return []

    try:
        root = ET.fromstring(res.text)
    except:
        return []

    items = []
    for item in root.findall("item"):
        title = item.findtext("title", "")
        author = item.findtext("author", "")
        cover = item.findtext("cover", "")
        pages = item.findtext("subInfo/paperBookList/priceSales")  # 페이지 정보 대체필드 없어서 임시
        publisher = item.findtext("publisher", "")

        # 페이지수 미지원 → 임의 250 입력 (동일 책은 길이가 비슷함)
        try:
            pages = int(pages)
        except:
            pages = 250

        items.append({
            "title": title,
            "author": author,
            "cover": cover,
            "publisher": publisher,
            "pages": pages
        })

    return items


# -----------------------------
# 3) 세션 초기화
# -----------------------------
if "books" not in st.session_state:
    st.session_state.books = []

# -----------------------------
# 4) UI - 제목/저자 입력
# -----------------------------
st.title("📚 책 쌓기 프로젝트")

title_input = st.text_input("책 제목 입력")
author_input = st.text_input("저자 검색 (선택)")

search_btn = st.button("🔍 알라딘에서 검색")

selected_book = None

# -----------------------------
# 5) 검색 처리
# -----------------------------
if search_btn:
    results = search_books(title_input, author_input)

    if not results:
        st.error("검색 결과가 없습니다.")
    else:
        st.success("검색 결과를 찾았습니다!")

        for idx, book in enumerate(results):
            with st.container():
                st.write(f"### 📘 {idx+1}. {book['title']}")
                st.write(f"저자: {book['author']}")
                st.write(f"출판사: {book['publisher']}")
                st.image(book["cover"], width=120)

                if st.button(f"📌 이 책 선택하기 {idx+1}", key=f"select_{idx}"):
                    selected_book = book
                    st.session_state.books.append({
                        "title": book["title"],
                        "author": book["author"],
                        "pages": book["pages"],
                        "color": "#" + ''.join(random.choices("89ABCDEF", k=6))
                    })
                    st.rerun()

# -----------------------------
# 6) 책 쌓기 시각화
# -----------------------------
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = list(reversed(st.session_state.books))

    fig, ax = plt.subplots(figsize=(10, len(books) * 1.2))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 1.3 + 1)
    ax.invert_yaxis()

    y = 1
    toggle = 1

    for i, bk in enumerate(books):

        # 제목 글자 너무 길면 ... 처리
        display_title = bk["title"]
        if len(display_title) > 32:
            display_title = display_title[:29] + "..."

        # 페이지수를 기반으로 높이 조금 증가
        height = 1.1 + (bk["pages"] / 2000)

        x_shift = (i % 3) * 0.7 * toggle
        toggle *= -1

        rect = plt.Rectangle((3 + x_shift, y), 6, height, color=bk["color"], ec="black", linewidth=2)
        ax.add_patch(rect)

        ax.text(
            3 + x_shift + 3,
            y + height/2,
            display_title,
            fontproperties=font_prop,
            fontsize=14,
            ha="center",
            va="center",
            weight="bold"
        )

        y += height + 0.1

    ax.axis("off")
    st.pyplot(fig)
