import numpy as np
import torch
import os
from tacotron2 import Tacotron2
from wavernn import WaveRNN
from utils.text import text_to_sequence
from utils.dsp import reconstruct_waveform, save_wav
from utils.display import simple_table
from utils import hparams as hp

from transformers import AutoModelForCausalLM, AutoTokenizer, TextGenerationPipeline
import torch
import accelerate

def get_pipeline(path:str, tokenizer:AutoTokenizer, accelerator:accelerate.Accelerator) -> TextGenerationPipeline:
    model = AutoModelForCausalLM.from_pretrained(
        path, torch_dtype=torch.float16, device_map='auto', trust_remote_code=True)
    
    terminators = [tokenizer.eos_token_id, tokenizer.pad_token_id]

    pipeline = TextGenerationPipeline(model = model, tokenizer = tokenizer, num_workers=accelerator.state.num_processes*4, pad_token_id=tokenizer.pad_token_id, eos_token_id=terminators)

    return pipeline

model_dir = "Bohanlu/Taigi-Llama-2-Translator-7B" # or "Bohanlu/Taigi-Llama-2-Translator-13B" for the 13B model
tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=False)

accelerator = accelerate.Accelerator()
pipe = get_pipeline(model_dir, tokenizer, accelerator)

PROMPT_TEMPLATE = "[TRANS]\n{source_sentence}\n[/TRANS]\n[{target_language}]\n"

def translate(source_sentence:str, target_language:str) -> str:
    prompt = PROMPT_TEMPLATE.format(source_sentence=source_sentence, target_language=target_language)
    out = pipe(prompt, return_full_text=False, repetition_penalty=1.1, do_sample=False)[0]['generated_text']
    return out[:out.find("[/")].strip()


def synthesize_taiwanese_tts(input_text: str) -> str:
    class Args:
        tts_weights = "../models/tacotron2_latest.pyt"
        voc_weights = "../models/wavernn.pyt"
        save_dir = "./result"
        vocoder = 'wavernn'
        hp_file = 'hparams.py'
        save_attn = False
        batched = True
        target = None
        overlap = None
        force_cpu = False

    args = Args()
    hp.configure(args.hp_file)

    device = torch.device('cuda' if torch.cuda.is_available() and not args.force_cpu else 'cpu')
    print('Using device:', device)

    # Initialize vocoder
    if args.vocoder == 'wavernn':
        voc_model = WaveRNN(rnn_dims=hp.voc_rnn_dims,
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
                            mode=hp.voc_mode).to(device)
        voc_model.load(args.voc_weights)
        voc_model.eval()
        voc_k = voc_model.get_step() // 1000
    else:
        raise ValueError("Unsupported vocoder")

    # Initialize Tacotron2
    tts_model = Tacotron2().to(device)
    tts_model.load(args.tts_weights)
    tts_model.eval()
    tts_k = tts_model.get_step() // 1000

    simple_table([('Tacotron2', str(tts_k) + 'k'),
                  ('Vocoder Type', 'WaveRNN'),
                  ('WaveRNN', str(voc_k) + 'k'),
                  ('Generation Mode', 'Batched' if args.batched else 'Unbatched'),
                  ('Target Samples', args.target if args.batched else 'N/A'),
                  ('Overlap Samples', args.overlap if args.batched else 'N/A')])

    # translation
    translated_text = translate(input_text, "POJ")

    # Convert text to sequence
    seq = text_to_sequence(translated_text.strip(), ['basic_cleaners'])
    x = np.array(seq)[None, :]
    x = torch.autograd.Variable(torch.from_numpy(x)).to(device).long()

    # Generate mel spectrogram
    with torch.no_grad():
        _, mel_outputs_postnet, _, _ = tts_model.inference(x)

    # if mel_outputs_postnet.shape[2] > 2000:
        # raise RuntimeError("Generated mel spectrogram is too long.")

    os.makedirs(args.save_dir, exist_ok=True)
    v_type = 'wavernn_batched' if args.batched else 'wavernn_unbatched'
    save_path = os.path.join(args.save_dir, f'1_{v_type}_{tts_k}k.wav')

    m = mel_outputs_postnet
    wav = voc_model.generate(m, args.batched, hp.voc_target, hp.voc_overlap, hp.mu_law)
    save_wav(wav, save_path)

    print(f"\nSaved synthesized speech to: {save_path}")
    return save_path

path = synthesize_taiwanese_tts("你今天過得好嗎?")
print("音檔儲存於：", path)