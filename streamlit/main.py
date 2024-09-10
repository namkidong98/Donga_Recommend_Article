from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from inference import crawling, summarize, hybrid_search
from milvus_connect import milvus_connect
from typing import Optional
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# 홈 화면
@app.get("/")
async def main(request : Request):
    return templates.TemplateResponse("index.html", {"request" : request})


# 동아닷컴 URL을 입력 받았을 때
@app.post("/api/url")
async def fetchUrlData(request : Request): # filter : Optional[str] = None
    try:
        data = await request.json()
        url = data.get('url')
        content = crawling(url)
        if not content: 
            raise Exception("Article not found")
        summary = summarize(content)
        if not summary: 
            raise Exception("Summarization Error")
        collection = milvus_connect("Donga")
        result = hybrid_search(collection, summary, filter=None) 
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
        return JSONResponse(content = json.dumps(entities, ensure_ascii=False, indent=4), status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=404)


# 기사 초안(텍스트)를 입력 받았을 때
@app.post("/api/text")
async def processText(request : Request):
    try:
        data = await request.json()
        content = data.get('text')
        if not content: 
            raise Exception("Article not found")
        summary = summarize(content)
        if not summary: 
            raise Exception("Summarization Error")
        collection = milvus_connect("Donga")
        result = hybrid_search(collection, summary, filter=None)
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
        return JSONResponse(content = json.dumps(entities, ensure_ascii=False, indent=4), status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=404)