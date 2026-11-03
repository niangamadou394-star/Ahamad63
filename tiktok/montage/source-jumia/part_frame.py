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

