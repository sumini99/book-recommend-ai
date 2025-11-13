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

    ns = {'ns': 'http://www.aladin.co.kr/ttb/apiguide.aspx'}
    items = root.findall(".//ns:item", ns)

    results = []
    for item in items:
        def get_value(tag):
            node = item.find(f"ns:{tag}", ns)
            return node.text if node is not None else ""

        results.append({
            "title": get_value("title"),
            "author": get_value("author"),
            "cover": get_value("cover"),
            "publisher": get_value("publisher"),
            "pubdate": get_value("pubDate"),
            "isbn": get_value("isbn"),
            "isbn13": get_value("isbn13"),
            "price": get_value("priceSales"),
            "link": get_value("link"),
            "pages": get_value("subInfo/ns:itemPage"),  # 페이지수 (없을 수도 있음)
        })

    return results
