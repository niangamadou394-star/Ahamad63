# Kirène : jingle « Kirène avec Orange » (pub envoyée par Amadou) seul au début, puis bruitages rythmés sous la voix.
# Bruitages (comme Yango v2, qu'il a demandés) : petit générique au début, « pop » sur chaque étiquette,
# souffle sur les plein écrans, tampon « JETÉ », coup sourd sur les 3 leçons, « ding » sur les bons chiffres.
# Tout est synthétisé ici (aucun son téléchargé), puis mixé sous la voix, assez bas pour qu'elle reste claire.
# usage : python3 sfx.py voix.wav sortie.wav
import sys, subprocess
import numpy as np, soundfile as sf
import gfx
from gfx import T, FULLS, TOTAL

SR = 48000
rng = np.random.default_rng(7)

def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))

def tone(f0, f1, dur, tau, harm=(1.0,)):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(a * np.sin((i + 1) * ph) for i, a in enumerate(harm))
    return x * env_exp(n, tau) * np.minimum(1, t / 0.003)

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y

def pop():
    return 0.5 * tone(1100, 420, 0.09, 0.025, (1.0, 0.25))

def logo_pop():
    return 0.5 * tone(700, 1500, 0.12, 0.04, (1.0, 0.3))

def whoosh(dur=0.5):
    n = int(dur * SR); t = np.arange(n) / dur / SR
    noise = rng.standard_normal(n)
    hi = noise - lowpass(noise, 900)                   # souffle aigu
    shape = np.sin(np.pi * np.clip(t, 0, 1)) ** 2
    return 0.22 * hi * shape

def thud():
    n = int(0.35 * SR)
    body = tone(110, 45, 0.35, 0.09)
    click = lowpass(rng.standard_normal(n), 2500) * env_exp(n, 0.012)
    return 0.9 * body + 0.35 * click

def ding():
    return 0.32 * (tone(1318, 1318, 0.8, 0.22, (1.0, 0.0, 0.25)) + 0.6 * tone(1976, 1976, 0.8, 0.15))

def buzz():
    n = int(0.22 * SR); t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * 150 * t)) * 0.5 + np.sin(2 * np.pi * 300 * t) * 0.3
    return 0.18 * lowpass(x, 1800) * np.minimum(1, (0.22 - t) / 0.03) * np.minimum(1, t / 0.005)

def generique():
    """petit générique (~1,8 s) : coup grave + accord + arpège montant, posé sous les premiers mots"""
    out = np.zeros(int(1.9 * SR))
    def add(x, t0, g=1.0):
        i = int(t0 * SR); out[i:i + len(x)] += g * x[:len(out) - i]
    add(thud(), 0.0, 0.9)
    for f in (220.0, 261.6, 329.6):                      # la mineur, doux
        add(tone(f, f, 1.8, 0.55, (1.0, 0.35, 0.12)), 0.0, 0.16)
    for k, f in enumerate((440.0, 523.3, 659.3, 880.0)):  # arpège
        add(tone(f, f, 0.5, 0.12, (1.0, 0.2)), 0.10 + k * 0.11, 0.22)
    add(ding(), 0.58, 0.5)
    return out

_pop, _lpop = pop, logo_pop
from gfx import *
pop, logo_pop = _pop, _lpop
EVENTS = []
EVENTS += [(a - 0.28, whoosh, 0.9) for a, b, _, _ in FULLS[:-1]]
EVENTS += [(FULLS[-1][0] - 0.15, whoosh, 0.7), (JSTART - 0.2, whoosh, 0.7)]
EVENTS += [(t_2009 - 0.1, thud, 0.6), (t_eau - 0.15, pop, 0.6), (t_puces - 0.1, pop, 0.6), (CARD_KAO, logo_pop, 0.7), (t_kao, ding, 0.35)]
EVENTS += [(t_minutes - 0.2, pop, 0.5), (t_minutes + 0.25, pop, 0.5), (t_revendre + 0.3, logo_pop, 0.6)] + [(t_utilis - 0.25 + i * 0.08, pop, 0.35) for i in range(3)]
EVENTS += [(t_15 - 0.15, thud, 0.6), (t_toujours - 0.1, ding, 0.4), (t_puce2 - 0.15, pop, 0.5)]
EVENTS += [(t_deux - 0.15, thud, 0.7), (FULLS_D["l1"][0] - 0.05, thud, 0.5), (FULLS_D["l2"][0] - 0.05, thud, 0.5)]
EVENTS += [(t_vaut - 0.2, pop, 0.6), (t_vaut, pop, 0.6), (t_si - 0.1, logo_pop, 0.5)] + [(t_aime - 0.15 + i * 0.07, pop, 0.3) for i in range(5)]
EVENTS += [(t_qualite - 0.15, pop, 0.5), (t_acheter - 0.1, ding, 0.4)]
EVENTS += [(t_strat - 0.15, thud, 0.5), (t_comme - 0.05, logo_pop, 0.6), (t_partenariat - 0.15, ding, 0.35), (t_revendre2 - 0.1, pop, 0.5)]
EVENTS += [(t_choix - 0.2, pop, 0.6), (t_nouveau2 - 0.15, pop, 0.6), (t_revendre3 - 0.15, pop, 0.6)]
EVENTS += [(FULLS_D["choix"][1] + 0.3, pop, 0.5), (t_strat2 - 0.15, pop, 0.5)]   # rien de fort sur le dernier mot
b = FULLS[-1][0]
EVENTS += [(b, logo_pop, 0.6)] + [(b + 0.45 + i * 0.25, pop, 0.7) for i in range(3)] + [(b + 1.4, ding, 0.5)]

JINGLE_WAV = "/tmp/claude-0/-home-user-Ahamad63/82063c25-e035-5c7f-982a-4daa61791572/scratchpad/kirene/jingle.wav"

if __name__ == "__main__":
    voice, sr = sf.read(sys.argv[1], dtype="float64")
    assert sr == SR
    fx = np.zeros(len(voice))
    for t0, fn, g in EVENTS:
        x = fn() * g
        i = max(0, int(t0 * SR))
        if i >= len(fx): continue
        fx[i:i + len(x)] += x[:len(fx) - i]
    fx *= 10 ** (-10 / 20)
    mono = voice.mean(axis=1) if voice.ndim == 2 else voice
    j, _ = sf.read(JINGLE_WAV, dtype="float64")
    j = j.mean(axis=1) if j.ndim == 2 else j
    n = min(len(j), len(mono))
    i0 = int(JSTART * SR)
    n = min(len(j), len(mono) - i0)
    mono[i0:i0 + n] += j[:n]
    mono = mono + fx
    out = np.stack([mono, mono], axis=1)
    peak = np.abs(out).max()
    if peak > 0.97: out *= 0.97 / peak
    sf.write(sys.argv[2], out, SR, subtype="PCM_24")
    print("événements", len(EVENTS), "crête", round(float(peak), 3))
