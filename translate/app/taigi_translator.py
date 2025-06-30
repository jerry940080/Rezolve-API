# taigi_translator.py

from transformers import AutoModelForCausalLM, AutoTokenizer, TextGenerationPipeline
import torch
import accelerate

# ✅ 初始化模型一次
model_dir = "./models/models--Bohanlu--Taigi-Llama-2-Translator-7B/snapshots/784ecc27f53659d710c13cdaec651ade2b65799f/"
tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=False)
accelerator = accelerate.Accelerator()

def get_pipeline(path: str, tokenizer, accelerator) -> TextGenerationPipeline:
    model = AutoModelForCausalLM.from_pretrained(
        path,
        torch_dtype=torch.float16,
        device_map='auto',
        trust_remote_code=True
    )
    terminators = [tokenizer.eos_token_id, tokenizer.pad_token_id]
    return TextGenerationPipeline(
        model=model,
        tokenizer=tokenizer,
        num_workers=accelerator.state.num_processes * 4,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=terminators
    )

pipe = get_pipeline(model_dir, tokenizer, accelerator)

PROMPT_TEMPLATE = "[TRANS]\n{source_sentence}\n[/TRANS]\n[{target_language}]\n"

def translate(source_sentence: str, target_language: str) -> str:
    prompt = PROMPT_TEMPLATE.format(source_sentence=source_sentence, target_language=target_language)
    out = pipe(prompt, return_full_text=False, repetition_penalty=1.1, do_sample=False)[0]['generated_text']
    if "[/" in out:
        return out[:out.find("[/")].strip()
    return out.strip()

# if __name__ == '__main__':
#     translated_text = translate("你好嗎？", "POJ")
#     print(translated_text)
