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



# ---------- « Kirène avec Orange » (images envoyées par Amadou dans images/) ----------
PHOTOS = {"eau": "pub-eau.jpg", "puce": "puce.jpg", "logo": "logo-kao.png", "produits": "produits.jpg"}
KGREEN = (46, 160, 70)
KBLUE = (20, 92, 170)
KORANGE = (255, 121, 0)

def T0(w, after=0.0):
    return wt(w, after)

t_2009 = T0("2009")
t_kirene = T0("kirène")
t_eau = T0("l'eau")
t_puces = T0("puces")
t_kao = T0("kirène", t_puces)
t_avec = T0("avec", t_kao)
t_principe = T0("principe")
t_minutes = T0("minutes")
t_orange2 = T0("orange", t_minutes)
t_revendre = T0("revendre", t_minutes)
t_utilis = T0("utilisateurs", t_revendre)
t_15 = T0("15")
t_puce2 = T0("puce", t_15)
t_toujours = T0("toujours", t_15)
t_etla = T0("et", t_toujours)
t_deux = T0("deux", t_etla)
t_dabord = T0("d'abord")
t_marque = T0("marque", t_dabord)
t_produit = T0("produit", t_marque)
t_aujourd = T0("aujourd'hui", t_produit)
t_vaut = T0("vaut")
t_si = T0("si", t_vaut)
t_aime = T0("aime")
t_qualite = T0("qualité")
t_acheter = T0("acheter", t_qualite)
t_deuxieme = T0("deuxièmement")
t_nouveau = T0("nouveau")
t_parfois = T0("parfois")
t_strat = T0("stratégique")
t_comme = T0("comme", t_strat)
t_partenariat = T0("partenariat")
t_revendre2 = T0("revendre", t_partenariat)
t_donc = T0("donc", t_revendre2)
t_choix = T0("choix")
t_nouveau2 = T0("nouveau", t_choix)
t_revendre3 = T0("revendre", t_choix)
t_prends = T0("prends")
t_strat2 = T0("stratégique", t_prends)

from edl import ISLANDS as _I
INTRO_END = 0.0
JSTART = E(_I[1][1]) + 0.1          # v2 : le jingle passe juste après sa 1re phrase (« …Kirène avec Orange. »)
JEND = JSTART + 1.15

def green_bg(img, a):
    if a <= 0: return
    bg = Image.new("RGBA", (W, H), KGREEN + (255,))
    d = ImageDraw.Draw(bg)
    for i in range(14):   # halo clair au centre
        r = 900 - i * 55
        c = tuple(int(v + (255 - v) * 0.018 * i) for v in KGREEN)
        d.ellipse((540 - r, 860 - r, 540 + r, 860 + r), fill=c + (255,))
    if a < 1: bg.putalpha(int(255 * a))
    img.alpha_composite(bg)

def intro_screen(img, t, a):
    green_bg(img, a)
    def top(p, t):
        dark_line(p, 540, 250, "POURQUOI UNE MARQUE D'EAU", 66)
        accent_line(p, 540, 360, "VEND DES PUCES ?", 76)
        sc, k = 1.0 + 0.04 * math.sin(t * 9), 1.0   # logo déjà là à l'image 0, il pulse sur le jingle
        dx, dy, z = orbit(t, 6, 4, 3.0)
        spot_glow(p, 540, 860, 380, k)
        p.rbox(540 - 300 * sc, 860 - 300 * sc, 540 + 300 * sc, 860 + 300 * sc, 60 * sc, fill=rgba(WHITE, k))
        paste(p, load(PHOTOS["logo"]), 540 + dx, 860 + dy, 560 * sc * z, k)
    img.alpha_composite(draw_area(top, t, (0, 150, 1080, 1250), a), (0, 150))

def jingle_screen(img, t, a):
    intro_screen(img, t, a)

def end_bg(img, t, a):
    green_bg(img, a)
    ImageDraw.Draw(img).rectangle((0, 0, W, H), fill=(0, 0, 0, int(90 * a)))

OPAQUE = []

# ---------- dessins ----------
def sim(p, cx, cy, s, a=1.0, col=WHITE):
    """carte SIM dessinée"""
    w, h = 150 * s, 200 * s
    p.rbox(cx - w / 2 + 6, cy - h / 2 + 10, cx + w / 2 + 6, cy + h / 2 + 10, 14 * s, fill=rgba((0, 0, 0), 0.3 * a))
    p.poly([(cx - w / 2, cy - h / 2), (cx + w / 2 - 40 * s, cy - h / 2), (cx + w / 2, cy - h / 2 + 40 * s), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], rgba(col, a))
    p.rbox(cx - 42 * s, cy - 20 * s, cx + 42 * s, cy + 50 * s, 10 * s, fill=rgba((230, 186, 60), a))
    p.line([(cx - 42 * s, cy + 15 * s), (cx + 42 * s, cy + 15 * s)], rgba((180, 140, 30), a), 3 * s)
    p.line([(cx, cy - 20 * s), (cx, cy + 50 * s)], rgba((180, 140, 30), a), 3 * s)

def orange_logo(p, cx, cy, s, a=1.0):
    p.rbox(cx - 80 * s + 5, cy - 80 * s + 8, cx + 80 * s + 5, cy + 80 * s + 8, 6 * s, fill=rgba((0, 0, 0), 0.3 * a))
    p.rbox(cx - 80 * s, cy - 80 * s, cx + 80 * s, cy + 80 * s, 4 * s, fill=rgba(KORANGE, a))
    p.text(cx - 64 * s, cy + 50 * s, "orange", "Inter-Bold", 34 * s, rgba(WHITE, a), anchor="ls")

def kirene_logo(p, cx, cy, s, a=1.0):
    p.circle(cx + 5, cy + 8, 82 * s, fill=rgba((0, 0, 0), 0.3 * a))
    p.circle(cx, cy, 82 * s, fill=rgba(WHITE, a)); p.circle(cx, cy, 74 * s, outline=rgba(KGREEN, a), width=8 * s)
    p.text(cx, cy + 4 * s, "KIRÈNE", "InterDisplay-Black", 38 * s, rgba(KBLUE, a))

def ic_sim(p, x, y, s, a, fg):
    sim(p, x, y, 0.2 * s, a, fg)
def ic_tag(p, x, y, s, a, fg):
    p.poly([(x - 24 * s, y - 18 * s), (x + 8 * s, y - 18 * s), (x + 26 * s, y), (x + 8 * s, y + 18 * s), (x - 24 * s, y + 18 * s)], rgba(fg, a))
def ic_hand(p, x, y, s, a, fg):
    p.rbox(x - 26 * s, y - 8 * s, x + 2 * s, y + 10 * s, 8 * s, fill=rgba(fg, a)); p.rbox(x - 2 * s, y - 10 * s, x + 26 * s, y + 8 * s, 8 * s, fill=rgba(fg, a))
def ic_heart2(p, x, y, s, a, fg):
    p.circle(x - 11 * s, y - 8 * s, 14 * s, fill=rgba(fg, a)); p.circle(x + 11 * s, y - 8 * s, 14 * s, fill=rgba(fg, a))
    p.poly([(x - 24 * s, y - 2 * s), (x + 24 * s, y - 2 * s), (x, y + 24 * s)], rgba(fg, a))
def ic_cart(p, x, y, s, a, fg):
    p.line([(x - 26 * s, y - 18 * s), (x - 16 * s, y - 18 * s), (x - 8 * s, y + 10 * s), (x + 20 * s, y + 10 * s), (x + 26 * s, y - 10 * s), (x - 12 * s, y - 10 * s)], rgba(fg, a), 5 * s)
    p.circle(x - 4 * s, y + 20 * s, 5 * s, fill=rgba(fg, a)); p.circle(x + 16 * s, y + 20 * s, 5 * s, fill=rgba(fg, a))
def ic_bulb2(p, x, y, s, a, fg):
    bulb(p, x, y - 6 * s, 16 * s, rgba(fg, a))
def ic_chess(p, x, y, s, a, fg):
    p.circle(x, y - 16 * s, 10 * s, fill=rgba(fg, a))
    p.poly([(x - 10 * s, y - 8 * s), (x + 10 * s, y - 8 * s), (x + 16 * s, y + 16 * s), (x - 16 * s, y + 16 * s)], rgba(fg, a))
    p.rbox(x - 22 * s, y + 14 * s, x + 22 * s, y + 24 * s, 3 * s, fill=rgba(fg, a))

# ---------- cartes au-dessus de sa tête (mur flouté, y 40-500) ----------
def card_hook(p, t):
    k = 1 - ease_io((t - (t_eau - 0.4)) / 0.3)
    if k > 0:
        dark_line(p, 540, 90, "POURQUOI UNE MARQUE D'EAU", 54, k)
        accent_line(p, 540, 180, "VEND DES PUCES ?", 62, k)
    sticker(p, 200, 330, 250, 110, t, t_2009 - 0.1, "2009", 66, fill=WHITE, fg=INK, font_="InterDisplay-Black")
    sc, a = pop(t, t_eau - 0.15)
    if a > 0:
        dx, dy, z = orbit(t, 6, 4, 4.0)
        photo(p, "eau", 540 + dx, 260 + dy, 420, a, sc * z)
        label(p, 540, 455, "de l'eau…", t, t_eau, fill=KBLUE, fg=WHITE, size=40)
    sc, a = pop(t, t_puces - 0.1)
    if a > 0:
        dx, dy, z = orbit(t, 6, 4, 4.0, 0.5)
        sim(p, 880 + dx, 290 + dy, 0.95 * sc * z, a)
        label(p, 880, 455, "…des puces", t, t_puces, fill=GOLD, fg=WHITE, size=40)

def card_kao(p, t):
    a0 = CARD_KAO
    sc, a = pop(t, a0, 0.5)
    if a > 0:
        spot_glow(p, 540, 260, 260, a)
        p.rbox(540 - 210 * sc, 260 - 210 * sc, 540 + 210 * sc, 260 + 210 * sc, 46 * sc, fill=rgba(WHITE, a))
        paste(p, load(PHOTOS["logo"]), 540, 260, 390 * sc, a)

def card_15(p, t):
    a0 = FULLS_D["principe"][1]
    k = ease_io((t - t_15 + 0.1) / 0.8)
    sc, a = pop(t, t_15 - 0.15)
    if a > 0:
        tw = p.tw("+ 15 ANS", "InterDisplay-Black", 80)
        p.rbox(330 - tw / 2 - 30, 130 - 62, 330 + tw / 2 + 30, 130 + 62, 26, fill=rgba(GOLD, a))
        p.text(330, 134, f"+ {int(round(15 * k))} ANS", "InterDisplay-Black", int(80 * sc), rgba(WHITE, a))
    sticker(p, 330, 290, 520, 100, t, t_toujours - 0.1, "TOUJOURS LÀ", 56, fill=WHITE, fg=INK, icon=ic_check, font_="InterDisplay-Black")
    sc, a = pop(t, t_puce2 - 0.15)
    if a > 0:
        dx, dy, z = orbit(t, 6, 4, 4.0)
        photo(p, "puce", 820 + dx, 270 + dy, 380, a, sc * z)

def card_marque(p, t):
    a0 = FULLS_D["l1"][1]
    sc, a = pop(t, t_vaut - 0.2)
    if a > 0:
        sticker(p, 300, 110, 320, 100, t, t_vaut - 0.2, "MARQUE", 54, fill=GOLD, fg=WHITE, icon=ic_tag, font_="InterDisplay-Black")
        p.text(540, 114, ">", "InterDisplay-Black", int(90 * sc), rgba(WHITE, a))
        sticker(p, 790, 110, 320, 100, t, t_vaut, "PRODUIT", 54, fill=WHITE, fg=INK, font_="InterDisplay-Black")
    sc, a = pop(t, t_si - 0.1)
    if a > 0 and t < t_qualite - 0.2:
        a *= 1 - ease_io((t - (t_qualite - 0.5)) / 0.3)
        dx, dy, z = orbit(t, 6, 4, 4.0)
        photo(p, "produits", 540 + dx, 335 + dy, 230, a, sc * z)
    for i in range(5):
        sc, a = pop(t, t_aime - 0.15 + i * 0.07)
        if a > 0 and t < t_qualite - 0.2:
            a *= 1 - ease_io((t - (t_qualite - 0.5)) / 0.3)
            dy = 10 * math.sin(t * 5 + i)
            ic_heart2(p, 180 + i * 50 if i < 3 else 760 + (i - 3) * 90, 280 + dy + (i % 2) * 70, 1.4 * sc, a, (235, 60, 80))
    sticker(p, 540, 300, 720, 100, t, t_qualite - 0.15, "peu importe la qualité…", 46, fill=WHITE, fg=INK)
    sticker(p, 540, 430, 640, 110, t, t_acheter - 0.1, "ILS ACHÈTENT", 60, fill=GOLD, fg=WHITE, icon=ic_cart, font_="InterDisplay-Black")

def card_strat(p, t):
    a0 = FULLS_D["l2"][1]
    sticker(p, 540, 95, 600, 110, t, t_strat - 0.15, "STRATÉGIQUE", 64, fill=GOLD, fg=WHITE, icon=ic_chess, font_="InterDisplay-Black")
    sc, a = pop(t, t_comme - 0.05)
    if a > 0:
        kirene_logo(p, 330, 290, 0.95 * sc, a)
        orange_logo(p, 750, 290, 0.95 * sc, a)
    sc, a = pop(t, t_partenariat - 0.15)
    if a > 0:
        p.circle(540, 290, 56 * sc, fill=rgba(GOLD, a)); ic_hand(p, 540, 290, 1.5 * sc, a, WHITE)
    sticker(p, 540, 450, 820, 92, t, t_revendre2 - 0.1, "Revendre un produit qui existe", 44, fill=WHITE, fg=INK, icon=ic_sim)

def card_fin(p, t):
    a0 = FULLS_D["choix"][1]
    glass(p, 540, 90, 760, 90, t, a0, "Prends le temps de réfléchir", 46, font_="InterDisplay-Black")
    sc, a = pop(t, a0 + 0.3)
    if a > 0:
        dx, dy, z = orbit(t, 4, 3, 3.0)
        spot_glow(p, 540, 270, 150, a)
        bulb(p, 540 + dx, 255 + dy, 62 * sc * z, rgba((246, 196, 40), a))
    sticker(p, 540, 440, 700, 110, t, t_strat2 - 0.15, "PLUS STRATÉGIQUE ?", 60, fill=GOLD, fg=WHITE, icon=ic_chess, font_="InterDisplay-Black")

# ---------- écrans plein écran (vidéo floutée derrière) ----------
def full_principe(p, t):
    a0 = FULLS_D["principe"][0]
    highlight(p, 540, 230, "LE PRINCIPE EST SIMPLE", 70, t, a0)
    sc, a = pop(t, t_minutes - 0.2)
    if a > 0: orange_logo(p, 220, 600, 1.1 * sc, a)
    k = ease((t - t_minutes) / 0.5)
    if k > 0:
        p.arrow(340, 600, 420, 600, k, rgba(WHITE, 0.95), 8, 26)
        chip(p, 380, 680, "minutes", k, col=WHITE, size=30)
    sc, a = pop(t, t_minutes + 0.25)
    if a > 0: kirene_logo(p, 540, 600, 1.05 * sc, a)
    k = ease((t - t_revendre + 0.1) / 0.5)
    if k > 0:
        p.arrow(660, 600, 740, 600, k, rgba(WHITE, 0.95), 8, 26)
        chip(p, 700, 680, "revend", k, col=GOLD, size=30, fg=WHITE)
    for i in range(3):
        sc, a = pop(t, t_utilis - 0.25 + i * 0.08)
        if a > 0: person(p, 830 + (i % 2) * 70, 560 + i * 45, 1.3 * sc, rgba(WHITE, a))
    sc, a = pop(t, t_revendre + 0.3)
    if a > 0:
        dx, dy, z = orbit(t, 6, 4, 4.0)
        sim(p, 540 + dx, 1000 + dy, 1.4 * sc * z, a)
    ka = appear(t, t_utilis)
    if ka > 0: p.text(540, 1250 + (1 - ka) * 20, "Le réseau d'Orange, la marque Kirène", "Inter-Bold", 46, rgba(WHITE, ka))

def full_2lecons(p, t):
    a0 = FULLS_D["2lecons"][0]
    sc, k = pop(t, t_deux - 0.15, 0.45)
    if k > 0:
        spot_glow(p, 540, 620, 300, k)
        p.circle(540, 620, 170 * sc, fill=rgba(GOLD, k))
        p.text(540, 628, "2", "InterDisplay-Black", int(230 * sc), rgba(WHITE, k))
    k1 = appear(t, t_deux + 0.1)
    p.text(540, 900 + (1 - k1) * 20, "LEÇONS MAJEURES", "InterDisplay-Black", 84, rgba(WHITE, k1))

def full_lever(n, name, txt, sub):
    def fn(p, t):
        a0 = FULLS_D[name][0]
        sc, k = pop(t, a0 - 0.05, 0.45)
        if k > 0:
            spot_glow(p, 540, 560, 260, k)
            p.circle(540, 560, 140 * sc, fill=rgba(GOLD, k))
            p.text(540, 566, str(n), "InterDisplay-Black", int(180 * sc), rgba(WHITE, k))
        k1 = appear(t, a0 + 0.1)
        fs = min(84, 84 * 980 / p.tw(txt, "InterDisplay-Black", 84))
        p.text(540, 830 + (1 - k1) * 20, txt, "InterDisplay-Black", fs, rgba(WHITE, k1))
        k2 = appear(t, a0 + 0.3)
        p.text(540, 925 + (1 - k2) * 20, sub, "Inter-Bold", 44, rgba(GREY, k2))
    return fn

def full_choix(p, t):
    a0 = FULLS_D["choix"][0]
    highlight(p, 540, 230, "TON CHOIX", 84, t, t_choix - 0.2)
    sticker(p, 540, 520, 860, 170, t, t_nouveau2 - 0.15, "CRÉER UN NOUVEAU PRODUIT", 48, fill=WHITE, fg=INK, icon=ic_bulb2, font_="InterDisplay-Black")
    sc, a = pop(t, t_nouveau2 + 0.6)
    if a > 0: p.text(540, 700, "OU", "InterDisplay-Black", int(70 * sc), rgba(WHITE, a))
    sticker(p, 540, 880, 860, 170, t, t_revendre3 - 0.15, "REVENDRE UN PRODUIT EXISTANT", 46, fill=GOLD, fg=WHITE, icon=ic_sim, font_="InterDisplay-Black")

def full_end(p, t):
    b = END0
    sc, k = pop(t, b, 0.5)
    if k > 0:
        p.rbox(540 - 150 * sc, 230 - 150 * sc, 540 + 150 * sc, 230 + 150 * sc, 34 * sc, fill=rgba(WHITE, k))
        paste(p, load(PHOTOS["logo"]), 540, 230, 280 * sc, k)
    highlight(p, 540, 460, "LA LEÇON DE KIRÈNE", 58, t, b + 0.15)
    for i, (txt, ic) in enumerate([("Vends ta marque avant ton produit", ic_tag),
                                   ("Pas besoin d'inventer", ic_bulb2),
                                   ("Pense partenariat", ic_hand)]):
        t0 = b + 0.45 + i * 0.25
        sc, kk = pop(t, t0, 0.35)
        if kk <= 0: continue
        y = 640 + i * 150
        p.circle(95, y, 50 * sc, fill=rgba(GOLD, kk)); p.text(95, y + 2, str(i + 1), "InterDisplay-Black", int(56 * sc), rgba(WHITE, kk))
        sticker(p, 590, y, 880, 118, t, t0 + 0.05, txt, 44, icon=ic, font_="InterDisplay-Black")
    sticker(p, 540, 1140, 900, 120, t, b + 1.4, "Créer ou revendre ?", 50, fill=WHITE, fg=INK, icon=ic_comment, font_="InterDisplay-Black")
    k = appear(t, b + 1.6)
    if k > 0: p.text(540, 1260 + (1 - k) * 20, "Dis-le en commentaire", "Inter-Bold", 44, rgba(WHITE, k))

# ---------- programme ----------
PRE = 0.22
FULLS = []
FULLS_D = {}
def add_full(name, a, b, fn, opaque=False):
    FULLS.append((a, b, fn, opaque)); FULLS_D[name] = (a, b)
END0 = END_SPEECH + 0.3
add_full("principe", JEND, t_15 - 0.12, full_principe)
add_full("2lecons", cut_near(t_etla - 0.1), t_dabord - 0.08, full_2lecons)
add_full("l1", t_dabord - 0.08, t_aujourd - 0.08, full_lever(1, "l1", "VENDS TA MARQUE", "plutôt que ton produit"))
add_full("l2", cut_near(t_deuxieme - 0.1), t_parfois - 0.08, full_lever(2, "l2", "PAS BESOIN D'INVENTER", "sois stratégique"))
add_full("choix", cut_near(t_donc - 0.1), cut_near(t_prends - 0.1) + 0.5, full_choix)
add_full("end", END0, TOTAL + 1, full_end, True)
FULLS.sort(key=lambda f: f[0])
assert FULLS[-1][2] is full_end

OPAQUE = [(JSTART - 0.22, JEND, jingle_screen, 0.15, 0.18), (END0 - 0.1, TOTAL + 1, end_bg, 0.35, 0.0)]

CARD_KAO = t_kao - 0.2
CARDS = [
    (INTRO_END, CARD_KAO, card_hook),
    (CARD_KAO, JSTART, card_kao),
    (FULLS_D["principe"][1], FULLS_D["2lecons"][0], card_15),
    (FULLS_D["l1"][1], FULLS_D["l2"][0], card_marque),
    (FULLS_D["l2"][1], FULLS_D["choix"][0], card_strat),
    (FULLS_D["choix"][1], FULLS_D["end"][0], card_fin),
]

# plus rythmé : petits zooms sur beaucoup de mots-clés
PUNCHES = [t_2009, t_kao, t_revendre, t_15, t_vaut, t_acheter, t_strat, t_partenariat, t_strat2]
def punch(t):
    k = 0.0
    for p0 in PUNCHES:
        if p0 <= t < p0 + 0.45: k = max(k, math.exp(-(t - p0) * 9))
    return 1 + 0.09 * k
def flash(t):
    return max([0.0] + [0.4 * math.exp(-(t - p0) * 14) for p0 in (t_kao, t_vaut, t_strat2) if p0 <= t < p0 + 0.3])
# ---------- sous-titres : blanc, contour noir, mot-clé sur pastille orange ----------
CAPS = captions()
CAP_Y = 1600
def draw_caption(img, t):
    g = next((c for c in CAPS if c["s"] <= t < c["e"]), None)
    if g is None:
        return
    size = 70
    f = font("InterDisplay-Black", size)
    sp = f.getlength(" ")
    ws = [(w["w"].upper(), w["hl"], f.getlength(w["w"].upper()), w["s"]) for w in g["words"]]
    lines, cur, cw = [], [], 0
    for x in ws:
        if cur and cw + sp + x[2] > 960:
            lines.append(cur); cur, cw = [], 0
        cur.append(x); cw += (sp if len(cur) > 1 else 0) + x[2]
    lines.append(cur)
    lay = Image.new("RGBA", (W * SS, 300 * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    lh = size * 1.18
    y = 150 - lh * len(lines) / 2 + lh / 2
    for ln in lines:
        tw = sum(x[2] for x in ln) + sp * (len(ln) - 1)
        x = (W - tw) / 2
        for wd, hl, ww, ts in ln:
            k = clamp((t - ts + 0.04) / 0.14)
            if k <= 0:
                x += ww + sp; continue
            sc = back(k) * 0.25 + 0.75
            cx = x + ww / 2
            Fs = font("InterDisplay-Black", max(8, int(size * SS * sc)))
            if hl:
                bw, bh = (ww / 2 + 14) * sc, size * 0.62 * sc
                d.rounded_rectangle(((cx - bw) * SS, (y - bh) * SS, (cx + bw) * SS, (y + bh) * SS), radius=14 * SS, fill=GOLD + (255,))
                d.text((cx * SS, y * SS + 2 * SS), wd, font=Fs, fill=WHITE + (255,), anchor="mm")
            else:
                d.text((cx * SS, y * SS + 2 * SS), wd, font=Fs, fill=WHITE + (255,), anchor="mm", stroke_width=int(7 * SS * sc), stroke_fill=(0, 0, 0, 255))
            x += ww + sp
        y += lh
    lay = lay.resize((W, 300), Image.LANCZOS)
    img.alpha_composite(lay, (0, CAP_Y - 150))

# ---------- composition ----------
def draw_area(fn, t, box_, a):
    x0, y0, x1, y1 = box_
    im = Image.new("RGBA", ((x1 - x0) * SS, (y1 - y0) * SS), (0, 0, 0, 0))
    fn(P(ImageDraw.Draw(im), SS, ox=x0, oy=y0), t)
    im = im.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    if a < 1:
        r, g, b, al = im.split()
        im = Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * a))))
    return im

FULL_BOX = (0, 120, 1080, 1520)
CARD_BOX = (0, 30, 1080, 510)

def frame(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frosts = []
    cov = full_cover(t)
    if cov > 0:
        frosts.append(((0, 0, W, H), 0, cov, 0.55))
    fa = FULLS[-1][0]
    kb = ease_io((t - (fa - 0.1)) / 0.35)
    if kb > 0:
        ImageDraw.Draw(img).rectangle((0, 0, W, H), fill=END_BG + (int(255 * kb),))
    for a, b, fn, fi, fo in OPAQUE:
        if a - 0.01 <= t < b + fo + 0.01:
            ko = min(ease_io((t - a) / fi) if fi > 0 else 1.0, 1 - ease_io((t - b) / fo) if fo > 0 else 1.0)
            if ko > 0.003:
                fn(img, t, ko)
    def glass_frosts(k):
        for (x0, y0, x1, y1), r, ga in GLASS:
            x0, y0 = max(0, x0 // 2 * 2), max(0, y0 // 2 * 2)
            x1, y1 = min(W, (x1 + 1) // 2 * 2), min(H, (y1 + 1) // 2 * 2)
            if x1 - x0 > 4 and y1 - y0 > 4:
                frosts.append(((x0, y0, x1, y1), min(r, (y1 - y0) // 2 - 1), ga * k, 0.40))
        GLASS.clear()
    for a, b, fn, _ in FULLS:
        if a - PRE - 0.05 <= t < b + PRE + 0.05:
            kc = env(t, a - 0.08, b + 0.25, 0.3, 0.25) if b < TOTAL else ease_io((t - (a - 0.08)) / 0.3)
            if kc > 0:
                GLASS.clear(); _CUR["a"] = 1.0
                img.alpha_composite(draw_area(fn, t, FULL_BOX, kc * cov), FULL_BOX[:2])
                glass_frosts(kc * cov)
    for a, b, fn in CARDS:
        if a - 0.05 <= t < b + 0.05:
            kc = env(t, a, b, 0.2, 0.3) * (1 - cov)
            if kc > 0.003:
                GLASS.clear(); _CUR["a"] = 1.0
                img.alpha_composite(draw_area(fn, t, CARD_BOX, kc), CARD_BOX[:2])
                glass_frosts(kc)
    fl = flash(t)
    if fl > 0.01:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * fl))))
    if t < END_SPEECH + 0.4:
        draw_caption(img, t)
    w = int(W * min(t / TOTAL, 1))
    if w > 1:
        ImageDraw.Draw(img).rectangle((0, 0, w, 6), fill=GOLD + (255,))
    return img, frosts

