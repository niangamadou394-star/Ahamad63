
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
