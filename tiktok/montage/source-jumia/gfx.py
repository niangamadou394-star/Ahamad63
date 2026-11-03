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



# ---------- « Jumia » (images envoyées par Amadou dans images/) ----------
# Nouvelles règles (3 nov.) : gros titre au CENTRE dès l'image 0, rien dans les 12 % du haut (onglets TikTok),
# ~40 s, changement de cadrage (zoom serré 1,35 en alternance à chaque coupe visible).
PHOTOS = {"phone": "phone.jpg", "livreur": "livreur.jpg", "levee": "levee.jpg", "kasuwa": "kasuwa.jpg"}
JORANGE = (246, 139, 30)
from edl import ISLANDS as _I

t_ils = 0.0
t_milliard = wt("milliard")
t_dollars = wt("dollars")
t_jumia = wt("jumia")
t_amazon = wt("l'amazon")
t_senegal = wt("sénégal")
t_premiere = wt("première")
t_wall = wt("wall")
t_2019 = wt("2019")
t_comment = wt("comment")
t_rentables = wt("rentables")
t_2012 = wt("2012")
t_aucune = wt("aucune")
t_rentable1 = wt("rentable", t_aucune)
t_donc = wt("donc")
t_startup = wt("start-up")
t_il = wt("il", t_startup)
t_partout = wt("partout", t_il)
t_afrique = wt("afrique", t_partout)
t_conquerir = wt("conquérir")
t_rentable2 = wt("rentable", t_conquerir)
t_encore = wt("encore")
t_lever = wt("lever")
t_fonds = wt("fonds")
t_vendre = wt("vendre", t_fonds)
t_rentable3 = wt("rentable", t_vendre)

HOOK_END = cut_near(t_jumia - 0.05)           # coupe entre « dollars » et « Jumia »

def photo_bg(img, key, a, dark=0.55, blur=3, crop=None):
    """photo plein écran (recadrée pour remplir 1080x1920), floutée et assombrie"""
    if a <= 0: return
    im = load(PHOTOS[key]).convert("RGB")
    if crop: im = im.crop(crop)
    sc = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.BILINEAR)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    if blur: im = im.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(blur)).resize((W, H), Image.BILINEAR)
    im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), dark).convert("RGBA")
    if a < 1: im.putalpha(int(255 * a))
    img.alpha_composite(im)

def counter_text(k):
    v = int(round(1_000_000_000 * k))
    return "- " + f"{v:,}".replace(",", " ") + " $"

def hook_screen(img, t, a):
    ImageDraw.Draw(img).rectangle((0, 0, W, H), fill=(18, 16, 20, int(255 * a)))
    photo_bg(img, "phone", a, dark=0.6, blur=3)
    def mid(p, t):
        # gros titre au centre, déjà là à l'image 0 ; photo Jumia nette dessous
        dark_line(p, 540, 400, "POURQUOI JUMIA", 92)
        accent_line(p, 540, 540, "PERD DE L'ARGENT ?", 92)
        k = ease_io((t + 0.15) / (t_milliard + 0.9))
        fs = 84
        tw = p.tw("- 1 000 000 000 $", "InterDisplay-Black", fs)
        sc = 1 + 0.07 * math.exp(-(t - (t_milliard + 0.75)) * 6) if t > t_milliard + 0.75 else 1
        p.rbox(540 - tw / 2 - 34, 700 - 68, 540 + tw / 2 + 34, 700 + 68, 26, fill=rgba(RED, 1))
        p.text(540, 704, counter_text(k), "InterDisplay-Black", int(fs * sc), rgba(WHITE, 1))
        ka = appear(t, t_dollars)
        if ka > 0: p.text(540, 815 + (1 - ka) * 15, "de pertes avant la Bourse", "Inter-Bold", 50, rgba(WHITE, ka))
        im = load(PHOTOS["phone"])
        w = 980; h = w * im.height / im.width
        p.rbox(540 - w / 2 - 6, 1190 - h / 2 - 6, 540 + w / 2 + 6, 1190 + h / 2 + 6, 30, fill=rgba(WHITE, 1))
        paste(p, im, 540, 1190, w * (1 + 0.02 * t), 1, radius=24)
    img.alpha_composite(draw_area(mid, t, (0, 300, 1080, 1560), a), (0, 300))

def end_bg(img, t, a):
    photo_bg(img, "livreur", a, dark=0.72, blur=3)

# ---------- dessins ----------
def flag_sn(p, cx, cy, s, a=1.0):
    """drapeau du Sénégal complet : vert, jaune, rouge, étoile verte"""
    fw, fh = 150 * s, 100 * s; x0, y0 = cx - fw / 2, cy - fh / 2
    p.rbox(x0 + 5, y0 + 8, x0 + fw + 5, y0 + fh + 8, 8 * s, fill=rgba((0, 0, 0), 0.35 * a))
    p.rbox(x0, y0, x0 + fw, y0 + fh, 8 * s, fill=rgba((253, 239, 66), a))
    p.rbox(x0, y0, x0 + fw / 3 + 4, y0 + fh, 8 * s, fill=rgba((0, 133, 63), a))
    p.rbox(x0 + fw / 3, y0, x0 + fw / 3 + 6, y0 + fh, 0, fill=rgba((0, 133, 63), a))
    p.rbox(x0 + fw * 2 / 3 - 4, y0, x0 + fw, y0 + fh, 8 * s, fill=rgba((227, 27, 35), a))
    p.rbox(x0 + fw * 2 / 3 - 6, y0, x0 + fw * 2 / 3, y0 + fh, 0, fill=rgba((253, 239, 66), a))
    star(p, cx, cy, 22 * s, rgba((0, 133, 63), a))

def jumia_logo(p, cx, cy, s, a=1.0):
    tw = p.tw("JUMIA", "InterDisplay-Black", 64 * s)
    p.rbox(cx - tw / 2 - 70 * s + 5, cy - 46 * s + 8, cx + tw / 2 + 60 * s + 5, cy + 46 * s + 8, 18 * s, fill=rgba((0, 0, 0), 0.3 * a))
    p.rbox(cx - tw / 2 - 70 * s, cy - 46 * s, cx + tw / 2 + 60 * s, cy + 46 * s, 18 * s, fill=rgba(WHITE, a))
    p.text(cx - 18 * s, cy + 3 * s, "JUMIA", "InterDisplay-Black", 64 * s, rgba(INK, a))
    p.circle(cx + tw / 2 + 18 * s, cy, 24 * s, fill=rgba(JORANGE, a)); star(p, cx + tw / 2 + 18 * s, cy, 15 * s, rgba(WHITE, a))

def chart(p, x0, y0, w, h, k, a=1.0, col=None):
    """courbe de bourse qui monte (k = avancement)"""
    col = col or (52, 199, 120)
    pts = [(0, 0.2), (0.15, 0.35), (0.3, 0.3), (0.45, 0.55), (0.6, 0.5), (0.78, 0.8), (1.0, 0.95)]
    n = max(2, int(len(pts) * k) + 1)
    q = [(x0 + w * u, y0 + h - h * v) for u, v in pts[:n]]
    p.line(q, rgba(col, a), 10)

def pin(p, cx, cy, s, a=1.0, col=None):
    col = col or RED
    p.poly([(cx - 26 * s, cy - 30 * s), (cx + 26 * s, cy - 30 * s), (cx, cy + 20 * s)], rgba(col, a))
    p.circle(cx, cy - 40 * s, 30 * s, fill=rgba(col, a)); p.circle(cx, cy - 40 * s, 12 * s, fill=rgba(WHITE, a))

def ic_pin(p, x, y, s, a, fg):
    pin(p, x, y + 14 * s, 0.6 * s, a, fg)
def ic_money(p, x, y, s, a, fg):
    p.rbox(x - 28 * s, y - 16 * s, x + 28 * s, y + 16 * s, 5 * s, fill=rgba(fg, a))
    p.circle(x, y, 9 * s, fill=rgba(GOLD if fg == WHITE else WHITE, a))
def ic_x(p, x, y, s, a, fg):
    xmark(p, x, y, 15 * s, rgba(fg, a), width=7 * s)
def ic_target(p, x, y, s, a, fg):
    p.circle(x, y, 24 * s, outline=rgba(fg, a), width=5 * s); p.circle(x, y, 12 * s, outline=rgba(fg, a), width=5 * s); p.circle(x, y, 4 * s, fill=rgba(fg, a))
def ic_cart(p, x, y, s, a, fg):
    p.line([(x - 26 * s, y - 18 * s), (x - 16 * s, y - 18 * s), (x - 8 * s, y + 10 * s), (x + 20 * s, y + 10 * s), (x + 26 * s, y - 10 * s), (x - 12 * s, y - 10 * s)], rgba(fg, a), 5 * s)
    p.circle(x - 4 * s, y + 20 * s, 5 * s, fill=rgba(fg, a)); p.circle(x + 16 * s, y + 20 * s, 5 * s, fill=rgba(fg, a))

# ---------- cartes au-dessus de sa tête (zone 240-500 : rien sous les onglets TikTok) ----------
def card_intro(p, t):
    sc, a = pop(t, HOOK_END + 0.05)
    if a > 0: jumia_logo(p, 360, 300, 1.0 * sc, a)
    sticker(p, 360, 430, 560, 88, t, t_amazon - 0.1, "l'Amazon de l'Afrique", 44, fill=GOLD, fg=WHITE, icon=ic_cart)
    sc, a = pop(t, t_senegal - 0.15)
    if a > 0:
        dx, dy, z = orbit(t, 5, 3, 3.0)
        flag_sn(p, 850 + dx, 300 + dy, 1.2 * sc * z, a)
        label(p, 850, 430, "au Sénégal", t, t_senegal, fill=WHITE, fg=INK, size=40)

def card_rentable(p, t):
    sticker(p, 540, 300, 640, 120, t, t_comment - 0.1, "Pas rentable ?", 64, fill=WHITE, fg=INK, font_="InterDisplay-Black")
    stamp(p, 540, 440, "COMMENT ?", 60, t, t_rentables - 0.1, -6, col=RED)

def card_startup(p, t):
    sticker(p, 540, 300, 600, 110, t, t_donc + 0.1, "Toi qui lances", 56, fill=WHITE, fg=INK, font_="InterDisplay-Black")
    sticker(p, 540, 430, 560, 100, t, t_startup - 0.15, "TA START-UP", 58, fill=GOLD, fg=WHITE, icon=ic_bulb, font_="InterDisplay-Black")

def ic_bulb(p, x, y, s, a, fg):
    bulb(p, x, y - 6 * s, 16 * s, rgba(fg, a))

def card_partout(p, t):
    k = 1 - ease_io((t - (t_conquerir - 0.4)) / 0.3)
    if k > 0:
        for i, (x, y) in enumerate([(200, 330), (330, 270), (470, 350), (610, 280), (750, 340), (880, 290)]):
            sc, a = pop(t, t_partout - 0.3 + i * 0.06)
            if a > 0: pin(p, x, y, 1.0 * sc, a * k, WHITE)
        stamp(p, 540, 440, "PARTOUT EN AFRIQUE ?", 52, t, t_afrique - 0.05, -5, col=RED)
    if t > t_conquerir - 0.4:
        sc, a = pop(t, t_conquerir - 0.1)
        if a > 0:
            spot_glow(p, 540, 300, 140, a); pin(p, 540, 330, 1.6 * sc, a, GOLD)
        sticker(p, 540, 450, 820, 100, t, t_conquerir, "CONQUIERS LÀ OÙ TU ES", 52, fill=GOLD, fg=WHITE, icon=ic_target, font_="InterDisplay-Black")

# ---------- écrans plein écran (vidéo floutée derrière) ----------
def full_wall(p, t):
    a0 = FULLS_D["wall"][0]
    highlight(p, 540, 420, "WALL STREET", 110, t, a0 - 0.05)
    sc, a = pop(t, a0 + 0.1)
    if a > 0:
        p.rbox(200, 560, 880, 960, 30, fill=rgba((0, 0, 0), 0.35 * a))
        chart(p, 240, 600, 600, 320, ease_io((t - a0 - 0.1) / 1.4), a)
    sticker(p, 540, 1080, 560, 130, t, t_2019 - 0.1, "2019", 86, fill=WHITE, fg=INK, font_="InterDisplay-Black")
    ka = appear(t, t_2019 + 0.3)
    if ka > 0: p.text(540, 1230 + (1 - ka) * 15, "entrée à la Bourse de New York", "Inter-Bold", 48, rgba(WHITE, ka))

def full_2012(p, t):
    a0 = FULLS_D["2012"][0]
    k0 = appear(t, a0 - 0.05)
    p.text(540, 330 + (1 - k0) * 15, "DEPUIS 2012", "InterDisplay-Black", 96, rgba(WHITE, k0))
    years = list(range(2012, 2026))
    for i, y in enumerate(years):
        col, row = i % 5, i // 5
        x, yy = 170 + col * 185, 560 + row * 220
        t0 = t_2012 + 0.05 + i * 0.12
        sc, a = pop(t, t0, 0.3)
        if a <= 0: continue
        p.rbox(x - 80 * sc, yy - 60 * sc, x + 80 * sc, yy + 60 * sc, 18 * sc, fill=rgba(WHITE, 0.92 * a))
        p.text(x, yy - 14, str(y), "InterDisplay-Black", int(40 * sc), rgba(INK, a))
        if t > t0 + 0.15: xmark(p, x, yy + 26, 16, rgba(RED, a), clamp((t - t0 - 0.15) / 0.2), 7)
    highlight(p, 540, 1260, "AUCUNE ANNÉE RENTABLE", 70, t, t_aucune - 0.1)
    ka = appear(t, t_rentable1 + 0.2)
    if ka > 0: p.text(540, 1370, "perte 2025 : 60 millions $", "Inter-Bold", 44, rgba(GREY, ka))

def full_lever(p, t):
    a0 = FULLS_D["lever"][0]
    sc, a = pop(t, t_lever - 0.15)
    if a > 0:
        dx, dy, z = orbit(t, 6, 4, 4.0)
        im = load(PHOTOS["levee"]).crop((0, 70, 399, 330)).convert("RGBA")
        w = 640 * sc * z; h = w * im.height / im.width
        p.rbox(540 - w / 2 - 6, 520 - h / 2 - 6, 540 + w / 2 + 6, 520 + h / 2 + 6, 30, fill=rgba(WHITE, a))
        paste(p, im, 540 + dx, 520 + dy, w, a, radius=24)
    sticker(p, 540, 830, 760, 130, t, t_fonds - 0.1, "LEVER DES FONDS", 70, fill=WHITE, fg=INK, icon=ic_money, font_="InterDisplay-Black")
    sc, a = pop(t, t_vendre)
    if a > 0: p.text(540, 960, "≠", "InterDisplay-Black", int(120 * sc), rgba(WHITE, a))
    sticker(p, 540, 1100, 760, 130, t, t_rentable3 - 0.15, "ÊTRE RENTABLE", 76, fill=GOLD, fg=WHITE, font_="InterDisplay-Black")

def full_end(p, t):
    b = END0
    k = appear(t, b)
    p.text(540, 330 + (1 - k) * 15, "LA LEÇON DE JUMIA", "InterDisplay-Black", 76, rgba(WHITE, k))
    for i, (txt, ic) in enumerate([("Lever des fonds ≠ gagner de l'argent", ic_money),
                                   ("Être partout ≠ être rentable", ic_pin),
                                   ("Conquiers d'abord là où tu es", ic_target)]):
        t0 = b + 0.3 + i * 0.22
        sc, kk = pop(t, t0, 0.35)
        if kk <= 0: continue
        y = 530 + i * 150
        p.circle(95, y, 50 * sc, fill=rgba(GOLD, kk)); p.text(95, y + 2, str(i + 1), "InterDisplay-Black", int(56 * sc), rgba(WHITE, kk))
        sticker(p, 590, y, 880, 118, t, t0 + 0.05, txt, 40, icon=ic, font_="InterDisplay-Black")
    sticker(p, 540, 1020, 900, 130, t, b + 1.1, "Tu commandes encore sur Jumia ?", 46, fill=GOLD, fg=WHITE, icon=ic_comment, font_="InterDisplay-Black")
    k = appear(t, b + 1.3)
    if k > 0: p.text(540, 1150 + (1 - k) * 15, "Dis-le en commentaire", "Inter-Bold", 46, rgba(WHITE, k))

# ---------- programme ----------
PRE = 0.22
FULLS = []
FULLS_D = {}
def add_full(name, a, b, fn, opaque=False):
    FULLS.append((a, b, fn, opaque)); FULLS_D[name] = (a, b)
END0 = END_SPEECH + 0.3
add_full("wall", cut_near(t_wall - 0.6), cut_near(t_comment - 0.1), full_wall)        # cache la coupe du mot retiré et la suivante
add_full("2012", cut_near(t_2012 - 0.1), cut_near(t_donc - 0.1), full_2012)
add_full("lever", cut_near(t_encore - 0.1), END0 - 0.05, full_lever)
add_full("end", END0, TOTAL + 1, full_end, True)
FULLS.sort(key=lambda f: f[0])
assert FULLS[-1][2] is full_end

OPAQUE = [(0.0, HOOK_END, hook_screen, 0.0, 0.2), (END0 - 0.1, TOTAL + 1, end_bg, 0.35, 0.0)]
INTRO_END = HOOK_END

CARDS = [
    (HOOK_END, FULLS_D["wall"][0], card_intro),
    (FULLS_D["wall"][1], FULLS_D["2012"][0], card_rentable),
    (FULLS_D["2012"][1], cut_near(t_il - 0.1), card_startup),
    (cut_near(t_il - 0.1), FULLS_D["lever"][0], card_partout),
]

PUNCHES = [t_senegal, t_rentables, t_startup, t_conquerir, t_rentable2]
def punch(t):
    k = 0.0
    for p0 in PUNCHES:
        if p0 <= t < p0 + 0.45: k = max(k, math.exp(-(t - p0) * 9))
    return 1 + 0.08 * k
def flash(t):
    return max([0.0] + [0.4 * math.exp(-(t - p0) * 14) for p0 in (t_rentables, t_conquerir) if p0 <= t < p0 + 0.3])
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

