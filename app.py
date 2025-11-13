import streamlit as st
import requests
import xml.etree.ElementTree as ET
import random
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# -------------------------
# 폰트 설정 (kyoboson.ttf)
# -------------------------
font_path = "kyoboson.ttf"
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)

# --------------------------------------------------------
# 알라딘 API 검색 함수
# --------------------------------------------------------
def search_books(query):
    TTBKEY = st.secrets["aladin"]["aladin_key"]

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

    root = ET.fromstring(res.text)

    items = root.findall(".//item")
    results = []

    for item in items:
        title = item.findtext("title", default="제목 없음")
        author = item.findtext("author", default="저자 정보 없음")
        cover = item.findtext("cover", default="")
        publisher = item.findtext("publisher", default="")
        isbn = item.findtext("isbn", default="")
        pages = 180  # 기본값 (Page정보 없음 → 임시)

        results.append({
            "title": title,
            "author": author,
            "cover": cover,
            "publisher": publisher,
            "isbn": isbn,
            "pages": pages
        })

    return results


# -------------------------
# 세션 상태 초기화
# -------------------------
if "books" not in st.session_state:
    st.session_state.books = []


# -------------------------
# UI 입력 영역
# -------------------------
st.title("📚 책 쌓기 프로젝트")

title_input = st.text_input("책 제목 입력")
search_btn = st.button("🔍 알라딘에서 검색")

selected_book = None

if search_btn and title_input:
    results = search_books(title_input)

    if not results:
        st.error("검색 결과가 없습니다.")
    else:
        st.subheader("📘 이 책이 맞나요?")
        for idx, book in enumerate(results):
            with st.container():
                st.write(f"### {idx+1}. {book['title']}")
                st.write(f"저자: {book['author']}")
                if book["cover"]:
                    st.image(book["cover"], width=150)

                if st.button(f"📚 이 책 쌓기 (선택 {idx+1})"):
                    selected_book = book
                    break

# -------------------------
# 선택된 책 저장
# -------------------------
if selected_book:
    # 랜덤 색상
    color = "#" + ''.join([random.choice("89ABCDEF") for _ in range(6)])

    # 책 높이 (페이지 기반)
    height = max(1.2, selected_book["pages"] / 200)

    # 책 데이터를 session_state에 저장
    st.session_state.books.append({
        "title": selected_book["title"],
        "author": selected_book["author"],
        "pages": selected_book["pages"],
        "color": color,
        "height": height
        # x_offset은 밑의 시각화하면서 자동 생성
    })

    st.success(f"'{selected_book['title']}' 선택됨! 아래에 쌓입니다.")


# =========================================================
# 📚 책 시각화
# =========================================================
st.subheader("📚 내가 쌓은 책들")

if not st.session_state.books:
    st.info("아직 쌓인 책이 없습니다.")
else:
    books = list(reversed(st.session_state.books))

    fig_height = max(5, len(books) * 1.3)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(books) * 2 + 1)
    ax.invert_yaxis()

    y = 1

    for idx, book in enumerate(books):
        color = book["color"]
        thickness = book["height"]

        # 책 좌표 고정 (한번 정해지면 변화 X)
        if "x_offset" not in book:
            offset_index = idx % 3
            offset_direction = -1 if (idx % 2 == 0) else 1
            book["x_offset"] = offset_index * 1.2 * offset_direction

        x_offset = book["x_offset"]

        # 말줄임표 처리
        title = book["title"]
        if len(title) > 18:
            title = title[:18] + "..."

        # 책 박스
        rect = plt.Rectangle(
            (3 + x_offset, y),
            6,
            thickness,
            color=color,
            ec="black",
            linewidth=2
        )
        ax.add_patch(rect)

        # 텍스트 중앙 정렬
        ax.text(
            3 + x_offset + 3,
            y + thickness / 2,
            title,
            fontsize=13,
            color="black",
            fontproperties=font_prop,
            weight="bold",
            ha="center",
            va="center"
        )

        # 책 간격 딱 붙게
        y += thickness + 0.05

    ax.axis("off")
    st.pyplot(fig)
