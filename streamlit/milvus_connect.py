from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection

QUERY_MODEL = 'solar-embedding-1-large-query'
PASSAGE_MODEL = 'solar-embedding-1-large-passage'

DENSE_FIELD = "dense_vector"
DENSE_DIMENSION = 4096 
DENSE_INDEX = {"index_type" : "FLAT", "metric_type" : "IP"}

SPARSE_FILED = "sparse_vector"
SPARSE_INDEX = {"index_type" : "SPARSE_INVERTED_INDEX", "metric_type" : "IP"}

# Collection 접속 및 생성
def milvus_connect(collection_name):
    # Milvus 설정
    MILVUS_HOST = '127.0.0.1'
    MILVUS_PORT = '19530'     

    # Milvus 연결
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
    if connections:
        print("Milvus connected")
    else:
        exit()

    # 컬렉션 존재 여부 확인 및 생성
    if utility.has_collection(collection_name):
        collection = Collection(collection_name)
        print(f"Collection '{collection_name}' loaded.")
    else:
        print(f"Collection '{collection_name}' does not exist.")
        print(f"Create '{collection_name}' Collection.")
        
        field_args = [
            FieldSchema(name='id', dtype=DataType.VARCHAR, is_primary=True, max_length=100),        # split된 block의 고유 ID
            FieldSchema(name='title', dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name='date', dtype=DataType.INT64),
            FieldSchema(name='content', dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name='NER', dtype=DataType.VARCHAR, max_length=3000),
            FieldSchema(name=DENSE_FIELD, dtype=DataType.FLOAT_VECTOR, dim=DENSE_DIMENSION),
            FieldSchema(name=SPARSE_FILED, dtype=DataType.SPARSE_FLOAT_VECTOR)
        ]
        
        # 스키마 정의
        schema = CollectionSchema(fields=field_args)
        
        # 컬렉션 생성
        collection = Collection(name=collection_name, schema=schema)
        
        # 인덱스 생성
        collection.create_index("dense_vector", DENSE_INDEX)
        collection.create_index("sparse_vector", SPARSE_INDEX)

        collection.flush()

        print(f"Collection '{collection_name}' created and loaded.")
    # 생성된 컬렉션 반환
    return collection

# Collection 제거용
def drop_collection(collection_name):
    MILVUS_HOST = '127.0.0.1'
    MILVUS_PORT = '19530' 
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        print(f"Drop {collection_name} Complete.")
    else:
        print(f"Can't find {collection_name}.")
# drop_collection("Donga")