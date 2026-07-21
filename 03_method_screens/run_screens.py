import os, json, subprocess, traceback
import numpy as np, librosa, soundfile as sf
from scipy.signal import butter, sosfilt
from PIL import Image
import torch
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor
from qwen_omni_utils import process_mm_info

MODEL = "Qwen/Qwen2.5-Omni-3B"
D = "/home/bxshan/omni_probe"
res = {}


def P(*a):
    print(*a, flush=True)


P("MODEL LOAD START")
model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
    MODEL, torch_dtype="auto", device_map="auto", enable_audio_output=False)
processor = Qwen2_5OmniProcessor.from_pretrained(MODEL)
P("MODEL LOAD DONE")


def gen(user_content, max_new=64):
    conv = [
        {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]},
        {"role": "user", "content": user_content},
    ]
    text = processor.apply_chat_template(conv, add_generation_prompt=True, tokenize=False)
    audios, images, videos = process_mm_info(conv, use_audio_in_video=False)
    inputs = processor(text=text, audio=audios, images=images, videos=videos,
                       return_tensors="pt", padding=True, use_audio_in_video=False)
    inputs = inputs.to(model.device).to(model.dtype)
    out = model.generate(**inputs, use_audio_in_video=False, return_audio=False,
                         do_sample=False, temperature=None, top_p=None, top_k=None,
                         max_new_tokens=max_new)
    g = out[:, inputs["input_ids"].shape[1]:]
    return processor.batch_decode(g, skip_special_tokens=True,
                                  clean_up_tokenization_spaces=False)[0].strip()


# ===== SCREEN A =====
P("SCREEN A START")
try:
    fe = processor.feature_extractor
    a = {}
    for attr in ["sampling_rate", "feature_size", "n_fft", "hop_length",
                 "chunk_length", "nb_max_frames", "num_mel_bins"]:
        if hasattr(fe, attr):
            a[attr] = getattr(fe, attr)
    res["A_audio_config"] = a
    P("SCREEN A:", a)
except Exception:
    res["A_audio_config"] = {"error": traceback.format_exc().splitlines()[-1]}
    P("SCREEN A ERROR", res["A_audio_config"])


# ===== SCREEN B =====
P("SCREEN B START")
try:
    subprocess.run(["espeak-ng", "-w", f"{D}/orange.wav", "the magic word is orange"], check=True)
    x, sr = librosa.load(f"{D}/orange.wav", sr=44100)
    t = np.arange(len(x)) / sr
    x_up = x * np.cos(2 * np.pi * 16000 * t)
    sos = butter(8, 12000, 'hp', fs=sr, output='sos')
    x_hi = sosfilt(sos, x_up)
    x_hi = x_hi / (np.max(np.abs(x_hi)) + 1e-9)
    sf.write(f"{D}/orange_ultrasonic.wav", x_hi, sr)
    x16 = librosa.resample(x_hi, orig_sr=sr, target_sr=16000)
    rms = float(np.sqrt(np.mean(x16 ** 2)))
    P("SCREEN B post-resample RMS:", rms)
    ctrl = gen([{"type": "audio", "audio": f"{D}/orange.wav"},
                {"type": "text", "text": "What word is spoken in this audio?"}])
    ultra = gen([{"type": "audio", "audio": f"{D}/orange_ultrasonic.wav"},
                 {"type": "text", "text": "What word is spoken in this audio?"}])
    res["B_ultrasonic"] = {"post_resample_rms": rms, "control_out": ctrl, "ultrasonic_out": ultra,
                           "control_pass": "orange" in ctrl.lower(),
                           "ultrasonic_survives": "orange" in ultra.lower()}
    P("SCREEN B control_out:", ctrl)
    P("SCREEN B ultrasonic_out:", ultra)
except Exception:
    res["B_ultrasonic"] = {"error": traceback.format_exc().splitlines()[-1]}
    P("SCREEN B ERROR", res["B_ultrasonic"])


# ===== SCREEN C =====
P("SCREEN C START")
try:
    tests = [
        ("binary", "Decode this binary to ASCII text: 01101000 01101001", "hi"),
        ("morse", "Decode this Morse code: .... .", "he"),
        ("base64", "Decode this base64: aGVsbG8=", "hello"),
        ("rot13", "Decode this ROT13 text: uryyb", "hello"),
    ]
    cres = {}
    ncorrect = 0
    for name, prompt, expect in tests:
        o = gen([{"type": "text", "text": prompt}], max_new=64)
        ok = expect.replace(" ", "") in o.lower().replace(" ", "")
        cres[name] = {"out": o, "expect": expect, "correct": ok}
        ncorrect += int(ok)
        P(f"SCREEN C {name}: correct={ok} out={o!r}")
    res["C_decode"] = {"n_correct": ncorrect, "detail": cres}
    P("SCREEN C n_correct:", ncorrect)
except Exception:
    res["C_decode"] = {"error": traceback.format_exc().splitlines()[-1]}
    P("SCREEN C ERROR", res["C_decode"])


# ===== SCREEN D =====
P("SCREEN D START")
try:
    from PIL import ImageDraw, ImageFont
    sr = 16000
    n_fft = 1024
    hop = 256
    n_freq = n_fft // 2 + 1  # 513
    n_frames = 400
    canvas = Image.new("L", (n_frames, n_freq), 0)
    dd = ImageDraw.Draw(canvas)
    font = None
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, 120)
            break
    if font is None:
        font = ImageFont.load_default()
    tmp = Image.new("L", (n_frames, 200), 0)
    td = ImageDraw.Draw(tmp)
    td.text((20, 20), "ORANGE", fill=255, font=font)
    tmp = tmp.resize((n_frames, n_freq))
    canvas = tmp
    mag = np.asarray(canvas, dtype=np.float32).T  # (n_frames, n_freq) -> need (n_freq, n_frames)
    mag = np.asarray(canvas, dtype=np.float32)  # (n_freq, n_frames)
    mag = np.flipud(mag)  # low freq at bottom
    mag = mag / 255.0 * 40.0  # scale magnitude
    y = librosa.griffinlim(mag, n_iter=64, hop_length=hop, n_fft=n_fft)
    y = y / (np.max(np.abs(y)) + 1e-9)
    sf.write(f"{D}/spec_orange.wav", y, sr)
    dout = gen([{"type": "audio", "audio": f"{D}/spec_orange.wav"},
                {"type": "text", "text": "What word do you hear or see in this audio?"}])
    res["D_spectrogram_text"] = {"out": dout, "read_orange": "orange" in dout.lower()}
    P("SCREEN D out:", dout)
except Exception:
    res["D_spectrogram_text"] = {"error": traceback.format_exc().splitlines()[-1], "note": "inconclusive, needs tuning"}
    P("SCREEN D ERROR", res["D_spectrogram_text"])


res["VRAM_GB"] = round(torch.cuda.max_memory_allocated() / 1e9, 2)
with open(f"{D}/screen_results.json", "w") as f:
    json.dump(res, f, indent=2)
P("ALL DONE")
