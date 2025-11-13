import requests
import xml.etree.ElementTree as ET
import streamlit as st

def search_books(query):
    TTBKEY = st.secrets["aladin"]["aladin_key"]

    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": TTBKEY,
        "Query": query,
        "QueryType": "Keyword",
        "MaxResults": 5,
        "SearchTarget": "Book",
        "output": "xml",
        "Version": "20131101"
    }

    res = requests.get(url, params=params)

    try:
        root = ET.fromstring(res.text)
    except:
        return []

    # XML namespace 정의
    ns = {'ns': 'http://www.aladin.co.kr/ttb/apiguide.aspx'}

    # item 태그 찾기
    items = root.findall(".//ns:item", ns)

    results = []
    for item in items:
        title = item.find("ns:title", ns)
        author = item.find("ns:author", ns)
        cover = item.find("ns:cover", ns)
        pubdate = item.find("ns:pubDate", ns)
        isbn13 = item.find("ns:isbn13", ns)

        results.append({
            "title": title.text if title is not None else "",
            "author": author.text if author is not None else "",
            "cover": cover.text if cover is not None else "",
            "pubdate": pubdate.text if pubdate is not None else "",
            "isbn13": isbn13.text if isbn13 is not None else "",
        })

    return results


