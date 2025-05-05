from kokoro import KPipeline
import soundfile as sf
import uuid
import os

# 模型初始化（建議只做一次）
pipeline = KPipeline(lang_code="a")  # 支援多語音風格

def run_kokoro_tts(text: str, speaker: str = "af_heart") -> str:
    output_path = f"/tmp/kokoro_{uuid.uuid4()}.wav"
    
    generator = pipeline(text, voice=speaker)
    for i, (gs, ps, audio) in enumerate(generator):
        if i == 0:  # 只輸出第一段
            sf.write(output_path, audio, 24000)
            break

    return output_path
