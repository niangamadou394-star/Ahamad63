/* ==========================================================================
   DE L'IDÉE AU LANCEMENT — 10 épisodes TikTok
   *texte* = mot mis en valeur (or, italique).  [texte] = case à remplir.
   ========================================================================== */
window.EPISODES = [
  // ------------------------------------------------------------------ 01
  {
    n: 1, slug: 'idee', accent: 'coral', title: 'L’idée',
    scenes: [
      { type: 'hook', kicker: 'Épisode 01', lines: ['Ton idée', 'ne vaut', '*rien.*'], sub: '…tant qu’elle ne résout pas un vrai problème.' },
      { type: 'chapter', title: 'L’idée', desc: 'Transformer une envie en hypothèse.', stage: 'Idée' },
      { type: 'text', lines: ['Une idée,', 'c’est une *hypothèse.*', 'Pas encore un projet.'] },
      { type: 'list', kicker: 'Le test des 3 filtres', title: 'Garde l’idée qui passe *les 3.*', items: [
        ['Un problème réel', 'Des gens le vivent vraiment, et souvent.'],
        ['Ta légitimité', 'Pourquoi toi ? Expérience, réseau, passion.'],
        ['Une envie durable', 'Tu te vois dessus dans 3 ans ?'],
      ] },
      { type: 'formula', kicker: 'Écris-la en une phrase', text: 'Pour [qui] qui [problème], je propose [solution].', note: 'Si tu n’arrives pas à la remplir, *l’idée n’est pas prête.*' },
      { type: 'cta', next: 'Valider ton idée *sans dépenser 1 €*', nextSub: 'La méthode des 10 conversations.' },
    ],
  },
  // ------------------------------------------------------------------ 02
  {
    n: 2, slug: 'valider', accent: 'teal', title: 'Valider le problème',
    scenes: [
      { type: 'hook', kicker: 'Épisode 02', lines: ['Ta mère adore', 'ton idée.', '*Ça ne compte pas.*'], sub: 'Valide avec ceux qui paieront.' },
      { type: 'chapter', title: 'Valider', desc: 'Prouver que le problème existe.', stage: 'Validation' },
      { type: 'stat', kicker: 'Le chiffre qui fait mal', value: 35, suffix: '%', ring: true, label: 'des startups qui échouent citent *l’absence de besoin* sur le marché.', source: 'Source : CB Insights · analyse de post-mortems' },
      { type: 'list', kicker: 'La méthode', title: '10 conversations *avant* 1 ligne de code.', items: [
        ['Parle à 10 personnes de ta cible', 'Pas tes proches. Des inconnus concernés.'],
        ['Parle de leur problème', 'Jamais de ton idée au début.'],
        ['Demande ce qu’ils font déjà', 'Leurs solutions actuelles = ta concurrence.'],
        ['Note leurs mots exacts', 'Ce seront tes futurs textes de vente.'],
      ] },
      { type: 'compare', kicker: 'La bonne question', bad: '« Tu achèterais mon appli ? »', good: '« Raconte-moi la *dernière fois* que ça t’est arrivé. »' },
      { type: 'text', lines: ['S’ils bricolent déjà', 'une solution…', '*c’est bon signe.*'] },
      { type: 'cta', next: 'Trouver *ton client idéal*', nextSub: 'Pourquoi « tout le monde » n’est pas une cible.' },
    ],
  },
  // ------------------------------------------------------------------ 03
  {
    n: 3, slug: 'cible', accent: 'purple', title: 'Ta cible',
    scenes: [
      { type: 'hook', kicker: 'Épisode 03', lines: ['Si tu parles', 'à *tout le monde,*', 'personne', 'ne t’écoute.'] },
      { type: 'chapter', title: 'La cible', desc: 'Choisir pour qui tu existes.', stage: 'Cible' },
      { type: 'zoom', kicker: 'Resserre. Encore.', levels: [
        'Tout le monde',
        'Les entrepreneurs',
        'Les artisans qui se lancent',
        'Les artisans de Clermont qui ouvrent *leur 1re boutique*',
      ] },
      { type: 'list', kicker: 'Ton client idéal', title: 'Dessine-le en *4 traits.*', items: [
        ['Qui il est', 'Âge, métier, situation, contraintes.'],
        ['Ce qui l’empêche de dormir', 'Son problème n°1, avec ses mots.'],
        ['Où il passe son temps', 'Réseaux, lieux, médias, communautés.'],
        ['Ce qu’il paie déjà', 'Son budget et ses habitudes d’achat.'],
      ] },
      { type: 'text', lines: ['Plus c’est précis,', '*plus ça vend.*'], small: 'Une niche n’est pas une prison : c’est une porte d’entrée.' },
      { type: 'cta', next: 'Construire *une offre irrésistible*', nextSub: 'Vendre un résultat, pas un produit.' },
    ],
  },
  // ------------------------------------------------------------------ 04
  {
    n: 4, slug: 'offre', accent: 'coral', title: 'L’offre',
    scenes: [
      { type: 'hook', kicker: 'Épisode 04', lines: ['Personne', 'n’achète', '*ton produit.*'], sub: 'On achète le résultat qu’il promet.' },
      { type: 'chapter', title: 'L’offre', desc: 'Ta promesse, claire et désirable.', stage: 'Offre' },
      { type: 'compare', kicker: 'Même service, autre impact', bad: '« Coaching en organisation, 10 séances. »', good: '« Récupère *5 h par semaine* en 30 jours. »', badLabel: 'Une prestation', goodLabel: 'Un résultat' },
      { type: 'list', kicker: 'Les 4 ingrédients', title: 'Une offre qui *se vend seule.*', items: [
        ['Un résultat clair', 'Ce qui change concrètement pour le client.'],
        ['Un délai', 'En combien de temps il l’obtient.'],
        ['Une preuve', 'Témoignage, cas client, démonstration.'],
        ['Un risque réduit', 'Garantie, essai, paiement en plusieurs fois.'],
      ] },
      { type: 'formula', kicker: 'Ta promesse en une phrase', text: 'J’aide [ma cible] à [un résultat] en [un délai], sans [son frein].' },
      { type: 'cta', next: 'Ton projet est-il *rentable ?*', nextSub: '3 chiffres à connaître par cœur.' },
    ],
  },
  // ------------------------------------------------------------------ 05
  {
    n: 5, slug: 'chiffres', accent: 'teal', title: 'Les chiffres',
    scenes: [
      { type: 'hook', kicker: 'Épisode 05', lines: ['Rentable ?', '*Prouve-le*', 'en 3 chiffres.'] },
      { type: 'chapter', title: 'Le modèle', desc: 'Comment ton projet gagne de l’argent.', stage: 'Modèle éco.' },
      { type: 'list', kicker: 'Les 3 chiffres', title: 'À connaître *par cœur.*', items: [
        ['Ton prix', 'Ce que vaut le résultat, pas ton temps.'],
        ['Tes coûts', 'Fixes + variables. Tous. Même les petits.'],
        ['Ton seuil de rentabilité', 'Le nombre de ventes pour couvrir tes coûts.'],
      ] },
      { type: 'equation', kicker: 'Le calcul', title: 'Seuil de *rentabilité*', formula: ['Charges fixes', '÷', 'Marge par vente'], example: ['1 500 €', '÷', '50 €', '='], result: { value: 30, unit: 'ventes', label: 'par mois pour être à l’équilibre' } },
      { type: 'text', lines: ['N’oublie pas', 'dans tes coûts :'], small: '*Cotisations sociales, assurance, banque, outils, comptable… et ta propre rémunération.*' },
      { type: 'cta', next: 'Lancer *une première version*', nextSub: 'Le MVP, sans budget ni perfection.' },
    ],
  },
  // ------------------------------------------------------------------ 06
  {
    n: 6, slug: 'mvp', accent: 'purple', title: 'Le MVP',
    scenes: [
      { type: 'hook', kicker: 'Épisode 06', lines: ['N’attends pas', 'que ce soit', '*parfait.*'], sub: 'Ce qui est parfait n’est jamais lancé.' },
      { type: 'chapter', title: 'Le prototype', desc: 'Tester en vrai, vite et pas cher.', stage: 'MVP' },
      { type: 'text', lines: ['MVP : la plus petite', 'version qui prouve', 'que *ça marche.*'], small: 'Minimum Viable Product — produit minimum viable.' },
      { type: 'list', kicker: 'Sans coder, sans stock', title: '4 MVP à lancer *cette semaine.*', items: [
        ['Une page de vente', 'Avec un bouton « Je réserve ma place ».'],
        ['Une prestation à la main', 'Tu fais manuellement ce que tu automatiseras.'],
        ['Une précommande', 'Ils paient avant que ça existe.'],
        ['Une liste privée', 'Newsletter, groupe WhatsApp ou Discord.'],
      ] },
      { type: 'stat', kicker: 'Ton seul objectif', value: 3, label: 'premiers *clients payants.*<br>Pas des likes. Pas des « bonne idée ! ».' },
      { type: 'cta', next: 'Statut juridique & *financement*', nextSub: 'Micro, EURL, SASU : y voir clair.' },
    ],
  },
  // ------------------------------------------------------------------ 07
  {
    n: 7, slug: 'structurer', accent: 'coral', title: 'Statut & financement',
    scenes: [
      { type: 'hook', kicker: 'Épisode 07', lines: ['Micro, EURL,', 'SASU…', '*tu bloques ?*'], sub: 'On démêle ça en 40 secondes.' },
      { type: 'chapter', title: 'Structurer', desc: 'Le bon cadre, le bon financement.', stage: 'Structure' },
      { type: 'list', kicker: 'Les 3 statuts les plus courants', title: 'Lequel *pour toi ?*', items: [
        ['Micro-entreprise', 'Simple pour tester. Plafonds de chiffre d’affaires.'],
        ['EURL', 'Société à associé unique. Gérant non salarié.'],
        ['SASU', 'Très souple. Président assimilé salarié.'],
      ] },
      { type: 'text', lines: ['Le bon statut', 'dépend de *tes chiffres.*'], small: 'Chiffre d’affaires, charges, protection sociale, projets d’associés.' },
      { type: 'list', kicker: 'Financer sans tout sortir de ta poche', title: 'Les pistes *à explorer.*', items: [
        ['Prêt d’honneur', 'À taux zéro, sans garantie — Initiative France, Réseau Entreprendre.'],
        ['Bpifrance', 'Prêts, garanties bancaires, accompagnement.'],
        ['Aides régionales', 'Selon ta région et ton secteur.'],
        ['Droits France Travail', 'ARE ou ARCE, sous conditions.'],
      ] },
      { type: 'text', lines: ['Vérifie toujours', 'les *règles à jour.*'], small: 'URSSAF, Bpifrance Création, ta CCI ou ta CMA — et fais-toi accompagner.', size: 84 },
      { type: 'cta', next: 'Créer *ta marque*', nextSub: 'Le kit minimum pour exister.' },
    ],
  },
  // ------------------------------------------------------------------ 08
  {
    n: 8, slug: 'marque', accent: 'teal', title: 'La marque',
    scenes: [
      { type: 'hook', kicker: 'Épisode 08', lines: ['Un beau logo', '*ne sauve pas*', 'une offre', 'bancale.'], sub: 'Mais une marque claire fait vendre une bonne offre.' },
      { type: 'chapter', title: 'La marque', desc: 'Être reconnu, compris, choisi.', stage: 'Marque' },
      { type: 'list', kicker: 'Le kit minimum', title: 'Ce qu’il te faut *vraiment.*', items: [
        ['Un nom', 'Facile à dire, à écrire, à retrouver.'],
        ['Une promesse', 'Une phrase. Celle de l’épisode 04.'],
        ['Une identité simple', '2 couleurs, 2 typos, un style photo.'],
        ['Un profil pro', 'Sur LE réseau où se trouve ta cible.'],
      ] },
      { type: 'text', lines: ['Choisis *1 réseau.*', 'Maîtrise-le.', 'Puis élargis.'] },
      { type: 'compare', kicker: 'La régularité gagne', bad: 'Poster partout, quand tu y penses.', good: '*3 contenus par semaine,* au même endroit.' },
      { type: 'cta', next: 'Préparer *le lancement*', nextSub: 'Ton rétroplanning sur 30 jours.' },
    ],
  },
  // ------------------------------------------------------------------ 09
  {
    n: 9, slug: 'pre-lancement', accent: 'purple', title: 'Le pré-lancement',
    scenes: [
      { type: 'hook', kicker: 'Épisode 09', lines: ['On ne lance', 'pas *dans le vide.*'], sub: 'Un bon lancement se prépare 30 jours avant.' },
      { type: 'chapter', title: 'Pré-lancement', desc: 'Créer l’attente avant le jour J.', stage: 'Pré-lancement' },
      { type: 'timeline', kicker: 'Ton rétroplanning', steps: [
        ['J-30', 'Annonce le projet, montre les coulisses.'],
        ['J-21', 'Ouvre ta liste d’attente.'],
        ['J-14', 'Bêta-testeurs & premiers témoignages.'],
        ['J-7', 'Révèle l’offre de lancement, limitée.'],
        ['J-1', 'Rappel à toute ta liste.'],
      ] },
      { type: 'text', lines: ['Le jour J, tu ne', 'cherches pas des clients.', 'Tu préviens *ceux*', '*qui attendent.*'], size: 80 },
      { type: 'cta', next: 'Le *jour J*', nextSub: 'Et surtout : ce qui se passe après.' },
    ],
  },
  // ------------------------------------------------------------------ 10
  {
    n: 10, slug: 'lancement', accent: 'coral', title: 'Le lancement',
    scenes: [
      { type: 'hook', kicker: 'Épisode 10', lines: ['Jour J.', '*Ce n’est que*', '*le début.*'] },
      { type: 'chapter', title: 'Le lancement', desc: 'Ouvrir les portes. Puis apprendre.', stage: 'Lancement' },
      { type: 'checklist', kicker: 'Check-list du jour J', title: 'Avant d’appuyer *sur le bouton.*', items: [
        'Page de vente testée',
        'Paiement qui fonctionne',
        'Email envoyé à ta liste',
        'Publication + stories',
        'Message perso à 20 contacts',
      ] },
      { type: 'list', kicker: 'Après le lancement', title: 'La boucle *qui fait grandir.*', items: [
        ['Mesure', 'Ventes, visites, taux de conversion.'],
        ['Écoute', 'Appelle tes premiers clients.'],
        ['Ajuste', 'Offre, prix, message. Puis recommence.'],
      ] },
      { type: 'text', lines: ['Lancer,', 'c’est apprendre', '*en public.*'] },
      { type: 'cta', big: 'Tu veux être *accompagné·e ?*', comment: 'Commente « LANCEMENT »', actions: [
        ['plus', 'Abonne-toi', 'la série complète est sur le profil'],
        ['share', 'Partage', 'à quelqu’un qui a un projet en tête'],
      ], dur: 6.5 },
    ],
  },
];
