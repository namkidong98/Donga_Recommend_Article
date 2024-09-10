from langchain_milvus.retrievers import MilvusCollectionHybridSearchRetriever
from pymilvus import WeightedRanker
from bs4 import BeautifulSoup
import requests, os
from openai import OpenAI
from model.bm25_model import Custom_BM25, Kiwi_Tokenizer
from langchain_upstage import UpstageEmbeddings
from dotenv import load_dotenv
load_dotenv()

QUERY_MODEL = 'solar-embedding-1-large-query'
PASSAGE_MODEL = 'solar-embedding-1-large-passage'

DENSE_FIELD = "dense_vector"
DENSE_DIMENSION = 4096 
DENSE_INDEX = {"index_type" : "FLAT", "metric_type" : "IP"}

SPARSE_FILED = "sparse_vector"
SPARSE_INDEX = {"index_type" : "SPARSE_INVERTED_INDEX", "metric_type" : "IP"}

# Sparse Embedding : Custom BM25
tokenizer = Kiwi_Tokenizer("model/custom_dict.txt")
custom_bm25 = Custom_BM25(corpus=[], tokenizer=tokenizer)
custom_bm25.load("model/bm25_model.json")

# Dense Embedding : Upstage/solar-embedding-1-large
dense_embedding_func = UpstageEmbeddings(
    model=PASSAGE_MODEL,
    upstage_api_key=os.getenv("UPSTAGE_API_KEY")
)

openai_client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY") # OPENAI API KEY
)

def hybrid_search(collection, query, filter):
    try:
        sparse_search_params = {"metric_type": "IP"}
        dense_search_params = {"metric_type": "IP", "params": {}}

        params = {
            "collection" : collection,
            "rerank" : WeightedRanker(0.7, 0.3),
            "anns_fields" : [DENSE_FIELD, SPARSE_FILED],
            "field_embeddings" : [dense_embedding_func, custom_bm25],
            "field_search_params" : [dense_search_params, sparse_search_params],
            "top_k" : 20,
            "text_field" : 'content',
        }
        if filter:
            params['field_exprs'] = [filter, filter] # 검색 조건 추가(dense와 sparse에 동일하게 적용)
        retriever = MilvusCollectionHybridSearchRetriever(**params)
        
        retrieved_docs = retriever.invoke(query)
        data = []
        unique_id = []
        for retreived_doc in retrieved_docs:
            doc_id = retreived_doc.metadata['id'].split("_")[0] # 기사 고유 ID 추출
            if doc_id not in unique_id: # 해당 기사가 아직 반환 리스트에 없는 경우만
                data.append(retreived_doc)
                unique_id.append(doc_id)
            if len(data) == 5: break # 상위 5개만 반환
        return data
    except Exception as e:
        print(e)
        return None

def crawling(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청에 실패하면 예외 발생
        soup = BeautifulSoup(response.text, 'html.parser')
        article_section = soup.find('section', class_='news_view')
        
        if article_section:
            # 광고 등 불필요한 태그를 제거
            for ad in article_section.find_all(['div', 'script', 'figure']):
                ad.decompose()
            
            # 남은 텍스트 추출
            article_text = article_section.get_text(separator=' ', strip=True)
            return article_text
        else:
            return None
    except requests.RequestException as e:
        print(f"HTTP 요청 실패: {e}")
        return None

def summarize(content):
    system_prompt = """
    당신은 기사를 요약해주는 챗봇으로 기사 본문을 제공받아 핵심 요점을 요약하는 업무를 수행해야 합니다.
    고유명사는 되도록 포함해야 하며, 한국어 기준 700자 분량의 요약을 해야 합니다.
    """

    # 프롬프트 예제
    user_prompt = f"""
    "기사 본문" : {content}
    "요약" :
    """
    try:
        # ChatGPT API 호출
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
        )
        response_text = response.choices[0].message.content.strip()
        return response_text
    except Exception as e:
        print(e)
        return None