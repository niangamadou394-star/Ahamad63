# « JOJ Dakar 2026 » : IMG_2657.mov (188 s, 1080p HLG vertical, 1er novembre).
# Il n'a pas suivi le script mot pour mot : on garde ses phrases. Retirés : le 1er essai « 70 % des marchés »,
# les reprises « plus de 2 700 athlètes / et sans compter les autres secteurs », « Donc aujourd'hui quand tu regardes » (il se lève),
# le faux départ « début centi… 53 », la 2e « ça me fait penser à Moduvated », « Donc aujourd'hui toute entreprise »,
# les 3 premières versions de la fin, « tout a été », la 4e version de la fin sauf « d'énormes sacrifices » et « c'était surtout au top ».
import os
FPS = 30.0
RUSH = {"A": "/mnt/project-files/IMG_2657.mov"}
CROP = {"A": (0, 200)}
SRC = os.environ.get("JOJ_SRC") or "/tmp/claude-0/-home-user-Ahamad63/82063c25-e035-5c7f-982a-4daa61791572/scratchpad/joj/joj-src.mkv"
MARGIN = 0.20

def to_pts(t):
    return t

SEGMENTS = [
 ("A", [(4.28, 11.96, "Hier, tout Sénégalais ou Africain tout court a ressenti un énorme sentiment de *fierté,* parce qu'on a tout simplement été *honorés.*"),
        (12.57, 13.29, "On a *accueilli,*"),
        (13.69, 14.45, "on a *célébré,*"),
        (14.77, 15.98, "on a raconté notre *histoire*"),
        (16.24, 18.30, "et on a surtout représenté l'*Afrique*"),
        (18.57, 19.45, "devant les yeux du *monde.*")]),
 ("A", [(21.47, 25.24, "Mais comme d'habitude, nous, on va pas seulement se limiter au niveau des événements,"),
        (25.50, 28.24, "mais on va parler surtout du côté *entrepreneuriat.*"),
        (28.51, 30.55, "Qu'est-ce que ça représente exactement ?")]),
 ("A", [(35.68, 40.24, "Ce qu'il faut savoir, c'est que *70* *%* des marchés ont été confiés à des entreprises"),
        (40.51, 41.03, "*sénégalaises.*"),
        (41.71, 44.41, "Et là, quand on voit du *monde,* on voit forcément des *clients.*"),
        (44.67, 46.89, "Plus de *2700* athlètes avec leurs équipes,")]),
 ("A", [(70.04, 71.42, "et sans compter les autres secteurs,"),
        (71.71, 72.58, "le domaine *artistique*"),
        (72.84, 74.98, "et le nombre de *touristes* qu'on a pu accueillir.")]),
 ("A", [(101.47, 105.21, "Et l'une des leçons qu'on peut aussi en tirer également, c'est le fait"),
        (105.47, 108.46, "qu'il y a eu des *petites* *entreprises,* ou bien même des entreprises moyennes, qui ont *brillé.*"),
        (108.90, 110.92, "Et là, ça me fait penser à *Moduvated.*")]),
 ("A", [(115.43, 118.30, "Ce n'est pas une grosse *multinationale,* mais elle a pu se *démarquer.*")]),
 ("A", [(153.16, 157.00, "Et ce qu'on peut surtout retenir, c'est le nombre d'*années* de *préparation,*"),
        (157.41, 158.86, "derrière, un sacré *travail* *d'équipe,*"),
        (159.42, 160.66, "du début jusqu'à la fin,")]),
 ("A", [(165.49, 166.42, "au niveau *artistique,*"),
        (166.81, 167.60, "*organisation,*"),
        (167.97, 168.63, "du *financement.*")]),
 ("A", [(178.66, 179.56, "D'énormes *sacrifices.*")]),
 ("A", [(183.34, 184.68, "C'était surtout *au* *top.*")]),
]
HEAD = {0: 0.0}
TAIL = {9: 0.25}

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
CUT_GAP = 0.37
SHORT, LONG = 0.18, 0.28

def spans():
    out = [[ISLANDS[0][0] - 0.0, None]]   # premier mot dès l'image 0
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
