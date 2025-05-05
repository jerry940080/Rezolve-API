from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
import logging
import json
from kokoro_tts import run_kokoro_tts


app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/v1/audio/speech")
async def tts_api(request: Request):
    payload = await request.json()
    text = payload.get("input")
    model = payload.get("model", "kokoro")
    voice = payload.get("voice", "zf_xiaobei")

    if not text:
        raise HTTPException(status_code=400, detail="Missing 'input' text")

    if model == "kokoro":
        output_path = run_kokoro_tts(text, speaker=voice)

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported model: {model}")

    return FileResponse(output_path, media_type="audio/wav", filename="speech.wav")
