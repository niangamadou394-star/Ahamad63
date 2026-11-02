# « Kirène avec Orange » : IMG_2669.mov (143 s, 1080p HLG vertical, 2 novembre). Montage plus rythmé (demande d'Amadou).
# Retirés : le faux départ « En 2009, la marque Ki… », les 5 premières prises de « Le principe est simple »,
# les autres « 15 ans plus tard » (dont « presque plus de 4 millions d'utilisateurs », chiffre non vérifié),
# les faux départs de « Deuxièmement », « Donc toi aujourd'hui / Donc si tu penses », le 1er « prends le temps ».
import os
FPS = 30.0
RUSH = {"A": "/mnt/project-files/IMG_2669.mov"}
CROP = {"A": (0, 200)}
SRC = os.environ.get("KIRENE_SRC") or "/tmp/claude-0/-home-user-Ahamad63/82063c25-e035-5c7f-982a-4daa61791572/scratchpad/kirene/kirene-src.mkv"
MARGIN = 0.16

def to_pts(t):
    return t

SEGMENTS = [
 ("A", [(8.07, 13.27, "En *2009,* le groupe *Kirène,* que nous connaissons tous, qui vendait de l'*eau,* a décidé de vendre des *puces*"),
        (13.82, 14.83, "*Kirène* *avec* *Orange.*")]),
 ("A", [(38.63, 43.36, "Le principe est simple : acheter des *minutes* chez *Orange* et les *revendre* à ses utilisateurs."),
        (43.78, 46.11, "*15* *ans* plus tard, la puce est toujours *là.*")]),
 ("A", [(62.45, 65.71, "Et là, on va encore une fois en tirer *deux* *leçons* majeures."),
        (66.17, 69.20, "D'abord, le fait de vendre sa *marque* plutôt que son *produit.*"),
        (69.62, 72.35, "Aujourd'hui, ta marque vaut plus que ton produit."),
        (72.72, 75.87, "Si t'arrives à créer une marque que tout le monde *aime,* que tes utilisateurs aiment,"),
        (76.43, 79.65, "peu importe la qualité de ton produit, ils vont quand même finir par *acheter.*")]),
 ("A", [(107.65, 110.27, "Deuxièmement, t'as pas besoin de créer quelque chose de *nouveau.*"),
        (110.61, 115.50, "Parfois, il suffit juste d'être *stratégique,* comme l'avait fait Kirène, c'est-à-dire de créer un *partenariat*"),
        (115.83, 118.50, "où tu vas *revendre* un produit déjà existant.")]),
 ("A", [(125.08, 130.13, "Donc, si tu as le choix aujourd'hui à te créer un *nouveau* *produit* ou à *revendre* un autre déjà existant,")]),
 ("A", [(133.70, 138.41, "prends le temps de réfléchir, et vois exactement si le fait de revendre un produit déjà existant"),
        (138.66, 140.10, "n'est pas plus *stratégique.*")]),
]
HEAD = {0: 1.30}   # le jingle « Kirène avec Orange » passe pendant cette pause (cachée sous l'écran d'ouverture)
TAIL = {5: 0.3}

def _r(t):
    return round(t * FPS) / FPS

CUTS_SRC = []
_acc = 0.0
for i, (k, isl) in enumerate(SEGMENTS):
    a = _r(isl[0][0] - HEAD.get(i, MARGIN))
    b = _r(isl[-1][1] + TAIL.get(i, MARGIN))
    CUTS_SRC.append((k, a, b, _acc))
    _acc += b - a
SRC_LEN = _acc

def comb(seg, t):
    """temps du rush (dans le segment seg) -> temps du fichier combiné"""
    k, a, b, off = CUTS_SRC[seg]
    return off + t - a

def seg_at(tc):
    for i, (k, a, b, off) in enumerate(CUTS_SRC):
        if tc < off + (b - a): return i
    return len(CUTS_SRC) - 1

ISLANDS = [(comb(i, s), comb(i, e), txt) for i, (k, isl) in enumerate(SEGMENTS) for s, e, txt in isl]
ISEG = [i for i, (k, isl) in enumerate(SEGMENTS) for _ in isl]
JINGLE = 1.15
CUT_GAP = 0.30
SHORT, LONG = 0.12, 0.20   # plus rythmé que d'habitude

def spans():
    out = [[ISLANDS[0][0] - JINGLE, None]]   # jingle seul, puis premier mot
    for j, ((s0, e0, t0), (s1, e1, t1)) in enumerate(zip(ISLANDS, ISLANDS[1:])):
        gap = s1 - e0
        if gap < CUT_GAP and ISEG[j] == ISEG[j + 1]:   # une jonction de segments est toujours une coupe
            continue
        want = LONG if t0.rstrip()[-1] in ".?" else SHORT
        out[-1][1] = e0 + min(want / 2, TAIL.get(ISEG[j], 1) if ISEG[j] != ISEG[j + 1] else 1)
        out.append([s1 - min(want / 2, HEAD.get(ISEG[j + 1], 1) if ISEG[j] != ISEG[j + 1] else 1), None])
    out[-1][1] = ISLANDS[-1][1] + 0.12
    return [(round(s * FPS) / FPS, round(e * FPS) / FPS) for s, e in out]

# en temps combiné, pour placer les animations : S(seg, t_rush)
def S(seg, t):
    return comb(seg, t)

if __name__ == "__main__":
    for c in CUTS_SRC: print(c)
    sp = spans(); print(len(sp), "plans", round(sum(e - s for s, e in sp), 2), "s ; SRC", round(SRC_LEN, 2), "s")
