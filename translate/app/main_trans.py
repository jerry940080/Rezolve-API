from fastapi import FastAPI
from pydantic import BaseModel
from taigi_translator import translate

app = FastAPI()

# 請求格式定義
class TranslationRequest(BaseModel):
    source_sentence: str
    target_language: str

# 路由：POST /translate
@app.post("/translate")
def translate_text(request: TranslationRequest):
    result = translate(request.source_sentence, request.target_language)
    print(result)
    return {"translation": result}