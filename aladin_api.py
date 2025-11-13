import requests
import xml.etree.ElementTree as ET
import streamlit as st


def search_books(title, author=""):
    TTBKEY = st.secrets["aladin"]["aladin_key"]

    # 검색어 조합 (저자 입력하면 함께 검색)
    if author:
        query = f"{title} {author}"
    else:
        query = title

    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": TTBKEY,
        "Query": query,
        "QueryType": "Keyword",     # 제목+저자 모두 대상
        "MaxResults": 5,            # 5개 가져오자
        "start": 1,
        "SearchTarget": "Book",
        "output": "xml",
        "Version": "20131101"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    root = ET.fromstring(response.text)

    results = []

    for item in root.findall(".//item"):
        title = item.findtext("title", default="제목 없음")
        author = item.findtext("author", default="저자 정보 없음")
        publisher = item.findtext("publisher", default="출판사 정보 없음")
        image = item.findtext("cover", default="")
        link = item.findtext("link", default="")

        # 페이지 수 추출 (없으면 200 기본값)
        pages_text = item.findtext("subInfo/paperbook/pages")
        try:
            pages = int(pages_text) if pages_text else 200
        except:
            pages = 200

        results.append({
            "title": title,
            "author": author,
            "publisher": publisher,
            "image": image,
            "link": link,
            "pages": pages
        })

    return results
