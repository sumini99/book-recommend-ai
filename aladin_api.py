import requests
import streamlit as st

def search_books(keyword):
    TTBKEY = st.secrets["aladin"]["aladin_key"]
    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"

    params = {
        "ttbkey": TTBKEY,
        "Query": keyword,
        "QueryType": "Keyword",   # 제목+저자 전체 검색
        "MaxResults": 5,
        "start": 1,
        "SearchTarget": "Book",
        "output": "JS",
        "Version": "20131101"
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return []

    data = response.json()

    # 검색 결과 없음
    if "item" not in data:
        return []

    results = []
    for item in data["item"]:
        results.append({
            "title": item.get("title", ""),
            "author": item.get("author", ""),
            "publisher": item.get("publisher", ""),
            "cover": item.get("cover", ""),
            "pages": int(item.get("subInfo", {}).get("itemPage", 180)),  # 없으면 기본 180
        })

    return results



