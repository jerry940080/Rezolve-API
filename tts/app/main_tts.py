from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
import logging
import httpx
from kokoro_tts import run_kokoro_tts

app = FastAPI()
logging.basicConfig(level=logging.INFO)

TRANSLATOR_API_URL = "http://translate-server:9000/translate"

@app.post("/v1/audio/speech/")
async def tts_api(request: Request):
    payload = await request.json()
    text = payload.get("input")
    target_language = payload.get("target_language", "POJ")
    model = payload.get("model", "kokoro")
    voice = payload.get("voice", "af_heart")
    print("---------receive---------")

    if not text:
        raise HTTPException(status_code=400, detail="Missing 'input' text")

    # === 呼叫翻譯 API ===
    try:
        async with httpx.AsyncClient() as client:
            translation_response = await client.post(
                TRANSLATOR_API_URL,
                json={"source_sentence": text, "target_language": target_language},
                timeout=120.0
            )
        translation_response.raise_for_status()
        translation_result = translation_response.json().get("translation")
        if not translation_result:
            raise HTTPException(status_code=502, detail="Empty translation from translation API")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Translation API error: {str(e)}")

    print(f"Translation result: {translation_result}")

    # === 語音合成 ===
    if model == "kokoro":
        try:
            output_path = run_kokoro_tts(translation_result, speaker=voice)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported model: {model}")

    return FileResponse(output_path, media_type="audio/wav", filename="speech.wav")