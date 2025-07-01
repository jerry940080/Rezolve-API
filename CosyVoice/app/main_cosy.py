# server.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
import logging
import os
from run_cosyvoice_tts import run_cosyvoice_tts

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/v1/audio/speech")
async def tts_api(request: Request):
    payload = await request.json()
    text = payload.get("input")
    model = payload.get("model", "cosyvoice")
    prompt_path = payload.get("prompt_path", "app/asset/min.wav")  # 預設測試檔案

    print("---------receive---------")

    if not text:
        raise HTTPException(status_code=400, detail="Missing 'input' text")
    if not prompt_path or not os.path.exists(prompt_path):
        raise HTTPException(status_code=400, detail=f"Missing or invalid prompt_path: {prompt_path}")

    # === 語音合成 ===
    if model == "cosyvoice":
        try:
            output_path = run_cosyvoice_tts(text, prompt_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported model: {model}")

    return FileResponse(output_path, media_type="audio/wav", filename="speech.wav")
