/* Carte Crispy Chicken : une seule source pour le site et les écrans.
   Pour changer un prix : modifier ici, le site se met à jour tout seul. */
window.CC_INFO = {
  nom: "Crispy Chicken",
  slogan: "Spécialiste Naan, Wings & Tenders",
  telephone: "07 51 05 36 56",
  email: "nirobsm4@gmail.com",
  adresse: "62 rue Fontgiève",
  ville: "63000 Clermont-Ferrand",
  horaires: "",           // à compléter, ex. "Tous les jours · 11h30 – 23h30"
  instagram: "",          // à compléter, ex. "crispychicken"
  // Mentions légales : à compléter dès que le client les donne
  societe: "INDIAN SHOP",            // raison sociale, ex. "SAS CRISPY CHICKEN"
  forme: "SARL au capital de 1 000 €",              // forme juridique et capital, ex. "SAS au capital de 1 000 €"
  siret: "100 583 954 00019",              // numéro SIRET (14 chiffres)
  rcs: "RCS Clermont-Ferrand 100 583 954",                // ex. "RCS Paris 123 456 789"
  tva: "",                // numéro de TVA intracommunautaire
  siege: "62 rue Fontgiève, 63000 Clermont-Ferrand",              // adresse du siège social
  directeur: "Shahjahan Monwar, gérant",          // nom du directeur de la publication
  domaine: "",            // nom de domaine définitif, ex. "crispychicken.fr"
  commande: "https://www.ubereats.com/store-browse-uuid/cabf92a0-9efb-5406-9217-25480c896916?diningMode=DELIVERY"
};

window.CC_MENU = [
  { id: "naans", titre: "Naans spéciaux", sous: "Pain naan cuit au tandoor, garni selon la recette.", items: [
    { n: "Naan Tenders", img: "naan-tenders", p: 8.5, d: "3 tenders de poulet, cheddar fondant, légumes et sauce au choix.", i: ["tender", "tender", "tender", "cheddar", "legumes", "sauce"] },
    { n: "Naan Tenders/Steak", img: "naan-tenders-steak", p: 9.5, d: "2 steaks hachés, 1 tender de poulet, cheddar fondant, légumes et sauce au choix.", i: ["steak", "steak", "tender", "cheddar", "legumes", "sauce"] },
    { n: "Naan Steak", img: "naan-steak", p: 8.5, d: "3 steaks hachés, cheddar fondant, légumes et sauce au choix.", i: ["steak", "steak", "steak", "cheddar", "legumes", "sauce"] },
    { n: "Naan Mix", img: "naan-mix", p: 9.5, d: "2 tenders de poulet, 1 steak haché, 1 œuf, cheddar fondant, légumes et sauce au choix.", i: ["tender", "tender", "steak", "oeuf", "cheddar", "legumes", "sauce"] },
    { n: "Naan Tikka", img: "naan-tikka", p: 9.0, d: "250 g de poulet mariné à la sauce Tikka, cheddar fondant, légumes et sauce au choix.", i: ["poulet", "cheddar", "legumes", "sauce"] },
    { n: "Naan Curry", img: "naan-curry", p: 9.0, d: "250 g de poulet mariné à la sauce Curry, cheddar fondant, légumes et sauce au choix.", i: ["poulet", "cheddar", "legumes", "sauce"] },
    { n: "Naan Suprême", img: "naan-supreme", p: 9.0, d: "3 steaks hachés, 1 œuf, cheddar fondant, légumes et sauce au choix.", i: ["steak", "steak", "steak", "oeuf", "cheddar", "legumes", "sauce"] },
    { n: "Naan Crispy Dynamite", img: "naan-dynamite", p: 10.0, d: "2 tenders de poulet, 1 steak haché, 1 galette de pommes de terre, cheddar fondant, oignons frits et sauce Dynamite.", i: ["tender", "tender", "steak", "galette", "cheddar", "oignons", "sauce"], star: true },
    { n: "Naan Farmer", img: "naan-farmer", p: 9.0, d: "2 steaks hachés, 1 tender de poulet, cheddar fondant, légumes et sauce au choix.", i: ["steak", "steak", "tender", "cheddar", "legumes", "sauce"] },
    { n: "Cheese Naan", img: "cheese-naan", p: 2.5, d: "Naan maison au fromage fondant." } ] },
  { id: "burgers", titre: "Burgers", items: [
    { n: "Cheeseburger", img: "cheeseburger", p: 3.9 },
    { n: "Double Cheeseburger", img: "double-cheeseburger", p: 5.9 },
    { n: "Big Steak Burger", img: "big-steak", p: 6.5, d: "3 steaks hachés, 2 tranches de cheddar fondant, salade et sauce burger.", i: ["steak", "steak", "steak", "cheddar", "salade", "sauce"] },
    { n: "Crispy Burger", img: "crispy-burger", p: 7.9, d: "2 tenders de poulet, 1 galette de pommes de terre, 2 tranches de cheddar fondant, salade et sauce mayonnaise au poivre.", i: ["tender", "tender", "galette", "cheddar", "salade", "sauce"], star: true },
    { n: "Crispy Twice Burger", img: "crispy-twice", p: 7.9, d: "3 tenders de poulet, 2 tranches de cheddar fondant, salade et sauce mayonnaise.", i: ["tender", "tender", "tender", "cheddar", "salade", "sauce"] } ] },
  { id: "wraps", titre: "Wraps", items: [
    { n: "Wrap Crispy Star", img: "wrap-star", p: 8.5, d: "2 tenders de poulet, 1 galette de pommes de terre, cheddar fondant, salade et sauce mayonnaise au poivre.", i: ["tender", "tender", "galette", "cheddar", "salade", "sauce"], star: true },
    { n: "Wrap Tenders", img: "wrap-tenders", p: 8.5, d: "3 tenders de poulet, cheddar fondant, salade et sauce mayonnaise au poivre.", i: ["tender", "tender", "tender", "cheddar", "salade", "sauce"] },
    { n: "Mini Wrap Tenders", img: "wrap-tenders", p: 3.0, d: "1 tender de poulet, cheddar fondant, salade et sauce Biggy.", i: ["tender", "cheddar", "salade", "sauce"] } ] },
  { id: "wings", titre: "Wings & Tenders", items: [
    { n: "3 Wings", img: "wings", p: 4.0 }, { n: "6 Wings", img: "wings-box", p: 5.9 }, { n: "10 Wings", img: "wings-box", p: 9.5 },
    { n: "3 Tenders", img: "tenders", p: 4.9 }, { n: "5 Tenders", img: "tenders-box", p: 7.0 }, { n: "10 Tenders", img: "tenders-box", p: 13.9 } ] },
  { id: "crousty", titre: "Crousti", sous: "Riz thaï parfumé, poulet croustillant et sauce maison au choix.", items: [
    { n: "Tasty Crousti Mini", img: "crousti-original", p: 6.9, d: "Poulet frit croustillant, riz thaï parfumé, sauce maison au choix et oignons frits.", i: ["poulet", "sauce", "oignons"] },
    { n: "Crousti Original", img: "crousti-original", p: 11.5, d: "Poulet frit ultra croustillant, riz thaï parfumé, sauce blanche maison ou sauce au choix, oignons frits et persil frais.", i: ["poulet", "sauce", "oignons"], star: true },
    { n: "Tasty Crousti pommes de terre", img: "crousti-pdt", p: 11.5, d: "Poulet frit ultra croustillant, pommes de terre en rondelles, sauce blanche maison ou sauce au choix, oignons frits et persil frais.", i: ["poulet", "galette", "sauce", "oignons"] },
    { n: "Crousti Alloco Crunch", img: "crousti-alloco", p: 12.9, d: "Riz blanc, tenders croustillants, banane plantain, sauce maison et oignons frits.", i: ["tender", "sauce", "oignons"] },
    { n: "Bowl Tenders Dynamite", img: "bowl-dynamite", p: 7.5, d: "3 tenders coupés en morceaux, mélangés à la sauce Dynamite et garnis d'oignons frits croustillants.", i: ["tender", "tender", "tender", "sauce", "oignons"] } ] },
  { id: "formules", titre: "Formules", sous: "Boisson comprise dans tous nos menus.", items: [
    { n: "Menu Étudiant", img: "naan-tenders", p: 10.0, d: "Naan Tenders ou 10 Wings, avec frites et boisson." },
    { n: "Menu Enfant", img: "menu-enfant", p: 7.0, d: "Mini Wrap, frites et boisson." },
    { n: "Menu Crousti Mini", img: "menu-crousti-mini", p: 12.5, d: "1 Tasty Crousti Mini, 1 tiramisu et 1 boisson au choix." },
    { n: "Menu Mix", img: "wings-box", p: 10.0, d: "3 Wings + 3 Tenders, avec frites et boisson." } ] },
  { id: "family", titre: "Family Packs", items: [
    { n: "Family Box Wings", img: "family-wings", p: 25.0, d: "30 Wings." },
    { n: "Family Box Tenders", img: "family-tenders", p: 26.5, d: "20 Chicken Tenders." },
    { n: "Family Mix Box", img: "family-mix", p: 25.9, d: "15 Wings + 10 Tenders." } ] },
  { id: "sides", titre: "Accompagnements", items: [
    { n: "Frites", img: "frites", p: 2.5 }, { n: "Frites au cheddar", p: 4.5 }, { n: "Tenders Cheese", img: "tenders-cheese", p: 5.5 },
    { n: "Tenders Dynamite", p: 5.5 }, { n: "Pommes de terre en rondelles", p: 4.5 }, { n: "Onion Rings (6 pièces)", img: "onion-rings", p: 3.9, d: "Anneaux d'oignon panés, ultra croustillants et dorés." } ] },
  { id: "desserts", titre: "Desserts", items: [
    { n: "Tiramisu Spéculoos Caramel", img: "tiramisu-speculoos", p: 4.0, d: "Tiramisu crémeux au mascarpone, morceaux de spéculoos et caramel." }, { n: "Donut", img: "donut", p: 2.0 }, { n: "Tarte au Daim", p: 3.5 } ] },
  { id: "boissons", titre: "Boissons", items: [
    { n: "Boisson soft (33 cl)", p: 2.0 }, { n: "Eau", p: 1.5 }, { n: "Coca-Cola (1,5 L)", p: 4.0 } ] },
];

window.CC_ING = { tender: "Tender", steak: "Steak haché", cheddar: "Cheddar", legumes: "Légumes", sauce: "Sauce", salade: "Salade", oeuf: "Œuf", galette: "Galette", oignons: "Oignons frits", poulet: "Poulet mariné" };
window.ccPrix = p => p.toFixed(2).replace(".", ",") + " €";
