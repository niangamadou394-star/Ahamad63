# JOJ : musique de la cérémonie (envoyée par Amadou) sous la voix + bruitages discrets.
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

_pop = pop
from gfx import *
pop = _pop
EVENTS = []
EVENTS += [(a - 0.32, whoosh, 0.9) for a, b, _, _ in FULLS[:-1]]
EVENTS += [(FULLS[-1][0] - 0.15, whoosh, 0.7), (INTRO_END - 0.2, whoosh, 0.8), (MODU_A - 0.2, whoosh, 0.8)]
EVENTS += [(t_entre - 0.1, pop, 0.6), (t_quest, pop, 0.5)]
EVENTS += [(t_70 - 0.2, thud, 0.7), (t_70 + 0.8, ding, 0.4), (t_senega - 0.3, pop, 0.6)]
EVENTS += [(FULLS_D[k][0] - 0.05, thud, 0.5) for k in ("l1", "l2", "l3")]
EVENTS += [(t_2700 - 0.15, pop, 0.6)] + [(t_equipes - 0.25 + i * 0.05, pop, 0.3) for i in range(9)]
a0 = FULLS_D["secteurs"][0]
EVENTS += [(a0 + 0.15, pop, 0.5), (a0 + 0.35, pop, 0.5), (t_artist - 0.1, pop, 0.5), (t_tour - 0.1, pop, 0.5)]
EVENTS += [(t_petites - 0.1, pop, 0.5), (t_moyennes - 0.1, pop, 0.5), (t_brille - 0.1, ding, 0.4)]
EVENTS += [(t_modu + 0.2, pop, 0.5), (t_multi - 0.1, thud, 0.7), (t_demarq - 0.1, ding, 0.4)]
EVENTS += [(t_travail - 0.2 + i * 0.06, pop, 0.3) for i in range(7)]
EVENTS += [(t_artist2 - 0.15, pop, 0.5), (t_orga - 0.15, pop, 0.5), (t_finan - 0.15, pop, 0.5), (t_sacr - 0.2, thud, 0.5)]
b = FULLS[-1][0]
EVENTS += [(b + 0.45 + i * 0.25, pop, 0.6) for i in range(3)] + [(b + 1.4, ding, 0.5)]   # rien de fort sur « au top » (dernier mot)

MUSIC = "/tmp/claude-0/-home-user-Ahamad63/82063c25-e035-5c7f-982a-4daa61791572/scratchpad/joj/musique.wav"
def music_bed(n):
    """musique de la cérémonie : forte sous l'intro, basse sous la parole, remonte sur l'écran final ; bouclée avec fondu"""
    m, sr = sf.read(MUSIC, dtype="float64")
    m = m.mean(axis=1) if m.ndim == 2 else m
    m = m[:int(56.5 * SR)]
    if len(m) < n:
        j, xf = int(9.0 * SR), int(1.5 * SR)
        tail = m[j:]
        need = n - len(m) + xf
        tail = np.concatenate([tail] * (need // len(tail) + 1))[:need]
        r = np.linspace(0, 1, xf)
        m = np.concatenate([m[:-xf], m[-xf:] * (1 - r) + tail[:xf] * r, tail[xf:]])
    m = m[:n]
    t = np.arange(n) / SR
    g = np.full(n, 0.13)
    g = np.where(t < INTRO_END, 0.30, g)
    k = np.clip((t - INTRO_END) / 0.8, 0, 1); g = np.where((t >= INTRO_END) & (t < INTRO_END + 0.8), 0.30 + (0.13 - 0.30) * k, g)
    k = np.clip((t - (END_SPEECH + 0.1)) / 0.8, 0, 1); g = np.where(t >= END_SPEECH + 0.1, 0.13 + (0.55 - 0.13) * k, g)
    k = np.clip((t - (n / SR - 1.6)) / 1.6, 0, 1); g *= 1 - k
    return m * g

if __name__ == "__main__":
    voice, sr = sf.read(sys.argv[1], dtype="float64")
    assert sr == SR
    fx = np.zeros(len(voice))
    for t0, fn, g in EVENTS:
        x = fn() * g
        i = max(0, int(t0 * SR))
        if i >= len(fx): continue
        fx[i:i + len(x)] += x[:len(fx) - i]
    fx *= 10 ** (-11 / 20)
    mono = voice.mean(axis=1) if voice.ndim == 2 else voice
    mono = mono + fx + music_bed(len(mono))
    out = np.stack([mono, mono], axis=1)
    peak = np.abs(out).max()
    if peak > 0.97: out *= 0.97 / peak
    sf.write(sys.argv[2], out, SR, subtype="PCM_24")
    print("événements", len(EVENTS), "crête", round(float(peak), 3))
