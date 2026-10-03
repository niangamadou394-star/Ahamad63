# De l’idée au lancement — carrousels LinkedIn (10 posts)

10 carrousels au format **PDF 1080 × 1350 (portrait 4:5)**, le format qui occupe le plus d’espace dans le fil LinkedIn. Chaque épisode a sa couleur signature, ce qui rend la série reconnaissable d’un post à l’autre.

| # | Carrousel | Couleur | Fichier |
|---|-----------|---------|---------|
| 01 | L’idée | Corail | `exports/carrousel-01-idee.pdf` |
| 02 | Valider le problème | Bleu électrique | `exports/carrousel-02-valider.pdf` |
| 03 | La cible | Violet | `exports/carrousel-03-cible.pdf` |
| 04 | L’offre | Orange | `exports/carrousel-04-offre.pdf` |
| 05 | Les chiffres | Émeraude | `exports/carrousel-05-chiffres.pdf` |
| 06 | Le MVP | Rose | `exports/carrousel-06-mvp.pdf` |
| 07 | Statut & financement | Bleu canard | `exports/carrousel-07-statut-financement.pdf` |
| 08 | La marque | Indigo | `exports/carrousel-08-marque.pdf` |
| 09 | Le pré-lancement | Jaune soleil | `exports/carrousel-09-pre-lancement.pdf` |
| 10 | Le lancement | Dégradé rose → violet | `exports/carrousel-10-lancement.pdf` |

Chaque slide existe aussi en PNG, dans `exports/png/`. Elles servent pour les aperçus, ou pour un post en images multiples.

## Publier un carrousel sur LinkedIn

1. Clique sur **Commencer un post**, puis sur **+ → Ajouter un document**.
2. Importe le PDF et donne-lui un titre court, par exemple « Ton idée ne vaut rien… (étape 1/10) ».
3. Colle le texte du post ci-dessous et publie.

Bonnes pratiques :
- **Rythme** : 2 posts par semaine (mardi et jeudi, entre 8 h et 10 h).
- **Après publication** : réponds à chaque commentaire dans la première heure.
- **Premier commentaire** : poste-le toi-même, avec le lien vers l’épisode précédent.

---

## Textes des posts

**01 — L’idée**
> Ton idée ne vaut rien.
> (Enfin… tant qu’elle ne résout pas un vrai problème.)
>
> Avant de te lancer, fais-lui passer 3 filtres :
> → un problème réel
> → ta légitimité
> → une envie qui tiendra 3 ans
>
> Puis écris-la en une phrase. Le modèle est dans le carrousel 👇
>
> C’est l’étape 1/10 de la série « De l’idée au lancement ».
> #entrepreneuriat #creationdentreprise #porteurdeprojet

**02 — Valider le problème**
> Ta mère adore ton idée ? Ça ne compte pas.
>
> Parmi les startups qui échouent, 35 % citent l’absence de besoin sur le marché (CB Insights).
> La parade : 10 conversations avant d’écrire une seule ligne de code.
>
> La question qui change tout est en slide 4.
> Étape 2/10 👇
> #validation #startup #entrepreneuriat

**03 — La cible**
> Si tu parles à tout le monde, personne ne t’écoute.
>
> J’ai mis dans ce carrousel l’exercice de l’entonnoir et les 4 traits de ton client idéal.
> Une niche n’est pas une prison : c’est une porte d’entrée.
>
> Étape 3/10 👇
> #marketing #persona #entrepreneuriat

**04 — L’offre**
> Personne n’achète ton produit.
> On achète le résultat qu’il promet.
>
> « 10 séances de coaching » ou « récupère 5 h par semaine en 30 jours » : même service, autre impact.
> Les 4 ingrédients d’une offre qui se vend seule 👇
>
> Étape 4/10
> #vente #offre #entrepreneuriat

**05 — Les chiffres**
> Ton projet est rentable ? Prouve-le en 3 chiffres.
>
> Le calcul du seuil de rentabilité tient en une ligne : charges fixes ÷ marge par vente.
> Exemple : 1 500 € ÷ 50 € = 30 ventes par mois.
>
> Enregistre ce post pour faire ton calcul. Étape 5/10 👇
> #businessplan #rentabilite #entrepreneuriat

**06 — Le MVP**
> Ce qui est parfait n’est jamais lancé.
>
> Voici 4 MVP à tester cette semaine, sans coder et sans stock.
> Un seul objectif : 3 premiers clients payants. Pas des likes.
>
> Étape 6/10 👇
> #mvp #startup #entrepreneuriat

**07 — Statut & financement**
> Micro, EURL, SASU… tu bloques ?
>
> Ce carrousel résume les 3 statuts les plus courants et les pistes pour financer ton projet sans tout sortir de ta poche.
> ⚠️ Ce sont des infos générales : vérifie toujours ta situation (URSSAF, Bpifrance Création, CCI ou CMA).
>
> Étape 7/10 👇
> #statutjuridique #financement #creationdentreprise

**08 — La marque**
> Un beau logo ne sauve pas une offre bancale.
> Mais une marque claire fait vendre une bonne offre.
>
> Voici le kit minimum pour exister, et la règle qui bat toutes les autres : la régularité.
> Étape 8/10 👇
> #branding #personalbranding #entrepreneuriat

**09 — Le pré-lancement**
> On ne lance pas dans le vide.
>
> Ton rétroplanning de J-30 à J-1 est dans ce carrousel.
> Le jour J, tu ne cherches pas des clients : tu préviens ceux qui attendent.
>
> Étape 9/10 👇
> #lancement #strategie #entrepreneuriat

**10 — Le lancement**
> Jour J. Ce n’est que le début.
>
> Tu y trouveras la check-list avant d’appuyer sur le bouton, puis la boucle qui fait grandir : mesurer, écouter, ajuster.
>
> Tu as un projet et tu veux être accompagné·e ?
> Commente « LANCEMENT » 👇
> #lancement #accompagnement #entrepreneuriat

---

## Modifier ou régénérer

Le contenu est partagé avec la série TikTok : `../tiktok/episodes.js`. Si tu modifies un texte, tu mets à jour les deux formats.

```bash
cd linkedin
node render.mjs        # régénère les 10 PDF et les PNG
node render.mjs 4      # seulement le carrousel 4
```

Pour voir un aperçu dans le navigateur, ouvre `carousel.html?ep=3`. Les couleurs de chaque épisode se règlent dans `THEMES`, dans `carousel.js`.
