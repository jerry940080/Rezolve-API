import sys
sys.path.append('third_party/Matcha-TTS')
from cosyvoice.cli.cosyvoice import CosyVoice, CosyVoice2
from cosyvoice.utils.file_utils import load_wav
import torchaudio

# zero_shot usage, <|zh|><|en|><|jp|><|yue|><|ko|> for Chinese/English/Japanese/Cantonese/Korean
cosyvoice = CosyVoice('models/CosyVoice-300M')
prompt_speech_16k = load_wav('./asset/min.wav', 16000)
for i, j in enumerate(cosyvoice.inference_cross_lingual('<|en|>I wanna Combo A and 4 neggets to go.', prompt_speech_16k, stream=False)):
    torchaudio.save('cross_lingual_{}.wav'.format(i), j['tts_speech'], cosyvoice.sample_rate)