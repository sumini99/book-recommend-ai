import requests
import xml.etree.ElementTree as ET
import streamlit as st

def search_books(title):
    """
    제목으로 알라딘 검색 → 최대 5개의 후보 반환
    """
    TTBKEY = st.secrets["aladin"]["aladin_key"]

    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": TTBKEY,
        "Query": title,
        "QueryType": "Title",
        "SearchTarget": "Book",
        "MaxResults": 5,
        "output": "xml",
        "Version": "20131101"
    }

    res = requests.get(url, params=params)
    if res.status_code != 200:
        return []

    root = ET.fromstring(res.text)
    items = root.findall("item")

    results = []

    for item in items:
        info = {
            "title": item.findtext("title"),
            "author": item.findtext("author"),
            "cover": item.findtext("cover"),
            "description": item.findtext("description"),
            "publisher": item.findtext("publisher"),
            "link": item.findtext("link"),
        }

        # 페이지 수 파싱
        sub_info = item.find("subInfo")
        if sub_info is not None:
            pages = sub_info.findtext("itemPage")
            info["pages"] = int(pages) if pages and pages.isdigit() else 120
        else:
            info["pages"] = 120

        results.append(info)

    return results


