"""Genera collage/jingle-80s.mp3: versión synth-pop ochentera de "Jingle Bells" (dominio público).
Uso: python music_build.py   (requiere numpy, scipy y ffmpeg)"""
import subprocess
from pathlib import Path
import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
BPM = 124
BEAT = 60 / BPM
BAR = BEAT * 4
OUT = Path(__file__).parent / "collage"
rng = np.random.default_rng(1)

A = [[71,1],[71,1],[71,2],[71,1],[71,1],[71,2],[71,1],[74,1],[67,1.5],[69,.5],[71,4]]
P1 = A + [[72,1],[72,1],[72,1.5],[72,.5],[72,1],[71,1],[71,1],[71,.5],[71,.5],[71,1],[69,1],[69,1],[71,1],[69,2],[74,2]]
P2 = A + [[72,1],[72,1],[72,1.5],[72,.5],[72,1],[71,1],[71,1],[71,.5],[71,.5],[74,1],[74,1],[72,1],[69,1],[67,4]]
CH = {"G": [55,59,62], "C": [55,60,64], "D7": [54,57,60], "D": [54,57,62]}
ROOT = {"G": 43, "C": 36, "D7": 38, "D": 38}
PROG = ["G","G","G","G","C","G","D7","D","G","G","G","G","C","G","D7","G"]
hz = lambda n: 440 * 2 ** ((n - 69) / 12)

INTRO = 2
BARS = INTRO + 32
N = int(SR * BAR * BARS) + SR * 2
lead = np.zeros(N); mix = np.zeros(N)

def saw(f, n, det=0.0):
    t = np.arange(n) / SR
    ph = (t * f * 2 ** (det / 1200)) % 1
    return 2 * ph - 1

def sq(f, n, det=0.0):
    return np.sign(saw(f, n, det))

def env(n, a=.01, d=.1, s=.6, r=.05):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e

def lp(x, fc, order=2):
    b, a = butter(order, min(fc / (SR / 2), .99))
    return lfilter(b, a, x)

def hp(x, fc):
    b, a = butter(2, fc / (SR / 2), "high")
    return lfilter(b, a, x)

def add(buf, start, sig):
    i = int(start * SR)
    buf[i:i + len(sig)] += sig[: max(0, len(buf) - i)]

def bars_of(seq):
    out = {}; t = 0
    for n, d in seq:
        b = int(t // 4 + 1e-6); out.setdefault(b, []).append((t - b * 4, n, d)); t += d
    return out
m1, m2 = bars_of(P1), bars_of(P2)
MEL = [m1.get(i, []) for i in range(16)] + [m2.get(i, []) for i in range(16)]

noise = rng.uniform(-1, 1, SR)
for k in range(BARS):
    t0 = k * BAR
    intro = k < INTRO
    lb = 0 if intro else (k - INTRO) % 32
    ch = "G" if intro else PROG[lb % 16]
    # bass: octave eighths
    for i in range(8):
        n = int(BEAT / 2 * SR)
        s = saw(hz(ROOT[ch] + (12 if i % 2 else 0)), n)
        s = lp(s, 700) * env(n, .005, .08, .5, .02) * .32
        add(mix, t0 + i * BEAT / 2, s)
    for b in range(4):
        # kick
        n = int(.32 * SR); t = np.arange(n) / SR
        f = 42 + 108 * np.exp(-t / .03)
        add(mix, t0 + b * BEAT, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .09) * .9)
        # off-beat hat
        n = int(.09 * SR)
        add(mix, t0 + b * BEAT + BEAT / 2, hp(noise[:n], 7000) * np.exp(-np.arange(n) / SR / .025) * .18)
        if not intro and b in (1, 3):
            n = int(.22 * SR)
            sn = hp(noise[:n], 1400) * np.exp(-np.arange(n) / SR / .06) * .45
            sn += np.sin(2 * np.pi * 190 * np.arange(n) / SR) * np.exp(-np.arange(n) / SR / .03) * .25
            add(mix, t0 + b * BEAT, sn)
    if intro:
        continue
    for s16 in range(16):
        n = int(.06 * SR)
        add(mix, t0 + s16 * BEAT / 4, hp(noise[n:2 * n], 9000) * np.exp(-np.arange(n) / SR / .015) * (.12 if s16 % 4 == 2 else .05))
    # pad
    n = int(BAR * SR)
    pad = sum(saw(hz(x), n, d) for x in CH[ch] for d in (-10, 10))
    add(mix, t0, lp(pad, 1300) * env(n, .25, .5, .7, .15) * .035)
    # lead
    for st, note, d in MEL[lb]:
        n = int(d * BEAT * SR)
        s = sq(hz(note), n, -7) * .5 + saw(hz(note), n, 7) * .5
        add(lead, t0 + st * BEAT, lp(s, 2600) * env(n, .01, .1, .6, .05) * .16)

# ping-pong style delay on the lead
dl = int(BEAT * .75 * SR)
wet = np.zeros_like(lead); fb = lead.copy()
for i in range(1, 5):
    wet[dl * i:] += fb[:-dl * i] * (.3 ** i)
mix += lead + wet * .8
mix = np.tanh(mix * 1.3) * .85
end = int(SR * BAR * BARS)
fade = int(.02 * SR)
mix = mix[:end]; mix[:fade] *= np.linspace(0, 1, fade); mix[-fade:] *= np.linspace(1, 0, fade)
pcm = (mix * 32767).astype(np.int16).tobytes()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                "-c:a", "libmp3lame", "-b:a", "96k", str(OUT / "jingle-80s.mp3")], input=pcm, check=True)
print("jingle-80s.mp3", round(end / SR, 1), "s")
