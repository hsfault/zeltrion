# How this reel is built

All visuals are code. `index.html` is a deterministic Three.js + DOM scene: `window.seek(t)` draws the exact frame for time `t`. Playwright captures each frame headlessly, and ffmpeg encodes them.

```
index.html      scene: glossy 3D logo arcs, bubbles, clock, supplier blocks, diamond, kinetic type, logo reveal
timeline.js     voice-over line start times and per-word reveal times (TL), plus the fallback ending (TL_ALT)
assets/         logo layers (background keyed out, recoloured to #63080F / #043417) and the voice-over lines (.wav)
vo.py           voice-over generation (Kokoro-82M neural TTS, voice af_heart, speed 0.95)
audio.py        synthesized score + sound design, voice placement and music ducking  (python3 audio.py [alt])
mix.sh          voice EQ and compression, bed at -8 dB, loudnorm to -14 LUFS / -1.5 dBTP
render.cjs      frame capture worker (node render.cjs <worker> <workers> 30 810 frames)
shots.cjs       render single stills for review (node shots.cjs 1.3 9.4 22.8)
```

## Steps

```bash
npm i three@0.186.1 @fontsource/cormorant-garamond @fontsource/cinzel @fontsource/manrope
python3 -m http.server 8123 &
# frames (4 parallel workers); add ?alt to the URL in render.cjs for the fallback ending
for w in 0 1 2 3; do node render.cjs $w 4 30 810 frames & done; wait
python3 audio.py && ./mix.sh audio
ffmpeg -framerate 30 -i frames/f%05d.png -i audio/final_audio.wav \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -c:a aac -b:a 256k -shortest reel.mp4
# cover: open index.html?cover and capture one frame
```

To use a real voice recording, replace `assets/<line>.wav` (hook1, hook2, l1a, l1b, l2, l3, l4, c1, c2), update the durations and word times in `timeline.js`, and re-run the audio and render steps.

Brand palette: cream #F7F3EC (background), maroon #63080F, green #043417, deep shade #4D0C12.
Fonts: Cormorant Garamond (display), Cinzel (labels, matching the logo's caps), Manrope (small subline).
