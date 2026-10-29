# Cahier des charges — Site vitrine « Amadou Niang »

**Accompagnement · Commercial · Pédagogie — Clermont-Ferrand**

| Élément | Valeur |
|---|---|
| Porteur du projet | Amadou Niang |
| Contact | niangamadou394@gmail.com · 06 17 56 63 42 |
| Version du document | 1.0 — 29/10/2026 |
| Dépôt | `niangamadou394-star/Ahamad63` (fichier `index.html`) |

---

## 1. Présentation du projet

### 1.1 Contexte
Amadou Niang est entrepreneur, freelance et alternant en Master Manager Commercial & Marketing (La Banque Postale, 2025–2027), basé à Clermont-Ferrand. Il propose :
- un service d'**assistance commerciale externalisée** aux artisans, commerçants, indépendants et porteurs de projets ;
- de l'**accompagnement entrepreneurial** (de l'idée au projet concret) ;
- de la **création de supports** (CV, LinkedIn, pitchs, flyers, réseaux sociaux) ;
- des **cours particuliers de mathématiques** (collège / lycée).

Le site existe aujourd'hui sous la forme d'une page unique (`index.html`). Ce cahier des charges formalise ses objectifs, son contenu et les évolutions attendues.

### 1.2 Objectifs
| # | Objectif | Indicateur de réussite |
|---|---|---|
| O1 | Présenter clairement l'offre et le parcours | Visiteur capable d'identifier les 4 services en moins de 30 s |
| O2 | Générer des demandes de contact qualifiées | ≥ 5 demandes / mois via le formulaire |
| O3 | Convertir vers les forfaits (Starter / Essentiel / Premium) | Clic sur « Choisir … » → prise de contact |
| O4 | Renforcer la crédibilité et l'image professionnelle | Taux de rebond < 60 %, retours qualitatifs |
| O5 | Être trouvé localement | Apparition sur « assistant commercial Clermont-Ferrand » |

### 1.3 Cibles
1. **Artisans et commerçants** de Clermont-Ferrand qui manquent de temps pour l'administratif commercial (devis, relances, e-mails, agenda).
2. **Porteurs de projets / entrepreneurs** souhaitant structurer une idée.
3. **Freelances, indépendants, dirigeants de TPE/PME**.
4. **Parents d'élèves** (collège / lycée) pour les cours de mathématiques.

---

## 2. Périmètre fonctionnel

### 2.1 Arborescence (page unique, navigation par ancres)
| Section | Ancre | Contenu |
|---|---|---|
| En-tête / navigation | — | Logo, liens, bouton « Me contacter », menu burger mobile |
| Accueil (hero) | — | Accroche « Je libère votre temps », prix d'appel (dès 150 €/mois), 2 boutons d'action |
| Chiffres clés | — | 48 h réponse · 3 forfaits · 100 % satisfaction · 1er échange gratuit |
| À propos | `#about` | Présentation, localisation, coordonnées, formation, langues |
| Expériences | `#experience` | Timeline : La Banque Postale, Acadomia, Complétude, SNS&AN Consulting, Ferme agro-élevage |
| Services | `#services` | 4 cartes de services numérotées |
| Forfaits | `#forfaits` | 3 offres tarifaires + bloc confidentialité / NDA |
| Méthode | — | 4 étapes : découverte, mise en place, prise en charge, bilan |
| Vision | `#vision` | Citations défilantes |
| Contact | `#contact` | Coordonnées + formulaire de demande |
| QR code | — | Partage du site |
| Pied de page | — | Signature, copyright, coordonnées |

### 2.2 Offre tarifaire à afficher
| Forfait | Prix / mois | Contenu | Délai de réponse |
|---|---|---|---|
| Starter | 150 € | 5 devis/factures, 10 relances, tableau de suivi partagé | 24 h |
| Essentiel *(populaire)* | 250 € | Starter + gestion e-mails 5 h/mois, agenda basique, rapport mensuel | 12 h |
| Premium | 400 € | Essentiel + e-mails & agenda illimités, suivi commercial complet, appel bilan 30 min | 4 h |

Conditions : sans engagement, résiliable à tout moment, 1er mois satisfait ou remboursé, NDA possible.

### 2.3 Exigences fonctionnelles
| Réf. | Exigence | Priorité |
|---|---|---|
| F1 | Navigation fluide vers chaque section (défilement doux), en-tête collant au scroll | Must |
| F2 | Menu burger plein écran sur mobile, fermé au clic sur un lien | Must |
| F3 | **Formulaire de contact fonctionnel** : nom, situation (liste), e-mail, besoin ; envoi réel par EmailJS | Must |
| F4 | Validation du formulaire (champs obligatoires, format e-mail) + messages de succès / d'erreur | Must |
| F5 | Boutons « Choisir Starter/Essentiel/Premium » pré-remplissant le besoin dans le formulaire | Should |
| F6 | Liens directs : `mailto:`, `tel:`, profil LinkedIn réel | Must |
| F7 | Carrousel de citations automatique (5 s) avec points de navigation | Could |
| F8 | QR code pointant vers l'URL définitive du site | Should |
| F9 | Animations d'apparition au défilement | Could |
| F10 | Prise de rendez-vous en ligne (Calendly / Google Agenda) pour l'échange découverte de 30 min | Could |
| F11 | Section témoignages / avis clients | Could |

---

## 3. Exigences non fonctionnelles

### 3.1 Charte graphique
- **Thème sombre** : fond `#060606`, accents dorés `#f0a500` / `#f5c040` / `#fde68a`, couleurs secondaires corail `#ff6b47`, turquoise `#0fa594`, violet `#9b5de5`.
- **Typographies** : *Playfair Display* (titres), *DM Sans* (texte).
- Ton : professionnel, chaleureux, direct.

### 3.2 Responsive & compatibilité
- Affichage correct de 320 px à 1920 px, sans défilement horizontal.
- Navigateurs : Chrome, Firefox, Safari, Edge (2 dernières versions), iOS et Android.

### 3.3 Performance
- Score Lighthouse Performance ≥ 90 sur mobile.
- Page < 500 Ko hors polices ; chargement < 2 s en 4G.

### 3.4 Accessibilité (RGAA / WCAG 2.1 AA)
- Contrastes suffisants (attention aux textes gris `--t3` sur fond noir).
- Libellés `<label>` associés à chaque champ du formulaire.
- Navigation au clavier, menu burger utilisable au clavier (`<button>` + `aria-expanded`).
- Texte alternatif sur les images, respect de `prefers-reduced-motion`.

### 3.5 Référencement (SEO)
- Balises `title` et `meta description` optimisées (déjà présentes).
- Ajout des balises Open Graph (partage LinkedIn / WhatsApp) et d'une favicon.
- Données structurées `LocalBusiness` (Clermont-Ferrand).
- Fiche Google Business Profile liée au site.

### 3.6 Juridique & RGPD
- **Mentions légales** (identité, statut juridique, SIRET, hébergeur).
- **Politique de confidentialité** : finalité du formulaire, durée de conservation, droits d'accès/suppression.
- Case de consentement sous le formulaire.
- Pas de cookies de suivi sans consentement.
- Conditions générales de vente pour les forfaits (résiliation, remboursement du 1er mois).

### 3.7 Sécurité
- Site statique servi en HTTPS.
- Clé publique EmailJS restreinte au domaine du site ; protection anti-spam (reCAPTCHA ou champ piège).

---

## 4. Contraintes techniques

| Élément | Choix |
|---|---|
| Technologie | HTML5 / CSS3 / JavaScript natif, fichier unique `index.html` |
| Dépendances | Google Fonts, EmailJS (`@emailjs/browser@3`), API QR code `api.qrserver.com` |
| Hébergement | GitHub Pages (gratuit, HTTPS) |
| Nom de domaine | Recommandé : domaine personnalisé (ex. `amadouniang.fr`) |
| Gestion de version | Git / GitHub |
| Maintenance | Mise à jour du contenu par Amadou Niang directement dans le fichier |

---

## 5. État actuel et corrections à prévoir

Constats relevés lors de l'analyse de `index.html` :

| # | Constat | Action |
|---|---|---|
| C1 | Le formulaire n'est pas relié à EmailJS : le script attend `#contact-form`, `#nom`, `#situation`, `#email`, `#message`, `#submit-btn`, `#form-success`, `#form-error`, qui n'existent pas ; le bouton affiche seulement une `alert()` | Envelopper les champs dans `<form id="contact-form">`, ajouter les `id` et les zones de message |
| C2 | Le lien « Vision » du menu mobile pointe vers `#vision`, ancre inexistante | Ajouter `id="vision"` à la section citations |
| C3 | Le lien LinkedIn pointe vers `https://linkedin.com` | Mettre l'URL réelle du profil |
| C4 | Le QR code pointe vers `niangamadou394-star.github.io/Amadou.N/` | Vérifier / mettre à jour avec l'URL définitive |
| C5 | Fautes et accents manquants : « 150€s », « metier », « ca », « base a », « Telephone », « Reponse », « determination », « elevage »… | Relecture orthographique complète |
| C6 | Mélange tutoiement / vouvoiement dans les services | Harmoniser (vouvoiement recommandé) |
| C7 | « 100 % satisfaction garantie » sans clients référencés | Remplacer par un engagement vérifiable ou ajouter des témoignages |
| C8 | Mentions légales et politique de confidentialité absentes | Créer les pages / sections (cf. 3.6) |

---

## 6. Planning prévisionnel

| Phase | Contenu | Durée |
|---|---|---|
| 1. Corrections | C1 à C6 : formulaire, ancres, liens, orthographe | 1 semaine |
| 2. Conformité | Mentions légales, RGPD, CGV, anti-spam | 1 semaine |
| 3. Visibilité | SEO, Open Graph, favicon, domaine, Google Business | 1 semaine |
| 4. Évolutions | Prise de RDV en ligne, témoignages, pré-remplissage forfaits | 2 semaines |
| 5. Recette & mise en ligne | Tests multi-appareils, Lighthouse, validation finale | 3 jours |

## 7. Budget indicatif

| Poste | Coût |
|---|---|
| Hébergement GitHub Pages | 0 € |
| EmailJS (offre gratuite, 200 e-mails/mois) | 0 € |
| Nom de domaine `.fr` | ≈ 10 €/an |
| Outil de prise de RDV (Calendly gratuit) | 0 € |
| **Total annuel** | **≈ 10 €** |

## 8. Recette — critères d'acceptation
- [ ] Un message envoyé depuis le formulaire arrive bien dans la boîte niangamadou394@gmail.com.
- [ ] Tous les liens du menu (desktop et mobile) mènent à une section existante.
- [ ] Le site s'affiche sans défaut sur iPhone, Android, tablette et ordinateur.
- [ ] Score Lighthouse ≥ 90 en Performance, Accessibilité, Bonnes pratiques et SEO.
- [ ] Aucune faute d'orthographe sur la page.
- [ ] Mentions légales et politique de confidentialité accessibles depuis le pied de page.
- [ ] Le QR code ouvre le site en production.

## 9. Livrables
1. `index.html` corrigé et enrichi.
2. Pages `mentions-legales.html` et `confidentialite.html`.
3. Favicon et image de partage Open Graph.
4. Site en ligne sur GitHub Pages (et domaine personnalisé le cas échéant).
5. Ce cahier des charges, tenu à jour.
