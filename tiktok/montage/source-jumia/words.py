# Texte prononcé, rangé par plage de parole du rush (temps source). *mot* = mot-clé en or.
# Les mots sont répartis dans leur plage selon leur longueur.
from edl import spans, FPS, ISLANDS as _ISL, to_pts
ISLANDS = [x[:3] for x in _ISL]

SPANS = spans()
def src2edit(t, pts=False):
    """temps d'analyse (ou pts si pts=True) -> temps du montage"""
    if not pts: t = to_pts(t)
    acc = 0.0
    for s, e in SPANS:
        if t < s:
            return acc
        if t <= e:
            return acc + t - s
        acc += e - s
    return acc
TOTAL_SPEECH = sum(e - s for s, e in SPANS)

def words():
    out = []
    for a, b, txt in ISLANDS:
        ws = txt.split()
        wt = [len(w.strip("*,.?«»")) + 1.5 for w in ws if True]
        tot = sum(wt); t = a
        for w, k in zip(ws, wt):
            d = (b - a) * k / tot
            hl = w.startswith("*")
            out.append(dict(w=w.replace("*", ""), hl=hl, s=src2edit(t), e=src2edit(t + d), end_isl=(w is ws[-1])))
            t += d
    return out

def captions(maxc=20, maxw=4):
    """Groupes de 1 à 4 mots ; on coupe sur la ponctuation et entre les plages."""
    ws = words(); groups, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        n = len(" ".join(x["w"] for x in cur))
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        brk = w["w"][-1] in ",.?" or nxt is None or len(cur) >= maxw or \
              (nxt and n + 1 + len(nxt["w"]) > maxc) or (w["end_isl"] and nxt["s"] - w["e"] > 0.12)
        if brk:
            groups.append(dict(words=cur, s=cur[0]["s"], e=cur[-1]["e"])); cur = []
    for g, n in zip(groups, groups[1:]):
        if n["s"] - g["e"] < 0.45: g["e"] = n["s"]
        else: g["e"] += 0.25
    return groups

if __name__ == "__main__":
    for g in captions():
        print(f'{g["s"]:6.2f}-{g["e"]:6.2f}', " ".join(("*" + w["w"] + "*") if w["hl"] else w["w"] for w in g["words"]))
