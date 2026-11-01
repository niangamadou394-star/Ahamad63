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


# ---------- images vidéo envoyées par Amadou (cérémonie d'ouverture, Moduvated) ----------
# Images extraites à 30 i/s, déjà recadrées sans les filigranes : broll/cer (576x405), broll/mod (576x520).
BROLL = os.path.join(HERE, "broll")
_bimg = {}
def bframe(kind, ts, crop=None):
    n = max(1, int(round(ts * 30)) + 1)
    last = len(os.listdir(os.path.join(BROLL, kind))) if (kind, "n") not in _bimg else _bimg[(kind, "n")]
    _bimg[(kind, "n")] = last
    n = min(n, last)
    im = Image.open(os.path.join(BROLL, kind, f"{n:05d}.jpg")).convert("RGB")
    if crop: im = im.crop(crop)
    return im

def shot_at(shots, t):
    """shots = [(début montage, dossier, début source, recadrage)] -> image du plan à l'instant t"""
    cur = shots[0]
    for s in shots:
        if t >= s[0]: cur = s
    t0, kind, src, crop = cur
    return bframe(kind, src + max(0.0, t - t0), crop)

def broll_screen(img, frame_im, a, cy=860, w=1080, zoom=1.0, dark=0.45):
    """plein écran opaque : la même image agrandie et floutée en fond, l'image nette au centre"""
    if a <= 0: return
    bw = 54; bh = int(bw * H / W)
    fw, fh = frame_im.size
    sc = max(bw / fw, bh / fh)
    bg = frame_im.resize((max(1, int(fw * sc)), max(1, int(fh * sc))), Image.BILINEAR)
    bg = bg.crop(((bg.width - bw) // 2, (bg.height - bh) // 2, (bg.width - bw) // 2 + bw, (bg.height - bh) // 2 + bh))
    bg = bg.filter(ImageFilter.GaussianBlur(2.5)).resize((W, H), Image.BILINEAR)
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), dark).convert("RGBA")
    ww = int(w * zoom); hh = int(ww * fh / fw)
    sharp = frame_im.resize((ww, hh), Image.LANCZOS)
    bg.paste(sharp, ((W - ww) // 2, int(cy - hh / 2)))
    if a < 1: bg.putalpha(int(255 * a))
    img.alpha_composite(bg)

# ---------- temps clés (montage) ----------
t_hier = 0.0
t_fierte = wt("fierté")
t_honor = wt("honorés")
t_accueil = wt("accueilli")
t_celeb = wt("célébré")
t_raconte = wt("raconté")
t_repr = wt("représenté")
t_afrique = wt("l'afrique")
t_monde = wt("monde")
t_mais = wt("mais", t_monde)
t_entre = wt("entrepreneuriat")
t_quest = wt("qu'est-ce")
t_cequil = wt("ce", t_quest + 0.5)
t_70 = wt("70")
t_marches = wt("marchés")
t_senega = wt("sénégalaises")
t_etla = wt("et", t_senega)
t_monde2 = wt("monde", t_senega)
t_clients = wt("clients")
t_plus = wt("plus", t_clients)
t_2700 = wt("2700", t_plus)
t_equipes = wt("équipes")
t_sans = wt("sans", t_equipes)
t_artist = wt("artistique")
t_tour = wt("touristes")
t_lune = wt("l'une")
t_quil = wt("qu'il", t_lune)
t_petites = wt("petites")
t_moyennes = wt("moyennes")
t_brille = wt("brillé")
t_etla2 = wt("et", t_brille)
t_modu = wt("moduvated")
t_multi = wt("multinationale")
t_demarq = wt("démarquer")
t_retenir = wt("retenir")
t_annees = wt("d'années")
t_prep = wt("préparation")
t_derriere = wt("derrière")
t_travail = wt("travail")
t_debut = wt("début")
t_artist2 = wt("artistique", t_debut)
t_orga = wt("organisation")
t_finan = wt("financement")
t_sacr = wt("sacrifices")
t_cetait = wt("c'était")
t_top = wt("top")

INTRO_END = cut_near(t_monde + 0.5)          # coupe entre la 1re et la 2e prise
MODU_A = min(t_etla2 - 0.15, cut_near(t_etla2) - 0.3)
MODU_B = cut_near(t_demarq + 0.6)             # coupe vers « Et ce qu'on peut surtout retenir »

# plans de la cérémonie posés sur les mots de l'intro (source : TikTok de la cérémonie, sans les filigranes)
CER = [
    (0.0, "cer", 1.5, None),               # drapeau du Sénégal
    (t_fierte - 0.35, "cer", 4.55, None),  # supportrice en jaune
    (t_fierte + 0.65, "cer", 5.75, None),  # danseuse en or
    (t_honor - 0.45, "cer", 27.85, None),  # « 2026 » sur la pelouse
    (t_accueil - 0.2, "cer", 31.1, None),  # « DAKAR »
    (t_celeb - 0.2, "cer", 35.9, None),    # artistes
    (t_raconte - 0.2, "cer", 15.3, None),  # costume traditionnel
    (t_repr - 0.1, "cer", 41.9, None),     # l'Afrique formée par les danseurs
    (t_monde - 0.45, "cer", 44.6, None),   # l'Afrique en lumière
]
MOD = [
    (MODU_A, "mod", 54.2, None),           # façade de la salle
    (t_modu + 0.55, "mod", 41.0, None),    # salle de musculation
    (t_multi - 0.3, "mod", 28.4, None),    # plafond éclair
    (t_demarq - 0.3, "mod", 30.2, None),
]
END_SHOTS = [(0.0, "cer", 41.9, None)]

# ---------- écrans opaques (images vidéo) ----------
def intro_screen(img, t, a):
    broll_screen(img, shot_at(CER, t), a, cy=880, zoom=1.0 + 0.03 * t / max(INTRO_END, 1))
    def top(p, t):
        dark_line(p, 540, 255, "POURQUOI LES JOJ", 76)
        accent_line(p, 540, 375, "PROFITENT À NOS PME", 76)
        glass(p, 540, 1330, 820, 80, t, 0.0, "Dakar 2026 · Jeux Olympiques de la Jeunesse", 34)
    im = draw_area(top, t, (0, 150, 1080, 1450), a)
    img.alpha_composite(im, (0, 150))

def modu_screen(img, t, a):
    broll_screen(img, shot_at(MOD, t), a, cy=960, w=860)
    def top(p, t):
        highlight(p, 540, 280, "MODUVATED", 84, t, MODU_A + 0.1)
        glass(p, 540, 400, 560, 84, t, MODU_A + 0.3, "Salle de sport à Dakar", 42, icon=ic_pin)
        sticker(p, 540, 1430, 900, 100, t, t_modu + 0.2, "Salle de fitness du Village olympique", 42, fill=GOLD, fg=WHITE, icon=ic_star)
    im = draw_area(top, t, (0, 150, 1080, 1500), a)
    img.alpha_composite(im, (0, 150))
    def mid(p, t):
        stamp(p, 540, 820, "PAS UNE MULTINATIONALE", 58, t, t_multi - 0.1, -6, col=RED)
        if t > t_demarq - 0.2:
            sticker(p, 540, 980, 780, 100, t, t_demarq - 0.1, "ELLE S'EST DÉMARQUÉE", 48, fill=WHITE, fg=INK, icon=ic_up, font_="InterDisplay-Black")
    if t > t_multi - 0.2:
        img.alpha_composite(draw_area(mid, t, (0, 650, 1080, 1100), a), (0, 650))

def end_bg(img, t, a):
    broll_screen(img, shot_at(END_SHOTS, t - END0), a, cy=960, w=1700, dark=0.72)

OPAQUE = []   # (début, fin, fonction, fondu d'entrée, fondu de sortie)

# ---------- cartes au-dessus de sa tête (mur flouté, y 40-500) ----------
def card_business(p, t):
    a0 = INTRO_END
    glass(p, 540, 90, 760, 84, t, a0 + 0.1, "Au-delà de l'événement…", 42, font_="InterDisplay-Black")
    sticker(p, 540, 240, 640, 110, t, t_entre - 0.1, "CÔTÉ BUSINESS", 64, fill=GOLD, fg=WHITE, icon=ic_case, font_="InterDisplay-Black")
    sc, a = pop(t, t_quest)
    if a > 0:
        p.circle(540, 410, 56 * sc, fill=rgba(WHITE, a))
        p.text(540, 414, "?", "InterDisplay-Black", int(76 * sc), rgba(GOLD, a))

def card_2700(p, t):
    a0 = FULLS_D["l1"][1]
    k = ease_io((t - t_2700 + 0.1) / 0.7)
    sc, a = pop(t, t_2700 - 0.15)
    if a > 0:
        txt = f"+ {int(round(2700 * k)):,}".replace(",", " ")
        tw = p.tw("+ 2 700", "InterDisplay-Black", 96)
        p.rbox(540 - tw / 2 - 40, 150 - 72, 540 + tw / 2 + 40, 150 + 72, 30, fill=rgba(GOLD, a))
        p.text(540, 154, txt, "InterDisplay-Black", int(96 * sc), rgba(WHITE, a))
        ka = appear(t, t_2700 + 0.4)
        if ka > 0: p.text(540, 260, "athlètes", "Inter-Bold", 46, rgba(WHITE, ka))
    for i in range(9):
        sc, a = pop(t, t_equipes - 0.25 + i * 0.05)
        if a > 0: person(p, 220 + i * 80, 420, 1.0 * sc, rgba(WHITE if i % 3 else GOLD, a))

def card_petites(p, t):
    a0 = FULLS_D["l2"][1]
    glass(p, 540, 85, 820, 84, t, a0, "Petites et moyennes entreprises", 42, font_="InterDisplay-Black")
    for i, (x, s) in enumerate([(330, 0.7), (540, 1.0), (750, 0.85)]):
        t0 = (t_petites if i == 0 else t_moyennes) - 0.1 + i * 0.12
        sc, a = pop(t, t0)
        if a > 0: shop(p, x, 300, s * sc, a)
    sc, a = pop(t, t_brille - 0.1)
    if a > 0:
        for i, x in enumerate((330, 540, 750)):
            dx, dy, z = orbit(t, 4, 3, 3.0, i / 3)
            star(p, x + 70 + dx, 205 + dy, 30 * sc * z, rgba((246, 196, 40), a), rot=t * 0.8)
        sticker(p, 540, 450, 420, 84, t, t_brille - 0.05, "ONT BRILLÉ", 48, fill=GOLD, fg=WHITE, icon=ic_star, font_="InterDisplay-Black")

def card_equipe(p, t):
    a0 = FULLS_D["l3"][1]
    glass(p, 540, 85, 760, 84, t, a0, "2018 → 2026 : 8 ans de travail", 42, font_="InterDisplay-Black")
    for i in range(7):
        sc, a = pop(t, t_travail - 0.2 + i * 0.06)
        if a > 0: person(p, 300 + i * 80, 285, 1.25 * sc, rgba(GOLD if i == 3 else WHITE, a))
    sticker(p, 540, 430, 620, 96, t, t_travail + 0.15, "UN SACRÉ TRAVAIL D'ÉQUIPE", 46, fill=GOLD, fg=WHITE, font_="InterDisplay-Black")

def card_top(p, t):
    a0 = FULLS_D["prep"][1]
    sc, a = pop(t, t_cetait + 0.05, 0.5)
    if a > 0:
        spot_glow(p, 540, 280, 220, a)
        sticker(p, 540, 280, 520, 150, t, t_cetait + 0.05, "AU TOP", 100, fill=GOLD, fg=WHITE, icon=ic_up, font_="InterDisplay-Black")

# ---------- dessins ----------
def shop(p, cx, cy, s, a=1.0):
    """petite boutique (entreprise) dessinée"""
    p.rbox(cx - 90 * s + 6, cy - 40 * s + 10, cx + 90 * s + 6, cy + 90 * s + 10, 10 * s, fill=rgba((0, 0, 0), 0.3 * a))
    p.rbox(cx - 90 * s, cy - 40 * s, cx + 90 * s, cy + 90 * s, 10 * s, fill=rgba(WHITE, a))
    for i in range(5):
        x0 = cx - 100 * s + i * 40 * s
        p.rbox(x0, cy - 80 * s, x0 + 40 * s, cy - 30 * s, 8 * s, fill=rgba(GOLD if i % 2 == 0 else WHITE, a))
    p.rbox(cx - 26 * s, cy + 10 * s, cx + 26 * s, cy + 90 * s, 6 * s, fill=rgba((60, 64, 76), a))
    p.rbox(cx - 76 * s, cy + 2 * s, cx - 40 * s, cy + 44 * s, 6 * s, fill=rgba((150, 200, 240), a))
    p.rbox(cx + 40 * s, cy + 2 * s, cx + 76 * s, cy + 44 * s, 6 * s, fill=rgba((150, 200, 240), a))

def gauge(p, cx, cy, r, k, a=1.0):
    """anneau qui se remplit jusqu'à k (0..1)"""
    p.arc(cx, cy, r, 0, 360, rgba((255, 255, 255), 0.18 * a), 34)
    if k > 0: p.arc(cx, cy, r, -90, -90 + 360 * k, rgba(GOLD, a), 34)

def ic_ball(p, x, y, s, a, fg):
    p.circle(x, y, 24 * s, outline=rgba(fg, a), width=5 * s)
    p.line([(x - 24 * s, y), (x + 24 * s, y)], rgba(fg, a), 4 * s); p.line([(x, y - 24 * s), (x, y + 24 * s)], rgba(fg, a), 4 * s)
def ic_music(p, x, y, s, a, fg):
    p.circle(x - 10 * s, y + 14 * s, 11 * s, fill=rgba(fg, a)); p.circle(x + 16 * s, y + 8 * s, 11 * s, fill=rgba(fg, a))
    p.line([(x - 1 * s, y + 14 * s), (x - 1 * s, y - 22 * s), (x + 25 * s, y - 28 * s), (x + 25 * s, y + 8 * s)], rgba(fg, a), 5 * s)
def ic_plane(p, x, y, s, a, fg):
    p.poly([(x - 26 * s, y + 4 * s), (x + 26 * s, y - 2 * s), (x + 26 * s, y + 6 * s), (x - 26 * s, y + 10 * s)], rgba(fg, a))
    p.poly([(x - 4 * s, y + 2 * s), (x + 10 * s, y - 24 * s), (x + 16 * s, y - 24 * s), (x + 8 * s, y + 2 * s)], rgba(fg, a))
    p.poly([(x - 4 * s, y + 8 * s), (x + 10 * s, y + 28 * s), (x + 16 * s, y + 28 * s), (x + 8 * s, y + 8 * s)], rgba(fg, a))
    p.poly([(x - 26 * s, y + 4 * s), (x - 30 * s, y - 12 * s), (x - 22 * s, y - 12 * s), (x - 16 * s, y + 4 * s)], rgba(fg, a))
def ic_gear(p, x, y, s, a, fg):
    for i in range(8):
        an = i * math.pi / 4
        p.line([(x + 18 * s * math.cos(an), y + 18 * s * math.sin(an)), (x + 28 * s * math.cos(an), y + 28 * s * math.sin(an))], rgba(fg, a), 9 * s)
    p.circle(x, y, 19 * s, outline=rgba(fg, a), width=8 * s)
def ic_heart2(p, x, y, s, a, fg):
    p.circle(x - 11 * s, y - 8 * s, 14 * s, fill=rgba(fg, a)); p.circle(x + 11 * s, y - 8 * s, 14 * s, fill=rgba(fg, a))
    p.poly([(x - 24 * s, y - 2 * s), (x + 24 * s, y - 2 * s), (x, y + 24 * s)], rgba(fg, a))

# ---------- écrans plein écran (vidéo floutée derrière) ----------
def full_70(p, t):
    a0 = FULLS_D["70"][0]
    k0 = appear(t, a0 - 0.1)
    p.text(540, 230 + (1 - k0) * 20, "LES MARCHÉS DES JOJ", "InterDisplay-Black", 70, rgba(WHITE, k0))
    k = ease_io((t - t_70 + 0.1) / 0.9)
    sc, a = pop(t, t_70 - 0.2)
    if a > 0:
        spot_glow(p, 540, 640, 300, a)
        gauge(p, 540, 640, 230 * sc, 0.7 * k, a)
        p.text(540, 650, f"{int(round(70 * k))} %", "InterDisplay-Black", int(150 * sc), rgba(WHITE, a))
    ka = appear(t, t_marches)
    if ka > 0: p.text(540, 950 + (1 - ka) * 20, "confiés à des", "Inter-Bold", 50, rgba(GREY, ka))
    highlight(p, 540, 1060, "ENTREPRISES SÉNÉGALAISES", 66, t, t_senega - 0.3)
    if t > t_senega:   # drapeau du Sénégal : vert, jaune, rouge, étoile verte au centre
        sc, a = pop(t, t_senega)
        if a > 0:
            fw, fh = 270 * sc, 180 * sc; x0, y0 = 540 - fw / 2, 1250 - fh / 2
            p.rbox(x0 + 6, y0 + 10, x0 + fw + 6, y0 + fh + 10, 10 * sc, fill=rgba((0, 0, 0), 0.35 * a))
            p.rbox(x0, y0, x0 + fw, y0 + fh, 10 * sc, fill=rgba((253, 239, 66), a))
            p.rbox(x0, y0, x0 + fw / 3, y0 + fh, 10 * sc, fill=rgba((0, 133, 63), a))
            p.rbox(x0 + fw * 2 / 3, y0, x0 + fw, y0 + fh, 10 * sc, fill=rgba((227, 27, 35), a))
            p.rbox(x0 + fw / 3 - 12 * sc, y0, x0 + fw / 3, y0 + fh, 0, fill=rgba((253, 239, 66), a))
            p.rbox(x0 + fw * 2 / 3, y0, x0 + fw * 2 / 3 + 12 * sc, y0 + fh, 0, fill=rgba((253, 239, 66), a))
            p.rbox(x0 + fw / 3 - 14 * sc, y0, x0 + fw / 3 + 1, y0 + fh, 0, fill=rgba((0, 133, 63), a))
            p.rbox(x0 + fw * 2 / 3 - 1, y0, x0 + fw * 2 / 3 + 14 * sc, y0 + fh, 0, fill=rgba((227, 27, 35), a))
            star(p, 540, 1250, 40 * sc, rgba((0, 133, 63), a))

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

def full_secteurs(p, t):
    a0 = FULLS_D["secteurs"][0]
    k0 = appear(t, a0 - 0.1)
    p.text(540, 210 + (1 - k0) * 20, "ET SANS COMPTER…", "InterDisplay-Black", 76, rgba(WHITE, k0))
    items = [("2 700 athlètes", ic_ball, a0 + 0.15), ("Leurs équipes", ic_people, a0 + 0.35),
             ("Les artistes", ic_music, t_artist - 0.1), ("Les touristes", ic_plane, t_tour - 0.1)]
    for i, (txt, ic, t0) in enumerate(items):
        sticker(p, 540, 420 + i * 160, 680, 120, t, t0, txt, 52, fill=GOLD if i >= 2 else WHITE, fg=WHITE if i >= 2 else INK, icon=ic, font_="InterDisplay-Black")
    ka = appear(t, t_tour + 0.5)
    if ka > 0: p.text(540, 1100 + (1 - ka) * 20, "= des milliers de clients", "Inter-Bold", 52, rgba(WHITE, ka))

def full_prep(p, t):
    a0 = FULLS_D["prep"][0]
    k0 = appear(t, a0 - 0.1)
    p.text(540, 200 + (1 - k0) * 20, "DU DÉBUT JUSQU'À LA FIN", "InterDisplay-Black", 68, rgba(WHITE, k0))
    for i, (txt, ic, t0) in enumerate([("Artistique", ic_music, t_artist2 - 0.15), ("Organisation", ic_gear, t_orga - 0.15), ("Financement", ic_franc, t_finan - 0.15)]):
        sticker(p, 540, 400 + i * 160, 620, 120, t, t0, txt, 56, fill=WHITE, fg=INK, icon=ic, font_="InterDisplay-Black")
    sc, a = pop(t, t_sacr - 0.2)
    if a > 0:
        spot_glow(p, 540, 1000, 200, a)
        sticker(p, 540, 1010, 760, 130, t, t_sacr - 0.2, "D'ÉNORMES SACRIFICES", 62, fill=GOLD, fg=WHITE, icon=ic_heart2, font_="InterDisplay-Black")

def full_end(p, t):
    b = END0
    k = appear(t, b)
    p.text(540, 160 + (1 - k) * 20, "LES JOJ, UNE LEÇON BUSINESS", "InterDisplay-Black", 60, rgba(WHITE, k))
    highlight(p, 540, 265, "CE QU'IL FAUT RETENIR", 52, t, b + 0.15)
    for i, (txt, ic) in enumerate([("Du monde = des clients", ic_people),
                                   ("Une petite boîte peut briller", ic_star),
                                   ("Le succès = des années de travail", ic_cal)]):
        t0 = b + 0.45 + i * 0.25
        sc, kk = pop(t, t0, 0.35)
        if kk <= 0: continue
        y = 450 + i * 150
        p.circle(95, y, 50 * sc, fill=rgba(GOLD, kk)); p.text(95, y + 2, str(i + 1), "InterDisplay-Black", int(56 * sc), rgba(WHITE, kk))
        sticker(p, 590, y, 880, 118, t, t0 + 0.05, txt, 44, icon=ic, font_="InterDisplay-Black")
    sticker(p, 540, 960, 900, 120, t, b + 1.4, "Tu as été fier des JOJ ?", 46, fill=GOLD, fg=WHITE, icon=ic_comment)
    k = appear(t, b + 1.6)
    if k > 0: p.text(540, 1080 + (1 - k) * 20, "Dis-le en commentaire", "Inter-Bold", 42, rgba(GREY, k))

# ---------- programme ----------
PRE = 0.26
FULLS = []
FULLS_D = {}
def add_full(name, a, b, fn, opaque=False):
    FULLS.append((a, b, fn, opaque)); FULLS_D[name] = (a, b)
END0 = END_SPEECH + 0.3
add_full("70", cut_near(t_cequil - 0.1), t_etla - 0.05, full_70)                                   # cache le 1er essai « 70 % »
add_full("l1", t_etla - 0.05, t_plus - 0.12, full_lever(1, "l1", "LÀ OÙ IL Y A DU MONDE", "il y a des clients"))
add_full("secteurs", cut_near(t_sans - 0.1), cut_near(t_lune - 0.1) - 0.0, full_secteurs)          # cache la coupe après « équipes »
add_full("l2", cut_near(t_lune - 0.1), t_quil - 0.08, full_lever(2, "l2", "UNE PETITE BOÎTE PEUT BRILLER", "pas besoin d'être une multinationale"))
add_full("l3", cut_near(t_retenir - 0.4), t_derriere - 0.1, full_lever(3, "l3", "DES ANNÉES DE PRÉPARATION", "et un sacré travail d'équipe"))
add_full("prep", cut_near(t_artist2 - 0.1), cut_near(t_cetait - 0.1), full_prep)                  # cache 2 coupes
add_full("end", END0, TOTAL + 1, full_end, True)
FULLS.sort(key=lambda f: f[0])
assert FULLS[-1][2] is full_end
# l2 démarre à la même coupe que la fin de « secteurs » : on les enchaîne sans revenir sur lui
FULLS = [(a, b, fn, o) for a, b, fn, o in FULLS]

OPAQUE = [(0.0, INTRO_END, intro_screen, 0.0, 0.25), (MODU_A, MODU_B, modu_screen, 0.3, 0.25), (END0 - 0.1, TOTAL + 1, end_bg, 0.4, 0.0)]

CARDS = [
    (INTRO_END, FULLS_D["70"][0], card_business),
    (FULLS_D["l1"][1], FULLS_D["secteurs"][0], card_2700),
    (FULLS_D["l2"][1], MODU_A, card_petites),
    (FULLS_D["l3"][1], FULLS_D["prep"][0], card_equipe),
    (FULLS_D["prep"][1], FULLS_D["end"][0], card_top),
]
CARD_BATH = 0.0

PUNCHES = [t_70, t_clients, t_top]
def punch(t):
    k = 0.0
    for p0 in PUNCHES:
        if p0 <= t < p0 + 0.45: k = max(k, math.exp(-(t - p0) * 9))
    return 1 + 0.07 * k
def flash(t):
    return max([0.0] + [0.45 * math.exp(-(t - p0) * 14) for p0 in PUNCHES if p0 <= t < p0 + 0.3])

def pin(p, cx, cy, s, a=1.0, col=None):
    col = col or RED
    p.poly([(cx - 26 * s, cy - 30 * s), (cx + 26 * s, cy - 30 * s), (cx, cy + 20 * s)], rgba(col, a))
    p.circle(cx, cy - 40 * s, 30 * s, fill=rgba(col, a)); p.circle(cx, cy - 40 * s, 12 * s, fill=rgba(WHITE, a))
def ic_pin(p, x, y, s, a, fg):
    pin(p, x, y + 14 * s, 0.6 * s, a, fg)
def ic_franc(p, x, y, s, a, fg):
    p.circle(x, y, 25 * s, outline=rgba(fg, a), width=5 * s)
    p.text(x, y + 1 * s, "F", "InterDisplay-Black", 30 * s, rgba(fg, a))
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

