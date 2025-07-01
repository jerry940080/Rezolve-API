import sys
import os
import uuid
import torch
import torchaudio
from langdetect import detect
from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.file_utils import load_wav

sys.path.append('third_party/Matcha-TTS')

cosyvoice = CosyVoice('models/CosyVoice-300M')


def add_language_tag(text: str) -> str:
    if text.strip().startswith("<|"):
        return text
    try:
        lang = detect(text)
        return f"<|en|>{text}" if lang == "en" else f"<|zh|>{text}"
    except Exception:
        return f"<|zh|>{text}"


def split_sentences(text: str, threshold: int = 100):
    punctuation = "。！？!?.,、:：;；"
    sentences = []
    buffer = text.strip()

    while len(buffer) > threshold:
        found = False
        for i in range(threshold, len(buffer)):
            if buffer[i] in punctuation:
                sentences.append(buffer[:i + 1].strip())
                buffer = buffer[i + 1:].lstrip()
                found = True
                break
        if not found:
            break

    if buffer:
        sentences.append(buffer.strip())

    return sentences


def run_cosyvoice_tts(text: str, prompt_path: str) -> str:
    prompt_speech_16k = load_wav(prompt_path, 16000)
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    sentences = split_sentences(text)
    print(f"共分割為 {len(sentences)} 句")

    audio_segments = []

    for idx, sentence in enumerate(sentences):
        text_with_tag = add_language_tag(sentence)
        print(f"合成第 {idx + 1} 句：{text_with_tag}")
        try:
            for result in cosyvoice.inference_cross_lingual(text_with_tag, prompt_speech_16k, stream=False):
                audio_segments.append(result["tts_speech"])
                # 每句後加 0.3 秒靜音
                silence = torch.zeros((1, int(0.3 * cosyvoice.sample_rate)))
                audio_segments.append(silence)
        except Exception as e:
            print(f"第 {idx + 1} 句失敗，跳過。錯誤訊息：{e}")
            continue

    if not audio_segments:
        raise RuntimeError("所有句子都無法合成，請檢查輸入內容。")

    final_audio = torch.cat(audio_segments, dim=1)
    output_path = os.path.join(output_dir, f"cosy_out_{uuid.uuid4().hex[:8]}.wav")
    torchaudio.save(output_path, final_audio, cosyvoice.sample_rate)

    torch.cuda.empty_cache()
    print(f"合成完成，儲存於: {output_path}")
    return output_path
