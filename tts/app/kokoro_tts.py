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

def run_kokoro_tts(translated_text: str, speaker: str = "af_heart") -> str:
    
    seq = text_to_sequence(translated_text.strip(), ['basic_cleaners'])
    x = np.array(seq)[None, :]
    x = torch.autograd.Variable(torch.from_numpy(x)).to(device).long()

    with torch.no_grad():
        _, mel_outputs_postnet, _, _ = tts_model.inference(x)

    if mel_outputs_postnet.shape[2] > 4000:
        raise RuntimeError("Generated mel spectrogram is too long.")

    os.makedirs('./result', exist_ok=True)
    save_path = f"./result/kokoro_{uuid.uuid4()}.wav"

    wav = voc_model.generate(mel_outputs_postnet, True, hp.voc_target, hp.voc_overlap, hp.mu_law)
    save_wav(wav, save_path)
    print(f"Saved synthesized speech to: {save_path}")
    return save_path

# if __name__ == '__main__':
#     wav_path = run_kokoro_tts("你好嗎？")
#     print(f"Output: {wav_path}")
