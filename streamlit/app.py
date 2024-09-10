import streamlit as st
from inference import crawling, summarize, hybrid_search
from milvus_connect import milvus_connect
from datetime import datetime
from dateutil.relativedelta import relativedelta

def option_to_filter(option):
    # ["지정 안함", "지난 7일", "지난 1달", "지난 3달", "지난 6달", "지난 1년"]
    today = datetime.today()
    start_day = None
    filter = "date >= " # milvus에 적용할 필터 형식
    if option == '지정 안함':
        filter = None
    if option == '지난 7일':
        start_day = today - relativedelta(weeks=1)
        filter += start_day.strftime("%Y%m%d")
    if option == '지난 1달':
        start_day = today - relativedelta(months=1)
        filter += start_day.strftime("%Y%m%d")
    if option == '지난 3달':
        start_day = today - relativedelta(months=3)
        filter += start_day.strftime("%Y%m%d")
    if option == '지난 6달':
        start_day = today - relativedelta(months=6)
        filter += start_day.strftime("%Y%m%d")
    if option == '지난 1년':
        start_day = today - relativedelta(months=12)
        filter += start_day.strftime("%Y%m%d")
    return filter

def milvus_hybrid(input, crawl=False, filter=None):
    try:
        if crawl: # 들어온 입력이 URL인 경우
            content = crawling(input)
        else: # 들어온 입력이 draft인 경우
            content = input
        if not content: 
            raise Exception("Article not found")
        summary = summarize(content)
        if not summary: 
            raise Exception("Summarization Error")
        collection = milvus_connect("Donga")
        result = hybrid_search(collection, summary, filter=filter) 
        entities = []
        for article in result:    
            data = {
                'id' : article.metadata['id'],
                'title' : article.metadata['title'],
                'date' : article.metadata['date'],
                'content' : article.page_content,
                'NER' : article.metadata['NER']
            }
            entities.append(data)
        return entities
    except:
        return "유효하지 않은 입력입니다"

# Streamlit 애플리케이션 시작
st.title("관련 기사 추천")

# 사용자 입력 받기
url_input = st.text_input("동아닷컴 기사 URL을 입력하세요")
draft_input = st.text_area("기사의 초안을 입력하세요", height=200)

option = st.selectbox("날짜 옵션을 선택하세요:", ["지정 안함", "지난 7일", "지난 1달", "지난 3달", "지난 6달", "지난 1년"])

if st.button("관련 기사 검색"):
    filter = option_to_filter(option)
    if url_input:
        st.header("Milvus HybridSearch")
        output_1 = milvus_hybrid(url_input, crawl=True, filter=filter)
        st.write(output_1)
    else: # draft_input
        st.header("Milvus HybridSearch")
        output_1 = milvus_hybrid(draft_input, crawl=False, filter=filter)
        st.write(output_1)