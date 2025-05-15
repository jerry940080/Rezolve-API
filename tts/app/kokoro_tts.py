# kokoro_tts.py

import uuid
import os
import numpy as np
import torch
import soundfile as sf
from tacotron2 import Tacotron2
from wavernn import WaveRNN
from utils.text import text_to_sequence
from utils.dsp import save_wav
from utils import hparams as hp
import re

hp.configure('/app/app/hparams.py')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

voc_model = WaveRNN(
    rnn_dims=hp.voc_rnn_dims,
    fc_dims=hp.voc_fc_dims,
    bits=hp.bits,
    pad=hp.voc_pad,
    upsample_factors=hp.voc_upsample_factors,
    feat_dims=hp.num_mels,
    compute_dims=hp.voc_compute_dims,
    res_out_dims=hp.voc_res_out_dims,
    res_blocks=hp.voc_res_blocks,
    hop_length=hp.hop_length,
    sample_rate=hp.sample_rate,
    mode=hp.voc_mode
).to(device)
voc_model.load("./models/wavernn.pyt")
voc_model.eval()

tts_model = Tacotron2().to(device)
tts_model.load("./models/tacotron2_latest.pyt")
tts_model.eval()

def split_sentences(text: str, threshold: int = 100):
    punctuation = "。！？!?.,、:：;；"
    sentences = []
    buffer = text.strip()

    while len(buffer) > threshold:
        found = False
        # 從第 threshold 個字開始找第一個標點符號
        for i in range(threshold, len(buffer)):
            if buffer[i] in punctuation:
                sentences.append(buffer[:i+1].strip())
                buffer = buffer[i+1:].lstrip()
                found = True
                break
        if not found:
            # 沒找到標點符號就整段丟出去
            break

    if buffer:
        sentences.append(buffer.strip())
    
    return sentences

def synthesize_sentence(text: str) -> np.ndarray:
    seq = text_to_sequence(text.strip(), ['basic_cleaners'])
    x = np.array(seq)[None, :]
    x = torch.autograd.Variable(torch.from_numpy(x)).to(device).long()

    with torch.no_grad():
        _, mel_outputs_postnet, _, _ = tts_model.inference(x)

    if mel_outputs_postnet.shape[2] > 10000:
        raise RuntimeError(f"單句過長（mel frames={mel_outputs_postnet.shape[2]}），請重新分段：'{text}'")

    wav = voc_model.generate(mel_outputs_postnet, True, hp.voc_target, hp.voc_overlap, hp.mu_law)
    return wav

def run_kokoro_tts(text: str, speaker: str = "af_heart") -> str:
    os.makedirs('./result', exist_ok=True)
    save_path = f"./result/kokoro_{uuid.uuid4()}.wav"

    sentences = split_sentences(text)
    print(f"共分割為 {len(sentences)} 句")

    all_wavs = []

    for idx, sentence in enumerate(sentences):
        print(f"合成第 {idx + 1} 句：{sentence}")
        try:
            wav = synthesize_sentence(sentence)
        except Exception as e:
            print(f"⚠️ 第 {idx + 1} 句失敗，跳過。錯誤訊息：{e}")
            continue

        all_wavs.append(wav)

        # 插入約 0.3 秒靜音（根據 sample rate）
        silence = np.zeros(int(0.3 * hp.sample_rate))
        all_wavs.append(silence)

    if not all_wavs:
        raise RuntimeError("❌ 所有句子都無法合成，請檢查輸入內容。")

    full_wav = np.concatenate(all_wavs)
    save_wav(full_wav, save_path)
    print(f"✅ 合成完成，儲存於: {save_path}")
    return save_path
