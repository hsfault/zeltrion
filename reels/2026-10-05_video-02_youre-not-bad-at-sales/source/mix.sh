#!/bin/bash
# usage: mix.sh <audio dir>   (expects vo_raw.wav + bed.wav, writes final_audio.wav)
set -e; cd "$1"
ffmpeg -y -loglevel error -i vo_raw.wav -af "highpass=f=75,equalizer=f=220:t=q:w=1:g=1.5,equalizer=f=3600:t=q:w=1.2:g=2.5,equalizer=f=7500:t=q:w=1:g=-1.5,acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=3,aecho=0.85:0.6:28|47:0.10|0.06,aformat=channel_layouts=stereo" vo_proc.wav
ffmpeg -y -loglevel error -i vo_proc.wav -i bed.wav -filter_complex "[0]volume=1.0[v];[1]volume=-8dB[b];[v][b]amix=inputs=2:normalize=0,alimiter=limit=0.89:attack=3:release=50[m]" -map "[m]" premix.wav
ffmpeg -nostats -i premix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p' > ln.json
python3 - <<'PY'
import json,subprocess
d=json.load(open('ln.json'))
f=f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','premix.wav','-af',f,'-ar','48000','final_audio.wav'],check=True)
PY
