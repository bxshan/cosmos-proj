import torch, time
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor
from qwen_omni_utils import process_mm_info

MODEL = "Qwen/Qwen2.5-Omni-3B"
AUDIO = "/home/bxshan/omni_probe/test.wav"

t0 = time.time()
model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
    MODEL, torch_dtype="auto", device_map="auto", enable_audio_output=False
)
processor = Qwen2_5OmniProcessor.from_pretrained(MODEL)
print("load secs:", round(time.time() - t0, 1))

conversation = [
    {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
    {"role": "user", "content": [
        {"type": "audio", "audio": AUDIO},
        {"type": "text", "text": "What word or phrase is spoken in this audio? Answer directly."},
    ]},
]

text = processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
audios, images, videos = process_mm_info(conversation, use_audio_in_video=False)
inputs = processor(text=text, audio=audios, images=images, videos=videos,
                   return_tensors="pt", padding=True, use_audio_in_video=False)
inputs = inputs.to(model.device).to(model.dtype)

t1 = time.time()
out = model.generate(**inputs, use_audio_in_video=False, return_audio=False, max_new_tokens=128)
gen = out[:, inputs["input_ids"].shape[1]:]
answer = processor.batch_decode(gen, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
print("gen secs:", round(time.time() - t1, 1))
print("VRAM_GB:", round(torch.cuda.max_memory_allocated() / 1e9, 2))
print("ANSWER_START>>>")
print(answer.strip())
print("<<<ANSWER_END")
