from faster_whisper import WhisperModel

# 用你的模型 repo 名稱或本地模型路徑
model = WhisperModel("./faster_Large", device="cuda", compute_type="float16", local_files_only=True)
segments, info = model.transcribe("kokoro_0a696808-de84-4f8e-be28-e5b4373af7d7.wav")
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")