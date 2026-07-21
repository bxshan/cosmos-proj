import os, json, subprocess, traceback
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio
import soundfile as sf
import torch
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor
from qwen_omni_utils import process_mm_info

MODEL = "Qwen/Qwen2.5-Omni-7B"
D = "/home/bxshan/omni_probe/11_temporal_probe"
os.makedirs(D, exist_ok=True)
FPS = 8
DUR = 3.0
SR = 16000
SEGMENTS = [("RED", (200, 40, 40)), ("BLUE", (40, 40, 200)), ("GREEN", (30, 150, 60))]
R = {}


def P(*a):
    print(*a, flush=True)


def font(sz=140):
    fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(fp, sz) if os.path.exists(fp) else ImageFont.load_default()


def make_frames():
    frames = []
    n = int(FPS * DUR)
    f = font(140)
    for i in range(n):
        t = i / FPS
        seg = min(int(t // 1.0), 2)
        word, bg = SEGMENTS[seg]
        img = Image.new("RGB", (640, 360), bg)
        dr = ImageDraw.Draw(img)
        bb = dr.textbbox((0, 0), word, font=f)
        w, h = bb[2] - bb[0], bb[3] - bb[1]
        dr.text(((640 - w) / 2 - bb[0], (360 - h) / 2 - bb[1]), word, fill=(255, 255, 255), font=f)
        frames.append(np.asarray(img))
    return frames


def make_audio(beep_t):
    n = int(SR * DUR)
    y = np.zeros(n, np.float32)
    if beep_t is not None:
        start = int(beep_t * SR)
        dur = int(0.150 * SR)
        tt = np.arange(dur) / SR
        y[start:start + dur] = 0.8 * np.sin(2 * np.pi * 1000 * tt).astype(np.float32)
    return y


def build_video(name, beep_t):
    vpath = f"{D}/{name}_silent.mp4"
    apath = f"{D}/{name}.wav"
    out = f"{D}/{name}.mp4"
    frames = make_frames()
    w = imageio.get_writer(vpath, fps=FPS, codec="libx264", macro_block_size=1,
                           ffmpeg_log_level="error")
    for fr in frames:
        w.append_data(fr)
    w.close()
    sf.write(apath, make_audio(beep_t), SR)
    # mux audio into video
    cmd = ["/usr/bin/ffmpeg", "-y", "-i", vpath, "-i", apath,
           "-c:v", "copy", "-c:a", "aac", "-shortest", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg mux failed: " + r.stderr.splitlines()[-1])
    # verify audio stream present
    probe = subprocess.run(["/usr/bin/ffprobe", "-v", "error", "-show_entries",
                            "stream=codec_type", "-of", "csv=p=0", out],
                           capture_output=True, text=True)
    P(f"  built {name}.mp4 streams={probe.stdout.split()}")
    return out


P("BUILD VIDEOS START")
vA = build_video("A_beep1p5", 1.5)
vB = build_video("B_beep2p5", 2.5)
vC = build_video("C_nobeep", None)
P("BUILD VIDEOS DONE")

P("MODEL LOAD START")
model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
    MODEL, torch_dtype=torch.bfloat16, device_map="auto", enable_audio_output=False)
processor = Qwen2_5OmniProcessor.from_pretrained(MODEL)
P("MODEL LOAD DONE")


def gen(video_path, prompt, use_audio_in_video):
    msgs = [
        {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
        {"role": "user", "content": [
            {"type": "video", "video": video_path},
            {"type": "text", "text": prompt}]},
    ]
    text = processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    audios, images, videos = process_mm_info(msgs, use_audio_in_video=use_audio_in_video)
    inputs = processor(text=text, audio=audios, images=images, videos=videos,
                       return_tensors="pt", padding=True, use_audio_in_video=use_audio_in_video)
    inputs = inputs.to(model.device)
    for k in inputs:
        if torch.is_floating_point(inputs[k]):
            inputs[k] = inputs[k].to(model.dtype)
    out = model.generate(**inputs, use_audio_in_video=use_audio_in_video, return_audio=False,
                         do_sample=False, temperature=None, top_p=None, top_k=None,
                         max_new_tokens=512)
    g = out[:, inputs["input_ids"].shape[1]:]
    return processor.batch_decode(g, skip_special_tokens=True,
                                  clean_up_tokenization_spaces=False)[0].strip()


# ---- Test C first: does it read the video timeline at all? ----
P("TEST C START")
try:
    oc = gen(vC, "List the words shown in the video, in order.", use_audio_in_video=False)
except Exception:
    oc = "ERROR: " + traceback.format_exc().splitlines()[-1]
lc = oc.lower()
seq_ok = (lc.find("red") < lc.find("blue") < lc.find("green")) if all(w in lc for w in ["red", "blue", "green"]) else False
P(f"TEST C seq_ok={seq_ok} :: {oc.replace(chr(10),' ')[:120]!r}")
R["testC"] = {"output": oc, "sequence_ok": seq_ok}

# ---- Test A: beep during BLUE ----
PROMPT = ("A word is shown in the video and a short beep plays at one moment. "
          "Which single word is on screen at the exact moment the beep plays?")
P("TEST A START")
try:
    oa = gen(vA, PROMPT, use_audio_in_video=True)
except Exception:
    oa = "ERROR: " + traceback.format_exc().splitlines()[-1]
a_word = "BLUE" if "blue" in oa.lower() else ("RED" if "red" in oa.lower() else ("GREEN" if "green" in oa.lower() else "?"))
P(f"TEST A answer={a_word} (expect BLUE) :: {oa.replace(chr(10),' ')[:120]!r}")
R["testA"] = {"beep_t": 1.5, "expect": "BLUE", "answer_word": a_word, "output": oa}

# ---- Test B: beep during GREEN ----
P("TEST B START")
try:
    ob = gen(vB, PROMPT, use_audio_in_video=True)
except Exception:
    ob = "ERROR: " + traceback.format_exc().splitlines()[-1]
b_word = "GREEN" if "green" in ob.lower() else ("RED" if "red" in ob.lower() else ("BLUE" if "blue" in ob.lower() else "?"))
P(f"TEST B answer={b_word} (expect GREEN) :: {ob.replace(chr(10),' ')[:120]!r}")
R["testB"] = {"beep_t": 2.5, "expect": "GREEN", "answer_word": b_word, "output": ob}

tracks = (R["testA"]["answer_word"] == "BLUE") and (R["testB"]["answer_word"] == "GREEN")
R["time_binding_confirmed"] = bool(tracks)
R["vram_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 2)
with open(f"{D}/temporal_probe_results.json", "w") as f:
    json.dump(R, f, indent=2)
P(f"TIME_BINDING_CONFIRMED={tracks}")
P("VRAM_GB:", R["vram_gb"])
P("ALL DONE")
