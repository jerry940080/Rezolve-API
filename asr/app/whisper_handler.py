from faster_whisper import WhisperModel

# 初始化模型（只載入一次）
_model = WhisperModel(
    "./models/faster_Large", device="cuda", compute_type="float16", local_files_only=True
)

def transcribe_audio(file_path: str) -> str:
    segments, _ = _model.transcribe(file_path)
    full_text = ""
    for segment in segments:
        full_text += segment.text + " " 

    return full_text.strip()