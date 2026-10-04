import sys, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('kokoro_fp16.onnx', 'voices.npz')
voice = sys.argv[1]; speed = float(sys.argv[2]); out = sys.argv[3]
# Video 02 script, verbatim from the playbook (hook + script + closing line)
lines = [
 ("hook1", "You're not bad at sales."),
 ("hook2", "You're just late."),
 ("l1a", "A lead messages you."),
 ("l1b", "An hour passes."),
 ("l2", "By then, they may have messaged three other suppliers."),
 ("l3", "Often, the first business to reply is the one that gets the call."),
 ("l4", "An instant first reply keeps them warm until you can talk."),
 ("c1", "Want messages you can send in the first minute?"),
 ("c2", "DM FAST."),
 ("a1", "How fast do you reply to a new enquiry?"),  # fallback ending
 ("a2", "Be honest."),
]
meta = []
import os; os.makedirs(out, exist_ok=True)
for key, text in lines:
    s, sr = k.create(text, voice=voice, speed=speed, lang='en-us')
    sf.write(f'{out}/{key}.wav', s, sr)
    meta.append({"key": key, "text": text, "dur": round(len(s)/sr, 3)})
    print(key, round(len(s)/sr,2), text)
json.dump(meta, open(f'{out}/meta.json','w'), indent=1)
