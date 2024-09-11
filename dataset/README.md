## Dataset Link(HuggingFace)
https://huggingface.co/datasets/kidong98/Donga_Article

<br>

## Dataset Summary

기본적으로 동아일보의 기사를 크롤링하여 기사 제목, 기사 본문, 기사의 고유 ID, 기사 링크를 추출하여 생성한 데이터셋입니다.   
2023년, 2024년 기사 데이터로 구성되어 있으며, 기본 csv파일을 기준으로 '_$$$'와 같이 적용된 기능에 따라 파일이 추가되어 있습니다.   
2023년 파일은 약 4만 5천개 가량의 2023년에 업로드된 동아닷컴의 기사를 담고 있으며, 2024년 파일은 1월부터 7월까지의 약 3만개 가량의 동아닷컴 기사를 담고 있습니다.   
'_ner'이 포함된 버전의 파일들은 한국언론진흥재단이 발표한 KPFBERT 기반의 NER 모델로 기사 본문에서 추출한 NER을 포함하고 있습니다.   
해당 데이터셋은 '관련기사 검색 및 추천' 시스템 구축을 위해 수집 및 구축되었으며 관련 프로젝트는 <a href="https://github.com/namkidong98/Donga_Recommend_Article">Github</a>를 참고하시면 됩니다.   

<br>

## Dataset columns

- id : 기사의 고유 ID(동아닷컴 URL에 포함되어 있음)
- title : 기사의 제목
- date : 기사의 업로드 날짜
- content : 기사의 본문
- NER : 기사 본문(content)에서 KPFBert기반 NER 모델로 추출한 NER

<br>

## Description for File Version

- '_norm' : 기본 csv 파일에서 기사에 등장하는 한자, 인용부호, 단위, 줄바꿈 등에 대한 정규화 전처리가 적용된 버전
- '_split' : 이전 버전에서 기사 본문 450자 기준으로 분할되고 각 블록의 index를 기사 고유 ID 끝에 '_1'과 같이 구분하여 만든 버전
- '_ner' : 이전 버전의 기사 본문(content)를 이용해 KPFBert 기반 NER 모델로 추출한 NER을 새로운 column으로 추가한 버전
- '_pruning' : 이전 버전에서 150자 이하의 정보성이 부족한 데이터를 제거한 버전

<br>
