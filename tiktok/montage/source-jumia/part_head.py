# Calque graphique « JOJ Dakar 2026 » (accent orange). Images des JO et de Moduvated envoyées par Amadou.
from gfx_base import *
from gfx_base import _f
import os
from edl import S
from words import words as _words

HERE = os.path.dirname(os.path.abspath(__file__))
END_BG = (16, 14, 13)
RED = (226, 60, 50)
GREEN = (52, 199, 120)
ORANGE = (255, 121, 0)

def T(seg, t):
    """temps du rush dans le segment seg -> temps du montage"""
    return E(S(seg, t))

_WL = _words()
def wt(txt, after=0.0):
    """début (temps du montage) du premier mot qui commence par txt, après after"""
    txt = txt.lower()
    return next(w["s"] for w in _WL if w["w"].lower().strip(",.?«»").startswith(txt) and w["s"] >= after - 1e-6)

# ---------- images fournies par Amadou ----------
_img = {}
def load(name):
    if name not in _img:
        _img[name] = Image.open(os.path.join(HERE, "images", name)).convert("RGBA")
    return _img[name]

def paste(p, im, cx, cy, w, a=1.0, radius=0):
    W2 = max(2, int(w * p.s * p.z)); H2 = max(2, int(W2 * im.height / im.width))
    r = im.resize((W2, H2), Image.LANCZOS)
    if radius:
        m = Image.new("L", r.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, W2 - 1, H2 - 1), radius=int(radius * p.s * p.z), fill=255)
        r.putalpha(Image.composite(r.split()[3], Image.new("L", r.size, 0), m))
    if a < 1:
        r.putalpha(r.split()[3].point(lambda v: int(v * a)))
    x, y = p.xy(cx, cy)
    p.d._image.alpha_composite(r, (int(x - W2 / 2), int(y - H2 / 2)))

PHOTOS = {}
LOGOS = {}

def photo(p, key, cx, cy, w, a=1.0, sc=1.0, border=True):
    """photo fournie par Amadou, coins arrondis, liseré blanc et ombre"""
    im = load(PHOTOS[key]); w *= sc; h = w * im.height / im.width
    p.rbox(cx - w / 2 + 8, cy - h / 2 + 12, cx + w / 2 + 8, cy + h / 2 + 12, 26 * sc, fill=rgba((0, 0, 0), 0.35 * a))
    if border:
        p.rbox(cx - w / 2 - 6, cy - h / 2 - 6, cx + w / 2 + 6, cy + h / 2 + 6, 30 * sc, fill=rgba(WHITE, a))
    paste(p, im, cx, cy, w, a, radius=24 * sc)
    return h

def photo_pop(p, key, cx, cy, w, t, t0):
    k, a = pop(t, t0)
    if a > 0: return photo(p, key, cx, cy, w, a, k)

# ---------- effets demandés : verre (un peu), orbite (un peu), spotlight ----------
GLASS = []          # vitres floutées de la carte en cours : (rect, rayon, alpha), lues par frame()
_CUR = {"a": 1.0, "ox": 0, "oy": 0}

def orbit(t, rx=10, ry=6, period=6.0, phase=0.0):
    """léger mouvement d'orbite : décalage (dx, dy) et échelle (profondeur)"""
    w = 2 * math.pi * (t / period + phase)
    return rx * math.cos(w), ry * math.sin(w), 1 + 0.025 * math.sin(w)

def glass_box(p, x0, y0, x1, y1, r, a):
    """vitre : flou + léger voile sombre (fait au rendu), voile blanc et liseré clair"""
    if a <= 0.01: return
    GLASS.append(((int(x0), int(y0), int(x1), int(y1)), int(r), a * _CUR["a"]))
    p.rbox(x0, y0, x1, y1, r, fill=rgba(WHITE, 0.10 * a), outline=rgba(WHITE, 0.55 * a), width=2.5)

def glass(p, cx, cy, w, h, t, t0, txt, size=40, icon=None, font_="Inter-ExtraBold", fg=WHITE):
    """étiquette en verre qui rebondit à son apparition (texte blanc)"""
    sc, a = pop(t, t0)
    if a <= 0: return 0
    w2, h2 = w * sc / 2, h * sc / 2
    glass_box(p, cx - w2, cy - h2, cx + w2, cy + h2, h * sc / 2.6, a)
    tx = cx
    if icon:
        iw = h * 0.62
        tw = p.tw(txt, font_, size)
        x0 = cx - (iw + 18 + tw) / 2 * sc
        icon(p, x0 + iw / 2 * sc, cy, sc * h / 100, a, fg)
        tx = x0 + (iw + 18) * sc + tw * sc / 2
    p.text(tx + 2, cy + 4, txt, font_, max(8, int(size * sc)), rgba((0, 0, 0), 0.35 * a))
    p.text(tx, cy + 2, txt, font_, max(8, int(size * sc)), rgba(fg, a))
    return a

def orbit_ring(p, cx, cy, rx, ry, t, a=1.0, n=2):
    """anneau d'orbite discret autour d'une image, avec de petits points orange qui tournent"""
    if a <= 0: return
    p.d.ellipse((*p.xy(cx - rx, cy - ry), *p.xy(cx + rx, cy + ry)), outline=rgba(WHITE, 0.22 * a), width=max(1, int(2 * p.s)))
    for i in range(n):
        w = 2 * math.pi * (t / 5.0 + i / n)
        x, y = cx + rx * math.cos(w), cy + ry * math.sin(w)
        p.circle(x, y, 9 + 3 * math.sin(w), fill=rgba(GOLD, a))

_glow = {}
def spot_glow(p, cx, cy, r, a=1.0):
    """halo de lumière derrière une image (spotlight)"""
    k = int(r * p.s)
    if k not in _glow:
        g = Image.new("L", (2 * k, 2 * k), 0)
        ImageDraw.Draw(g).ellipse((k * 0.35, k * 0.35, k * 1.65, k * 1.65), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(k * 0.28))
        im = Image.new("RGBA", g.size, (255, 236, 210, 0)); im.putalpha(g.point(lambda v: int(v * 0.30)))
        _glow[k] = im
    im = _glow[k]
    if a < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    x, y = p.xy(cx, cy)
    p.d._image.alpha_composite(im, (int(x - k), int(y - k)))

def image_orb(p, key, cx, cy, w, t, t0, phase=0.0, rx=10, ry=6, ring=False):
    """image fournie qui apparaît puis flotte doucement en orbite, avec halo derrière"""
    sc, a = pop(t, t0, 0.5)
    if a <= 0: return
    dx, dy, z = orbit(t, rx, ry, 7.0, phase)
    im = load(PHOTOS[key]); h = w * im.height / im.width
    spot_glow(p, cx, cy, max(w, h) * 0.8, a)
    if ring: orbit_ring(p, cx, cy, w * 0.62, h * 0.62 + 30, t, a)
    photo(p, key, cx + dx, cy + dy, w, a, sc * z)

# ---------- dessins ----------
def layer(p, w, h, draw, cx, cy, ang=0.0, a=1.0):
    """dessine sur un calque à part (coordonnées locales 0..w, 0..h), le tourne et le pose centré en (cx, cy)"""
    lay = Image.new("RGBA", (int(w * p.s), int(h * p.s)), (0, 0, 0, 0))
    draw(P(ImageDraw.Draw(lay), p.s))
    if ang: lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    if a < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * a)))
    X0, Y0 = p.xy(cx, cy)
    p.d._image.alpha_composite(lay, (int(X0 - lay.width / 2), int(Y0 - lay.height / 2)))

def stamp(p, cx, cy, txt, size, t, t0, ang=-12, col=RED, bg=True):
    """tampon qui s'écrase : grossi puis posé, légèrement penché"""
    k = clamp((t - t0) / 0.18)
    if k <= 0: return
    sc = 1 + 0.6 * (1 - ease(k))
    a = clamp((t - t0) / 0.08)
    tw = p.tw(txt, "InterDisplay-Black", size)
    w, h = tw + size, size * 1.5
    def dr(q):
        S2 = sc
        c, m = (w * S2 + 20) / 2, (h * S2 + 20) / 2
        q.rbox(c - w * S2 / 2, m - h * S2 / 2, c + w * S2 / 2, m + h * S2 / 2, size * 0.22 * S2,
               fill=rgba(WHITE, 0.94) if bg else None, outline=rgba(col, 1), width=size * 0.11 * S2)
        q.text(c, m + size * 0.04 * S2, txt, "InterDisplay-Black", size * S2, rgba(col, 1))
    layer(p, w * sc + 20, h * sc + 20, dr, cx, cy, ang, a)

def label(p, cx, cy, txt, t, t0, fill=WHITE, fg=INK, size=34):
    tw = p.tw(txt, "InterDisplay-Black", size)
    sticker(p, cx, cy, tw + 50, size * 1.9, t, t0, txt, size, fill=fill, fg=fg, font_="InterDisplay-Black")

_lg = {}
def logo(p, key, cx, cy, d, a=1.0, grey=0.0, round_=None):
    """logo envoyé par Amadou (Wari et Tigo ronds, Orange Money et Wave carrés arrondis) ; grey = passage au gris"""
    k = (key, round(grey, 2))
    if k not in _lg:
        im = Image.open(os.path.join(HERE, LOGOS[key])).convert("RGBA")
        if grey > 0:
            g = im.convert("L").convert("RGBA"); g.putalpha(im.split()[3])
            g = Image.eval(g, lambda v: v)
            im = Image.blend(im, g, grey)
            im.putalpha(Image.open(os.path.join(HERE, LOGOS[key])).convert("RGBA").split()[3])
        _lg[k] = im
    im = _lg[k]
    if a <= 0: return
    r = round_ if round_ is not None else (0 if key in ("airbnb",) else 0.22 * d)
    p.circle(cx + 5, cy + 9, d / 2, fill=rgba((0, 0, 0), 0.30 * a)) if key in ("airbnb",) else \
        p.rbox(cx - d / 2 + 5, cy - d / 2 + 9, cx + d / 2 + 5, cy + d / 2 + 9, r, fill=rgba((0, 0, 0), 0.30 * a))
    paste(p, im, cx, cy, d, a, radius=r)

def logo_pop(p, key, cx, cy, d, t, t0, grey=0.0):
    sc, a = pop(t, t0)
    if a > 0: logo(p, key, cx, cy, d * sc, a, grey)

def ic_up(p, x, y, s, a, fg):
    p.arrow(x - 20 * s, y + 20 * s, x + 20 * s, y - 20 * s, 1, rgba(fg, a), 7 * s, 22 * s)
def ic_star(p, x, y, s, a, fg):
    star(p, x, y, 26 * s, rgba(fg, a))

def crown(p, x, y, s, a):
    p.poly([(x - 34 * s, y + 18 * s), (x - 40 * s, y - 22 * s), (x - 16 * s, y), (x, y - 30 * s), (x + 16 * s, y), (x + 40 * s, y - 22 * s), (x + 34 * s, y + 18 * s)], rgba((246, 196, 40), a))

def dark_line(p, x, y, txt, size, a=1.0):
    tw = p.tw(txt, "InterDisplay-Black", size)
    glass_box(p, x - tw / 2 - 24, y - size * 0.72, x + tw / 2 + 24, y + size * 0.72, 18, a)
    p.text(x, y + 3, txt, "InterDisplay-Black", size, rgba(WHITE, a))

def accent_line(p, x, y, txt, size, a=1.0):
    tw = p.tw(txt, "InterDisplay-Black", size)
    p.rbox(x - tw / 2 - 24, y - size * 0.72, x + tw / 2 + 24, y + size * 0.72, 18, fill=rgba(GOLD, a))
    p.text(x, y + 3, txt, "InterDisplay-Black", size, rgba(WHITE, a))

def highlight(p, x, y, txt, size, t, t0, font_="InterDisplay-Black"):
    k = ease((t - t0) / 0.4)
    if k <= 0: return
    tw = p.tw(txt, font_, size)
    x0 = x - tw / 2 - 26
    p.rbox(x0, y - size * 0.72, lerp(x0, x + tw / 2 + 26, k), y + size * 0.72, 18, fill=rgba(GOLD, 1))
    if k > 0.5:
        p.text(x, y + 3, txt, font_, size, rgba(WHITE, clamp((k - 0.5) * 3)))

def numbered(p, t, t0, n, y, txt, ic, x_num=110, w=800, size=40, h=88):
    sc, a = pop(t, t0)
    if a <= 0: return
    p.circle(x_num, y, 42 * sc, fill=rgba(GOLD, a)); p.text(x_num, y + 2, str(n), "InterDisplay-Black", int(48 * sc), rgba(WHITE, a))
    glass(p, x_num + 60 + w / 2, y, w, h, t, t0 + 0.05, txt, size, icon=ic)

def ic_coin(p, x, y, s, a, fg):
    p.circle(x, y, 25 * s, outline=rgba(fg, a), width=5 * s)
    p.text(x, y + 1 * s, "$", "InterDisplay-Black", 30 * s, rgba(fg, a))
def ic_seed(p, x, y, s, a, fg):
    p.line([(x, y + 24 * s), (x, y - 6 * s)], rgba(fg, a), 6 * s)
    p.d.chord((*p.xy(x - 26 * s, y - 26 * s), *p.xy(x + 2 * s, y + 2 * s)), 0, 360, fill=rgba(fg, a))
    p.d.chord((*p.xy(x - 2 * s, y - 22 * s), *p.xy(x + 24 * s, y + 4 * s)), 0, 360, fill=rgba(fg, a))
def ic_heart(p, x, y, s, a, fg):
    p.circle(x - 11 * s, y - 8 * s, 14 * s, fill=rgba(fg, a)); p.circle(x + 11 * s, y - 8 * s, 14 * s, fill=rgba(fg, a))
    p.poly([(x - 24 * s, y - 2 * s), (x + 24 * s, y - 2 * s), (x, y + 24 * s)], rgba(fg, a))
def ic_case(p, x, y, s, a, fg):
    p.rbox(x - 26 * s, y - 14 * s, x + 26 * s, y + 22 * s, 6 * s, fill=rgba(fg, a))
    p.rbox(x - 10 * s, y - 24 * s, x + 10 * s, y - 12 * s, 4 * s, outline=rgba(fg, a), width=4 * s)
def ic_box(p, x, y, s, a, fg):
    p.rbox(x - 26 * s, y - 12 * s, x + 26 * s, y + 20 * s, 4 * s, fill=rgba(fg, a))
    p.rbox(x - 30 * s, y - 22 * s, x + 30 * s, y - 10 * s, 3 * s, fill=rgba(fg, a))

def env(t, a, b, fi=0.3, fo=0.3):
    return min(ease_io((t - a) / fi) if a > 0 else 1.0, 1 - ease_io((t - (b - fo)) / fo) if b < TOTAL else 1.0)

def full_cover(t):
    k = 0.0
    for a, b, _, _ in FULLS:
        kin = ease_io((t - (a - PRE)) / (PRE - 0.03))
        kout = 1 - ease_io((t - (b + 0.03)) / (PRE - 0.03)) if b < TOTAL else 1
        k = max(k, min(kin, kout))
    return k


