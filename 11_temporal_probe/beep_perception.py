import json, traceback
import torch
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor
from qwen_omni_utils import process_mm_info

MODEL = "Qwen/Qwen2.5-Omni-7B"
D = "/home/bxshan/omni_probe/11_temporal_probe"
R = {}


def P(*a): print(*a, flush=True)


model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
    MODEL, torch_dtype=torch.bfloat16, device_map="auto", enable_audio_output=False)
processor = Qwen2_5OmniProcessor.from_pretrained(MODEL)
P("MODEL LOAD DONE")


def gen(video_path, prompt):
    msgs = [{"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
            {"role": "user", "content": [{"type": "video", "video": video_path},
                                         {"type": "text", "text": prompt}]}]
    text = processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    audios, images, videos = process_mm_info(msgs, use_audio_in_video=True)
    inputs = processor(text=text, audio=audios, images=images, videos=videos,
                       return_tensors="pt", padding=True, use_audio_in_video=True)
    inputs = inputs.to(model.device)
    for k in inputs:
        if torch.is_floating_point(inputs[k]): inputs[k] = inputs[k].to(model.dtype)
    out = model.generate(**inputs, use_audio_in_video=True, return_audio=False,
                         do_sample=False, temperature=None, top_p=None, top_k=None, max_new_tokens=256)
    g = out[:, inputs["input_ids"].shape[1]:]
    return processor.batch_decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()


Q = ("Listen to the audio track of this video. Is there a short beep or tone sound? "
     "If yes, does it occur near the BEGINNING, the MIDDLE, or the END of the video? Answer with one of those words.")
for name, path, expect in [("A_beep1p5", f"{D}/A_beep1p5.mp4", "MIDDLE"),
                           ("B_beep2p5", f"{D}/B_beep2p5.mp4", "END"),
                           ("C_nobeep", f"{D}/C_nobeep.mp4", "NONE")]:
    try:
        o = gen(path, Q)
    except Exception:
        o = "ERROR: " + traceback.format_exc().splitlines()[-1]
    P(f"[{name}] expect={expect} :: {o.replace(chr(10),' ')[:150]!r}")
    R[name] = {"expect": expect, "output": o}

with open(f"{D}/beep_perception_results.json", "w") as f:
    json.dump(R, f, indent=2)
P("ALL DONE")
