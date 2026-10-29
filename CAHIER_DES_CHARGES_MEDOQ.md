# Cahier des charges fonctionnel — Medoq

**« Votre médicament. Réservé. Prêt. »**
Plateforme de disponibilité et de réservation de médicaments en pharmacie — Dakar, Sénégal.

| Élément | Valeur |
|---|---|
| Porteur du projet | Amadou Niang, fondateur de Medoq |
| Contact | niangamadou394@gmail.com · +33 6 17 56 63 42 |
| Version du document | 1.0 — 29/10/2026 |
| Base d'analyse | Code des dépôts `medoq-api` (API + application web), `medoq-pharma`, `medoq-dashboard`, `medoq-mobile` |

---

## 1. Contexte et objectifs

### 1.1 Problème
À Dakar, un patient qui a besoin d'un médicament doit souvent faire plusieurs pharmacies avant de le trouver : il perd du temps et de l'argent en transport, sans savoir à l'avance si le produit est en stock ni à quel prix. Les pharmacies, elles, n'ont aucun canal numérique pour se faire connaître ni pour anticiper la demande.

### 1.2 Solution
Medoq connecte patients et pharmacies en temps réel :
1. le patient **cherche** un médicament et voit les pharmacies qui l'ont en stock, avec le prix et la distance ;
2. il **réserve** en quelques secondes : le médicament lui est mis de côté pendant 2 heures ;
3. il **paie** par Wave, Orange Money ou en espèces ;
4. il **récupère** son médicament au comptoir, ou se le fait livrer.

### 1.3 Objectifs
| # | Objectif | Indicateur |
|---|---|---|
| O1 | Trouver un médicament disponible en moins de 10 secondes | Temps entre la recherche et l'affichage des résultats |
| O2 | Réserver en moins de 30 secondes | Durée du parcours de réservation |
| O3 | Recruter les pharmacies de Dakar | 50 pharmacies actives (objectif affiché sur la page d'accueil) |
| O4 | Fiabiliser l'information de stock | Moins de 5 % de réservations annulées pour rupture |
| O5 | Rendre le modèle rentable | Commission de 1,5 % par transaction + frais de livraison |

---

## 2. Acteurs et rôles

| Rôle | Code | Description | Accès |
|---|---|---|---|
| Visiteur | — | Personne non connectée | Recherche de médicaments et de pharmacies, mode démo |
| Patient | `PATIENT` | Utilisateur qui réserve des médicaments | Application patient |
| Pharmacien / personnel | `PHARMACY_STAFF` | Employé rattaché à une pharmacie | Espace pharmacie |
| Administrateur | `ADMIN` | Équipe Medoq | Validation des pharmacies, catalogue, statistiques |
| Livreur *(à créer)* | — | Personne qui assure les livraisons | Voir § 4.9 |

---

## 3. Périmètre

| Composant | Technologie | Rôle | Statut |
|---|---|---|---|
| API REST | Node.js 22, Express, PostgreSQL, JWT | Toute la logique métier | En production sur Render |
| Application web (PWA) | HTML/JS servi par l'API | Patient + pharmacie + démo | En ligne |
| Page d'accueil | `landing.html` | Présentation, inscription des pharmacies | En ligne |
| Tableau de bord pharmacie | Angular | Version avancée de l'espace pharmacie | Prototype |
| Application mobile | Flutter (version web compilée) | Application patient native | Prototype |
| SMS | Africa's Talking | Codes OTP, notifications | Intégré |
| E-mail | Gmail SMTP | Alertes admin | Intégré |
| Paiement | Wave, Orange Money | Paiement mobile | **Simulé — à intégrer** |

---

## 4. Spécifications fonctionnelles

Légende des priorités : **P1** = indispensable au lancement · **P2** = importante · **P3** = évolution.
Statut : ✅ existe · 🟡 partiel · ❌ à développer.

### 4.1 Inscription et connexion

| Réf. | Fonction | Règles de gestion | Priorité | Statut |
|---|---|---|---|---|
| AUTH-01 | Inscription patient | Nom, téléphone (obligatoires), e-mail (facultatif), mot de passe de 6 caractères minimum. Vérification du numéro par **code SMS (OTP) valable 10 minutes**. | P1 | ✅ |
| AUTH-02 | Connexion | Par téléphone **ou** e-mail + mot de passe. | P1 | ✅ |
| AUTH-03 | Protection contre les tentatives | Après **5 échecs**, compte bloqué **15 minutes**. | P1 | ✅ |
| AUTH-04 | Session | Jeton d'accès valable 24 h, jeton de rafraîchissement valable 7 jours, déconnexion. | P1 | ✅ |
| AUTH-05 | Mot de passe oublié | Code SMS puis choix d'un nouveau mot de passe. | P1 | ✅ |
| AUTH-06 | Profil | Consulter et modifier son nom, e-mail, adresse ; changer de mot de passe. | P1 | ✅ |
| AUTH-07 | Inscription pharmacie | Nom, adresse, téléphone, **numéro de licence** (unique), nom et téléphone du responsable, mot de passe. Le compte reste **inactif** jusqu'à validation par un administrateur (24–48 h) ; l'admin reçoit un e-mail. | P1 | ✅ |
| AUTH-08 | Plusieurs employés par pharmacie | Le responsable invite ses collègues. | P2 | ❌ |
| AUTH-09 | Suppression de compte | Le patient peut supprimer son compte et ses données. | P1 | ❌ |

### 4.2 Recherche de médicaments

| Réf. | Fonction | Règles de gestion | Priorité | Statut |
|---|---|---|---|---|
| MED-01 | Recherche par nom | Recherche par nom commercial ou **DCI** (molécule) ; résultats dès la saisie. | P1 | ✅ |
| MED-02 | Fiche médicament | Nom, DCI, forme, dosage, catégorie, description, mention « sur ordonnance », liste des pharmacies qui l'ont en stock avec prix. | P1 | ✅ |
| MED-03 | Médicaments populaires | Liste mise en avant sur l'accueil. | P2 | ✅ |
| MED-04 | Catégories | Filtrer par catégorie thérapeutique. | P2 | ✅ |
| MED-05 | Médicaments remboursés CMU | Liste des médicaments pris en charge par la Couverture Maladie Universelle. | P2 | ✅ |
| MED-06 | Médicaments équivalents | Proposer un générique de même DCI quand le produit est en rupture. | P2 | ❌ |
| MED-07 | Alerte de disponibilité | Prévenir le patient par SMS quand un médicament introuvable revient en stock. | P3 | ❌ |
| MED-08 | Gestion du catalogue | L'admin ajoute des médicaments ; il doit aussi pouvoir les modifier et les désactiver. | P1 | 🟡 |

### 4.3 Pharmacies

| Réf. | Fonction | Règles de gestion | Priorité | Statut |
|---|---|---|---|---|
| PHA-01 | Pharmacies proches | À partir de la position GPS du patient, rayon par défaut **10 km**, tri par distance ; filtre possible sur un médicament. | P1 | ✅ |
| PHA-02 | Fiche pharmacie | Nom, adresse, téléphone, horaires, note, médicaments disponibles, itinéraire. | P1 | ✅ |
| PHA-03 | Horaires d'ouverture | Le pharmacien modifie ses horaires jour par jour ; affichage « ouvert / fermé ». | P1 | 🟡 |
| PHA-04 | **Pharmacies de garde** | Afficher les pharmacies de garde la nuit et le week-end. Le calendrier des gardes doit être géré côté serveur (saisie admin ou import du planning officiel). | P1 | 🟡 *(affiché dans l'interface, absent de l'API)* |
| PHA-05 | Avis et notes | Le patient note la pharmacie (1 à 5) après une réservation terminée. | P3 | 🟡 *(champ en base, pas de saisie)* |
| PHA-06 | Carte | Affichage des pharmacies sur une carte. | P2 | ❌ |

### 4.4 Gestion du stock (espace pharmacie)

| Réf. | Fonction | Règles de gestion | Priorité | Statut |
|---|---|---|---|---|
| STK-01 | Liste du stock | Médicament, quantité, prix unitaire (FCFA), seuil d'alerte ; recherche. | P1 | ✅ |
| STK-02 | Ajouter / modifier | Ajouter un médicament du catalogue avec quantité et prix ; modifier quantité, prix et seuil. | P1 | ✅ |
| STK-03 | Alerte stock bas | Signaler les produits sous le seuil (5 par défaut) sur le tableau de bord. | P1 | ✅ |
| STK-04 | Import en masse | Import d'un fichier CSV `medicament;quantite;prix` à l'inscription (script d'onboarding). À proposer directement dans l'interface. | P2 | 🟡 |
| STK-05 | Mise à jour du stock à la réservation | Le stock est décrémenté à la réservation et **restitué** à l'annulation ou à l'expiration. | P1 | 🟡 *(restitution à l'expiration manquante)* |
| STK-06 | Connexion au logiciel de la pharmacie | Synchronisation automatique avec le logiciel de gestion officinal. | P3 | ❌ |

### 4.5 Réservation

**Cycle de vie d'une réservation**

```
          ┌──────────► CANCELLED (patient ou pharmacie)
          │
CONFIRMED ──► READY ──► COMPLETED
          │
          └──────────► EXPIRED (au bout de 2 h sans retrait)  ← à développer
```

| Réf. | Fonction | Règles de gestion | Priorité | Statut |
|---|---|---|---|---|
| RES-01 | Créer une réservation | Choix du médicament, de la pharmacie et de la quantité (≥ 1). Vérification du stock **dans une transaction** pour éviter que deux patients réservent la dernière boîte. | P1 | ✅ |
| RES-02 | Numéro de référence | Format `MRX-AAAA-000123`, unique ; sert de **code de retrait** au comptoir. | P1 | ✅ |
| RES-03 | Durée de réservation | Médicament mis de côté **2 heures** (paramétrable). | P1 | ✅ |
| RES-04 | **Expiration automatique** | Passé le délai, la réservation passe en `EXPIRED`, le stock est restitué, le patient est prévenu. | P1 | ❌ |
| RES-05 | Mode de récupération | Retrait en pharmacie (gratuit) ou **livraison (+1 500 FCFA)**, adresse obligatoire, délai annoncé 30–60 min, Dakar intramuros. | P1 | ✅ |
| RES-06 | Médicament sur ordonnance | Retrait en pharmacie **obligatoire** (pas de livraison), le patient coche qu'il possède une ordonnance valide, présentation de l'original au comptoir, paiement sur place. | P1 | ✅ |
| RES-07 | Photo de l'ordonnance | Le patient joint une photo ; le pharmacien la valide avant de préparer. | P2 | ❌ |
| RES-08 | Mes réservations | Liste filtrable : toutes, confirmées, prêtes, terminées, annulées. | P1 | ✅ |
| RES-09 | Annulation | Possible tant que le statut est `CONFIRMED` ; le stock est restitué. | P1 | ✅ |
| RES-10 | Côté pharmacie | Liste des réservations reçues ; actions **« Prête »** puis **« Remise au patient »**. | P1 | ✅ |
| RES-11 | Panier multi-médicaments | Réserver plusieurs médicaments d'une même ordonnance en une seule fois. | P2 | ❌ |
| RES-12 | Code QR de retrait | Afficher la référence sous forme de QR code, scanné par le pharmacien. | P3 | ❌ |

### 4.6 Paiement

| Réf. | Fonction | Règles de gestion | Priorité | Statut |
|---|---|---|---|---|
| PAY-01 | Choix du moyen | **Wave**, **Orange Money** ou **espèces**. | P1 | ✅ |
| PAY-02 | Espèces | Paiement enregistré « en attente » puis validé automatiquement quand la pharmacie remet le médicament. | P1 | ✅ |
| PAY-03 | **Wave / Orange Money réels** | Intégration des API marchandes : redirection vers le paiement, réception de la confirmation (webhook), remboursement. Aujourd'hui l'URL de paiement est **fictive**. | P1 | ❌ |
| PAY-04 | Commission Medoq | **1,5 %** du montant de chaque transaction (paramétrable), enregistrée sur chaque paiement. | P1 | ✅ |
| PAY-05 | Confirmation manuelle | La pharmacie ou l'admin peut confirmer un paiement. | P1 | ✅ |
| PAY-06 | Remboursement | Remboursement automatique en cas d'annulation, d'expiration ou de rupture, selon la politique de remboursement publiée. | P1 | ❌ |
| PAY-07 | Reversement aux pharmacies | Relevé périodique : montants encaissés moins commission, virement à la pharmacie. | P2 | ❌ |
| PAY-08 | Reçu | Reçu numérique envoyé au patient. | P2 | ❌ |

### 4.7 Notifications

| Réf. | Événement | Destinataire | Canal | Statut |
|---|---|---|---|---|
| NOT-01 | Code OTP | Patient / pharmacien | SMS | ✅ |
| NOT-02 | Réservation confirmée | Patient | SMS | ✅ |
| NOT-03 | Médicament prêt | Patient | SMS | ✅ |
| NOT-04 | Nouvelle pharmacie à valider | Admin | E-mail | ✅ |
| NOT-05 | **Nouvelle réservation reçue** | Pharmacie | Son / notification dans l'app + SMS | ❌ |
| NOT-06 | Réservation bientôt expirée (30 min avant) | Patient | SMS | ❌ |
| NOT-07 | Notifications dans l'application | Tous | Notifications push (PWA / mobile) | 🟡 |

### 4.8 Administration

| Réf. | Fonction | Statut |
|---|---|---|
| ADM-01 | Création du premier compte admin (protégée par une clé secrète, une seule fois) | ✅ |
| ADM-02 | Liste des pharmacies en attente ; **activer** ou **refuser** | ✅ |
| ADM-03 | Liste de toutes les pharmacies | ✅ |
| ADM-04 | Statistiques : patients, pharmacies actives / en attente, réservations, paiements | ✅ |
| ADM-05 | Liste de toutes les réservations avec filtres | ✅ |
| ADM-06 | Suspendre un patient ou une pharmacie | ❌ |
| ADM-07 | Gestion du planning des pharmacies de garde | ❌ |
| ADM-08 | Interface d'administration graphique (aujourd'hui l'API seule) | 🟡 |

### 4.9 Livraison *(évolution)*

| Réf. | Fonction | Priorité |
|---|---|---|
| LIV-01 | Attribution de la commande à un livreur | P2 |
| LIV-02 | Statuts « en cours de livraison » / « livrée » | P2 |
| LIV-03 | Suivi du livreur en temps réel | P3 |
| LIV-04 | Extension de la zone au-delà de Dakar intramuros | P3 |

### 4.10 Tableau de bord pharmacie

| Réf. | Indicateur | Statut |
|---|---|---|
| TDB-01 | Réservations du jour, en attente, terminées | ✅ |
| TDB-02 | Revenus générés via Medoq | ✅ |
| TDB-03 | Alertes de stock bas | ✅ |
| TDB-04 | Dernières réservations | ✅ |
| TDB-05 | Statistiques avancées : médicaments les plus demandés, recherches sans résultat, évolution mensuelle | 🟡 |

### 4.11 Mode démonstration

| Réf. | Fonction | Statut |
|---|---|---|
| DEM-01 | Découvrir l'application avec des données fictives, sans compte (patient et pharmacie) | ✅ |
| DEM-02 | Comptes de démonstration clairement séparés des vraies données | ✅ |

---

## 5. Parcours utilisateurs

### 5.1 Patient — réserver un médicament
1. Ouvre Medoq (web ou mobile) et autorise la géolocalisation.
2. Tape « Amoxicilline » → la liste des pharmacies proches qui l'ont en stock s'affiche, avec prix et distance.
3. Choisit une pharmacie, la quantité, le mode de récupération et de paiement.
4. Confirme → reçoit le numéro `MRX-…` à l'écran et par SMS.
5. Reçoit un SMS « Votre médicament est prêt ».
6. Se présente au comptoir avec son numéro (et son ordonnance si besoin), paie si ce n'est pas déjà fait, repart.

### 5.2 Pharmacie — traiter une réservation
1. Reçoit une alerte « Nouvelle réservation ».
2. Prépare le produit → appuie sur **« Prête »** (le patient est prévenu par SMS).
3. À l'arrivée du patient, vérifie le numéro → **« Remise au patient »**.
4. Le stock et le paiement en espèces sont mis à jour automatiquement.

### 5.3 Pharmacie — rejoindre Medoq
1. Remplit le formulaire « Inscrire ma pharmacie » (licence obligatoire).
2. L'équipe Medoq vérifie la licence et active le compte sous 24–48 h.
3. La pharmacie saisit ou importe son stock et ses horaires → elle devient visible des patients.

---

## 6. Exigences non fonctionnelles

### 6.1 Ergonomie
- Pensée **mobile d'abord**, utilisable avec une connexion 3G lente et sur des téléphones d'entrée de gamme.
- Installable sur l'écran d'accueil (PWA), avec fonctionnement minimal hors connexion (consultation des réservations).
- Langue : français ; **wolof** à prévoir (P2).
- Montants en **FCFA**, numéros au format `+221`.

### 6.2 Performance et disponibilité
- Résultats de recherche en moins de 1 seconde.
- Disponibilité visée : 99,5 %. L'offre gratuite de Render met le serveur en veille et la base gratuite est limitée : **passer à une offre payante avant le lancement public**.
- Sauvegarde quotidienne de la base de données.

### 6.3 Sécurité
- Mots de passe chiffrés (bcrypt), jetons JWT, contrôle des rôles sur chaque route : ✅.
- Le secret JWT ne doit **jamais** retomber sur une valeur par défaut en production (le code utilise `medoq-secret` si la variable manque) : à corriger.
- HTTPS obligatoire ; limitation du nombre de requêtes (envoi d'OTP notamment, pour éviter les abus de SMS).
- Journal des actions sensibles (validation de pharmacie, paiements).

### 6.4 Données de santé et conformité
- Respect de la **loi sénégalaise n° 2008-12** sur les données personnelles et déclaration auprès de la **CDP** (Commission de Protection des Données Personnelles).
- Les réservations révèlent des traitements médicaux : ce sont des **données de santé**, accès strictement limité, durée de conservation définie.
- Respect de la réglementation pharmaceutique : Medoq **ne vend pas** de médicaments, il met en relation ; la délivrance reste faite par le pharmacien. À valider avec l'**Ordre des Pharmaciens du Sénégal** et la **Direction de la Pharmacie et du Médicament**.
- Pages légales déjà publiées : mentions légales, confidentialité, cookies, remboursement ✅. À ajouter : **conditions générales d'utilisation** (CGU) pour patients et pharmacies.
- Mesure d'audience anonyme sans cookie (Plausible) ✅.

---

## 7. Paramètres métier

| Paramètre | Valeur actuelle | Variable |
|---|---|---|
| Commission Medoq | 1,5 % | `COMMISSION_RATE` |
| Durée de réservation | 2 heures | `RESERVATION_EXPIRY_HOURS` |
| Frais de livraison | 1 500 FCFA | `DELIVERY_FEE` |
| Validité d'un code SMS | 10 minutes | — |
| Blocage après échecs de connexion | 5 essais → 15 min | — |
| Rayon de recherche par défaut | 10 km | — |
| Seuil d'alerte stock | 5 unités | — |

---

## 8. Modèle de données (résumé)

| Table | Contenu |
|---|---|
| `users` | Patients, pharmaciens, admins (téléphone, e-mail, rôle, état du compte) |
| `otp_codes` | Codes SMS et leur validité |
| `pharmacies` | Nom, adresse, coordonnées GPS, horaires, licence, note, actif / vérifié |
| `pharmacy_users` | Lien entre une pharmacie et ses employés |
| `medications` | Catalogue : nom, DCI, forme, dosage, catégorie, ordonnance, CMU |
| `pharmacy_stock` | Quantité, prix et seuil par pharmacie et par médicament |
| `reservations` | Référence, patient, pharmacie, médicament, quantité, statut, expiration, montant, livraison |
| `payments` | Moyen, montant, commission, statut, références Wave / Orange Money |
| `refresh_tokens` | Sessions |

À ajouter : `on_duty_schedule` (gardes), `reviews` (avis), `prescriptions` (photos d'ordonnance), `notifications`, `payouts` (reversements), et un détail de réservation sur plusieurs lignes pour le panier.

---

## 9. Feuille de route

| Phase | Contenu | Durée indicative |
|---|---|---|
| **1. Prêt pour le lancement** | Expiration automatique (RES-04), paiement Wave et Orange Money réel (PAY-03, PAY-06), alerte nouvelle réservation (NOT-05), pharmacies de garde côté serveur (PHA-04), suppression de compte, CGU, secret JWT, limitation des OTP, offre d'hébergement payante | 6 semaines |
| **2. Pilote** | 10 à 20 pharmacies de Dakar, import du stock dans l'interface, gestion du catalogue par l'admin, suspension de comptes | 4 semaines |
| **3. Croissance** | Panier multi-médicaments, photo d'ordonnance, génériques, avis, carte, reversements, reçus | 8 semaines |
| **4. Expansion** | Application mobile publiée sur les stores, livreurs, wolof, autres villes, alertes de retour en stock, connexion aux logiciels officinaux | En continu |

---

## 10. Critères d'acceptation du lancement
- [ ] Un patient s'inscrit avec un vrai code SMS et réserve un médicament de bout en bout.
- [ ] Deux patients qui réservent la dernière boîte en même temps : un seul réussit.
- [ ] Une réservation non retirée expire au bout de 2 h et le stock est restitué.
- [ ] Un paiement Wave et un paiement Orange Money réels sont reçus, confirmés et remboursables.
- [ ] La pharmacie est alertée en moins de 10 secondes d'une nouvelle réservation.
- [ ] Un médicament sur ordonnance ne peut pas être livré.
- [ ] Une pharmacie non validée n'apparaît jamais dans les résultats.
- [ ] Les pharmacies de garde du jour s'affichent correctement.
- [ ] L'application reste utilisable sur un téléphone d'entrée de gamme en 3G.
