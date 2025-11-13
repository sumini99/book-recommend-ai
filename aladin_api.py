import requests
import xml.etree.ElementTree as ET
import streamlit as st


def search_book_from_aladin(title, author):
    """
    알라딘 API로 책 검색해서 1번째 결과 반환
    title + author를 함께 검색 (정확도 높음)
    """
    TTBKEY = st.secrets["aladin"]["TTBKEY"]   # 👉 Streamlit Secrets 에서 불러옴

    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": TTBKEY,
        "Query": f"{title} {author}",
        "QueryType": "Keyword",
        "SearchTarget": "Book",
        "MaxResults": 1,
        "output": "xml",
        "Version": "20131101"
    }

    res = requests.get(url, params=params)
    if res.status_code != 200:
        return None

    root = ET.fromstring(res.text)
    item = root.find("item")

    if item is None:
        return None

    data = {
        "title": item.findtext("title"),
        "author": item.findtext("author"),
        "cover": item.findtext("cover"),
        "description": item.findtext("description"),
        "link": item.findtext("link")
    }

    # 페이지 수는 subInfo 아래에 들어 있음
    sub_info = item.find("subInfo")
    if sub_info is not None:
        pages = sub_info.findtext("itemPage")
        data["pages"] = int(pages) if pages and pages.isdigit() else 100
    else:
        data["pages"] = 100  # 기본값

    return data
