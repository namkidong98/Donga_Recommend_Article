# Donga_Recommend_Article
Based on article data(동아일보), a system that receives the draft of the article as input and automatically recommends related articles 

<br>

# Pipeline
<img width="900" alt="pipeline" src="https://github.com/user-attachments/assets/da8de85f-bee9-42e1-add8-dfed009460a2">

1. 기자가 CMS(기사 작성 프로그램)에서 기사의 초안을 완성한다
2. 기사 초안에 대한 ‘관련 기사 추천’ 기능을 사용한다(필요시 날짜, 기자와 같은 필터링을 설정)
3. 서버에서 해당 기사 초안을 받아 ChatGPT 4o를 이용해 일정 분량(700~900자)으로 요약하고 이를 임베딩하여 벡터를 만든다 (필터링용 데이터가 있다면 같이 전송)
4. 서버가 VectorDB에 해당 벡터를 Query로 사용하여 관련 기사를 검색한다(필터링용 데이터가 있다면 메타 데이터 필터링을 수행)
5. 5개의 관련 기사를 검색하여 해당 기사의 요약문, 기자, 작성일, 링크 등을 CMS에 반환하고 이를 토대로 기자가 ‘관련 기사’를 선정한다

<br>

# Detail Description for each file
1. crawling.ipynb
    - 동아일보 2024년 기사 링크를 기반으로 크롤링하여 id, title, date, content, link로 이루어진 sqlite DB를 구축
    - dataset/2024.csv가 있으면 생략 가능, dataset은 <a href="https://huggingface.co/datasets/kidong98/news_article_donga2024">huggingface</a>에서 다운 가능

2. preprocessing.ipynb
    - title(기사 제목), content(기사 본문)에 대한 전처리 과정
    - 한자 변환(<a href="https://blog.naver.com/rlehd201/223525538408">hanja</a> 라이브러리 설치), 특수문자 변환(dataset/2024_norm.csv)
    - 이후 Dense Embedding의 성능을 높이기 위해 권장되는 토큰 수에 맞추기 위해 content 450자 기준 split(dataset/2024_norm_split.csv)

3. KPF-BERT-NER.ipynb
    - 한국언론진흥재단이 개발한 KPFBERT기반의 <a href="https://github.com/KPF-bigkinds/BIGKINDS-LAB/tree/main/KPF-BERT-NER">NER모델</a>을 이용한 기사본문 NER
      - 기사 데이터를 기반으로 학습한 KPFBERT이기 때문에 해당 Task에 가장 적합한 모델이라 판단
    - Colab에서 진행하였으며, 3만 개 기사를 450자 split한 7만개 행의 데이터에 대해 총 3~4시간 소요(dataset/2024_norm_split_ner.csv)

4. Kiwi_customizing.ipynb
    - 길이가 짧아 정보성이 부족한 기사(100~150자, 주로 행사 소개 or 간단한 소식 전달 수준)를 제거(dataset/2024_norm_split_ner_pruning.csv)
    - NER 결과 빈도 분석으로 유효한 어휘 모음 추출(3만개의 기사에서 추출된 NER 100만개, 중복없이 11만개, 빈도수 10 미만 제거하여 최종적으로 약 2만개)
    - NER 기반 유효한 어휘 모음(2만개)를 Kiwi 형태소 분석기 사전에 추가하여 Custom 형태소 분석기 제작(model/custom_dict.txt)

5. BM25_model.ipynb
    - 기사 본문(2024_norm_split.csv), Custom Kiwi 형태소 분석기를 각각 Corpus, Analyzer로 지정
    - Corpus, Analyzer를 이용하여 BM25 모델 생성, 학습(2시간 소요), 저장(model/bm25_model.json)

6. milvus_create_insert.ipynb
    - Sparse Embedding Model로 5번의 Custom BM25 모델을, Dense Embedding Model로 <a href="https://blog.naver.com/rlehd201/223520177857">Upstage/solar-embedding-1-large</a>를 이용
    - <a href="https://blog.naver.com/rlehd201/223520050648">Docker를 이용하여 Milvus Container를 생성 및 실행</a>하고 'Donga' Collection 생성
    - 기사 본문(dataset/2024_norm_split_ner_pruning.csv)을 Sparse/Dense Embedding하고 'Donga' Collection에 삽입(3~4시간 소요)

7. vector_search.ipynb
    - 구축한 Milvus Collection('Donga')에 <a href="https://python.langchain.com/v0.2/docs/integrations/retrievers/milvus_hybrid_search/">HybridSearchRetriever</a>로 vector search 수행(연관 기사 검색)
    - 현재 개발한 Hybridsearch 버전(Donga)과 <a href="https://github.com/namkidong98/Milvus_Practice/blob/main/milvus_800.ipynb">Basic 버전(Donga_800)</a>과의 비교
    - 일단, 짧은 질문 형태의 query 기반으로 연관 기사 검색 및 추천을 실행

8. document_input_compare.ipynb
    - 짧은 질문 형태의 query 대신, 평균 1500~3000자 길이의 기사 초안(draft)이 들어온다고 가정하고 그에 맞게 Retriever 구조 변경
    - DB에 없는 최근 기사의 본문을 ChatGPT 4o를 이용하여 700~900자 분량으로 요약하고 이를 input으로 하여 '연관 기사 검색 및 추천' 기능 테스트
    - Basic 버전(Donga_800)과 Hybridsearch 버전(Donga) 사이의 차이를 비교
    - <img width="700" alt="1" src="https://github.com/user-attachments/assets/9c32b1a7-40af-4bdf-b6e1-df7350188ef4">

<br>

# 향후 발전 방향
1. FastAPI를 이용한 서버 개발 및 Milvus를 Azure 클라우드에 배포하여 API 형태로 제공

2. 연관 기사 검색 옵션으로 '지난 7일', '지난 1달', '지난 1년', '지난 3년'을 추가하여 작성된 기사 원고에 맞는 '연관 기사 검색' 기능 구현
    - 당시의 화제성 있는 이슈를 다루는 기사의 경우, '지난 7일'처럼 짧은 기간으로 설정하는 것이 검색 및 추천 성능을 높일 것으로 기대
    - 과거 사건들과의 연관성을 비교(ex. 이태원 참사, 미연준 금리 변동 등)하는 기사의 경우, '지난 1년', '지난 3년'처럼 비교적 긴 기간으로 설정하는 것이 성능 향상에 도움이 될 것으로 기대
