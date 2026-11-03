# « Jumia » : IMG_2704.mov (133 s, 1080p HLG vertical, 3 novembre). Nouvelles règles : ~40 s, accroche choc, gros titre au centre.
# Ordre changé : on ouvre sur « Ils ont perdu près d'un milliard de dollars » (2e prise), puis la présentation.
# Mot « africaine » retiré à sa demande (16,94-17,58 s du rush, coupe dans la phrase cachée sous un plein écran).
# Retirés : la 1re prise des pertes, « Et là vous allez me dire… dans le monde », le 1er « De 2012 », le passage Wari,
# « le fait qu'une entreprise soit présente… » (redit à la fin), les faux départs de « Donc aujourd'hui », « Pense à ceci ».
import os
FPS = 30.0
RUSH = {"A": "/mnt/project-files/IMG_2704.mov"}
CROP = {"A": (0, 200)}
SRC = os.environ.get("JUMIA_SRC") or "/tmp/claude-0/-home-user-Ahamad63/82063c25-e035-5c7f-982a-4daa61791572/scratchpad/jumia/jumia-src.mkv"
MARGIN = 0.16

def to_pts(t):
    return t

SEGMENTS = [
 ("A", [(31.46, 34.06, "Ils ont perdu près d'*un* *milliard* de *dollars.*")]),
 ("A", [(11.96, 16.92, "Jumia, l'*Amazon* de l'Afrique, présent également au *Sénégal,* est la première entreprise")]),
 ("A", [(17.58, 20.37, "à faire son entrée à *Wall* *Street* en *2019.*")]),
 ("A", [(41.15, 42.87, "Comment ça se fait qu'ils ne sont pas *rentables* ?")]),
 ("A", [(46.42, 49.92, "De *2012* jusqu'à maintenant, *aucune* année *rentable.*")]),
 ("A", [(92.77, 96.86, "Donc aujourd'hui, lors de la création de ton entreprise ou bien même le lancement de ta *start-up,*")]),
 ("A", [(109.74, 113.54, "il ne faut surtout pas penser à vouloir s'installer un peu *partout*"),
        (113.84, 119.23, "en Afrique sans autant *conquérir* là où tu es, c'est-à-dire devenir *rentable* exactement.")]),
 ("A", [(123.70, 130.55, "Encore une fois, le fait de *lever* des *fonds* ou bien même vendre un peu partout ne veut pas dire devenir *rentable.*")]),
]
HEAD = {2: 0.0}
TAIL = {1: 0.0, 7: 0.25}

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
CUT_GAP = 0.30
SHORT, LONG = 0.12, 0.20   # plus rythmé que d'habitude

def spans():
    out = [[ISLANDS[0][0] - 0.0, None]]   # premier mot dès l'image 0
    for j, ((s0, e0, t0), (s1, e1, t1)) in enumerate(zip(ISLANDS, ISLANDS[1:])):
        gap = s1 - e0
        if gap < CUT_GAP and ISEG[j] == ISEG[j + 1]:   # une jonction de segments est toujours une coupe
            continue
        want = LONG if t0.rstrip()[-1] in ".?" else SHORT
        out[-1][1] = e0 + min(want / 2, TAIL.get(ISEG[j], 1) if ISEG[j] != ISEG[j + 1] else 1)
        lead = min(want / 2, HEAD.get(ISEG[j + 1], 1) if ISEG[j] != ISEG[j + 1] else 1)
        out.append([s1 - lead, None])
    out[-1][1] = ISLANDS[-1][1] + 0.12
    return [(round(s * FPS) / FPS, round(e * FPS) / FPS) for s, e in out]

# en temps combiné, pour placer les animations : S(seg, t_rush)
def S(seg, t):
    return comb(seg, t)

if __name__ == "__main__":
    for c in CUTS_SRC: print(c)
    sp = spans(); print(len(sp), "plans", round(sum(e - s for s, e in sp), 2), "s ; SRC", round(SRC_LEN, 2), "s")
