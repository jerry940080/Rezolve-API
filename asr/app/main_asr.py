from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil, os, traceback
from tempfile import NamedTemporaryFile
from whisper_handler import transcribe_audio
import httpx

app = FastAPI()
TRANSLATOR_API_URL = "http://translate-server:9000/translate"

@app.post("/v1/audio/transcriptions")
async def transcribe_endpoint(
    file: UploadFile = File(...),
    model: str = Form(...)
):
    try:
        suffix = os.path.splitext(file.filename)[1]
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        text = transcribe_audio(tmp_path)
        print(text)

        # === 呼叫翻譯 API ===
        try:
            async with httpx.AsyncClient() as client:
                translation_response = await client.post(
                    TRANSLATOR_API_URL,
                    json={"source_sentence": text, "target_language": "ZH"},
                    timeout=120.0
                )
            translation_response.raise_for_status()
            translation_result = translation_response.json().get("translation")
            if not translation_result:
                raise HTTPException(status_code=502, detail="Empty translation from translation API")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Translation API error: {str(e)}")

        print(f"Translation result: {translation_result}")
        return JSONResponse(content={"text": translation_result})


    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="語音辨識失敗：" + str(e))
