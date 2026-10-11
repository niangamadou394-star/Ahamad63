# Découpage du rush « Vidéo du jour - vertical.mp4 » : plages de parole gardées (temps source),
# choisies parmi ses prises ; pauses raccourcies, reprises et hésitations retirées.
FPS = 60.0
SRC = "/mnt/project-files/Vidéo du jour - vertical.mp4"
# (début, fin, texte) ; *mot* = mot-clé en or
ISLANDS = [
    (18.71, 22.32, "Tu ne vas jamais réussir ton projet sans valider les *5* *étapes* suivantes."),
    (22.71, 24.30, "Premièrement, *clarifie* le *besoin.*"),
    (24.60, 29.16, "C'est-à-dire, qu'est-ce que tu veux faire *exactement* ? Tu dois être capable de *pitcher* ton projet en moins d'une *minute.*"),
    (29.51, 30.64, "Expliquer le *problème,*"),
    (30.88, 31.48, "le *besoin,*"),
    (31.75, 32.87, "la *solution* que tu apportes"),
    (33.16, 33.60, "ainsi"),
    (33.82, 35.29, "que la *valeur* *ajoutée* que tu apportes."),
    (35.98, 36.60, "Deuxièmement,"),
    (37.08, 38.29, "il faut *valider* le *besoin.*"),
    (48.00, 52.10, "Quand on dit valider le besoin, il faut aller faire *l'étude* *de* *marché.* On en avait parlé précédemment."),
    (53.62, 55.56, "Il faut aller rencontrer des *futurs* *utilisateurs,*"),
    (55.82, 57.85, "rencontrer tes futurs *clients,* c'est ça qui va te permettre"),
    (58.06, 59.39, "de réellement *valider* le besoin."),
    (96.62, 99.46, "Troisièmement, avoir des objectifs *chiffrés.*"),
    (99.78, 102.29, "Pas des objectifs je veux atteindre telle chose ou telle chose, non."),
    (102.47, 103.40, "À telle date,"),
    (103.67, 105.05, "je veux avoir atteint tel *chiffre.*"),
    (105.34, 107.27, "C'est ça qui va te permettre de savoir exactement"),
    (107.59, 109.19, "*l'évolution* de ton projet."),
    (109.47, 110.73, "Chaque étape que tu vas valider,"),
    (111.00, 113.17, "ça va rentrer dans ces *objectifs* que tu vas atteindre."),
    (151.16, 153.30, "Quatrièmement, rencontrer les *bonnes* *personnes.*"),
    (153.56, 159.20, "C'est le fait de rencontrer ces bonnes personnes qui vont te permettre de valider l'étape 5, qui est de rencontrer des *investisseurs.*"),
    (159.52, 162.47, "Parce que sans ces investisseurs, tu risques de jamais *scaler* ton projet."),
    (162.82, 164.89, "Tu risques de jamais atteindre un certain *niveau,*"),
    (165.20, 167.06, "vu que tu as besoin forcément *d'argent*"),
    (167.40, 167.99, "pour pouvoir"),
    (168.73, 169.20, "développer,"),
    (170.31, 171.36, "*grandir* le projet."),
]
SHORT, LONG = 0.16, 0.28   # pause gardée dans une phrase / après un point
PAD = 0.07                  # marge de part et d'autre d'une plage (souffle de fin de mot)

def spans():
    out = []
    for i, (s, e, txt) in enumerate(ISLANDS):
        prev = ISLANDS[i - 1] if i else None
        nxt = ISLANDS[i + 1] if i + 1 < len(ISLANDS) else None
        # pause gardée après cette plage : si la suivante suit dans la même prise, on garde une partie du silence
        def keep(gap, end_txt):
            want = LONG if end_txt.rstrip()[-1] in ".?" else SHORT
            return min(gap, want)
        if prev and 0 <= s - prev[1] < 1.2:
            pre = keep(s - prev[1], prev[2]) / 2
        else:
            pre = PAD
        if nxt and 0 <= nxt[0] - e < 1.2:
            post = keep(nxt[0] - e, txt) / 2
        else:
            post = PAD if nxt else 0.25
        # entre deux prises, la pause vient du rush de chaque côté
        if nxt and not (0 <= nxt[0] - e < 1.2):
            post = keep(0.6, txt) / 2
        if prev and not (0 <= s - prev[1] < 1.2):
            pre = keep(0.6, prev[2]) / 2
        out.append([s - pre, e + post])
    m = []
    for s, e in out:
        s, e = round(s * FPS) / FPS, round(e * FPS) / FPS
        if m and s - m[-1][1] < 0.5 / FPS: m[-1][1] = e
        else: m.append([s, e])
    return [tuple(x) for x in m]

if __name__ == "__main__":
    sp = spans(); print(len(sp), "plans", round(sum(e - s for s, e in sp), 2), "s")
    for s, e in sp: print(f"{s:7.2f} {e:7.2f}")
