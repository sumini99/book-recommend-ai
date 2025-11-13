import requests
import xml.etree.ElementTree as ET
import streamlit as st

def search_books(title, author=""):
    TTBKEY = st.secrets["aladin"]["aladin_key"]

    if author:
        query = f"{title} {author}"
    else:
        query = title

    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": TTBKEY,
        "Query": query,
        "QueryType": "Keyword",
        "MaxResults": 5,
        "start": 1,
        "SearchTarget": "Book",
        "output": "xml",
        "Version": "20131101"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    try:
        root = ET.fromstring(response.text)
    except:
        return []

    results = []

    for item in root.findall(".//item"):
        title = item.findtext("title", default="제목 없음")
        author = item.findtext("author", default="저자 정보 없음")
        publisher = item.findtext("publisher", default="출판사 정보 없음")
        image = item.findtext("cover", default="")
        link = item.findtext("link", default="")

        # 🔥 안전한 페이지 수 처리
        pages = 200  # 기본값
        try:
            subinfo = item.find("subInfo")
            if subinfo is not None:
                paper = subinfo.find("paperbook")
                if paper is not None:
                    p = paper.findtext("pages")
                    if p and p.isdigit():
                        pages = int(p)
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
