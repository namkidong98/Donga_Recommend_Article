from langchain_milvus.utils.sparse import BM25SparseEmbedding
from pymilvus.model.sparse import BM25EmbeddingFunction
from kiwipiepy import Kiwi
from kiwipiepy.utils import Stopwords
from typing import List

class Kiwi_Tokenizer:
    def __init__(self, dict_path : str):
        self.kiwi = Kiwi(num_workers=0, model_type='sbg') # SkipBigram(sbg)
        self.stopwords = Stopwords()
        self.kiwi.load_user_dictionary(dict_path=dict_path)

    def __call__(self, sent : str) -> List[str]:
        tokens = self.kiwi.tokenize(sent, stopwords=self.stopwords)
        return [token.form for token in tokens]
    
class Custom_BM25(BM25SparseEmbedding):
    def __init__(self, corpus: List[str], tokenizer):
        # super().__init__(corpus=corpus) # fit도 자동으로 하기 때문에 이를 분리하기 위해 __init__은 overriding
        self.corpus = corpus
        self.analyzer = tokenizer # default로 설정된 build_default_analyer가 아닌, 입력된 tokenizer를 analyzer로 설정
        self.bm25_ef = BM25EmbeddingFunction(self.analyzer, num_workers=1)
    
    # corpus에 대해 analyzer를 이용하여 학습하여 BM25 모델을 생성하는 메소드
    def fit(self):
        self.bm25_ef.fit(self.corpus)
    
    # corpus에 대해 fit된 모델을 저장하는 메소드
    def save(self, filename : str):
        self.bm25_ef.save(filename)
    
    # fit된 모델을 로드하는 메소드
    def load(self, filename : str):
        self.bm25_ef.load(filename)