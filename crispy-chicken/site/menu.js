/* Carte Crispy Chicken : une seule source pour le site et les écrans.
   Pour changer un prix : modifier ici, le site se met à jour tout seul. */
window.CC_INFO = {
  nom: "Crispy Chicken",
  slogan: "Spécialiste Naan, Wings & Tenders",
  telephone: "",          // à compléter, ex. "01 23 45 67 89"
  adresse: "",            // à compléter
  ville: "",              // à compléter
  horaires: "",           // à compléter, ex. "Tous les jours · 11h30 – 23h30"
  instagram: "",          // à compléter, ex. "crispychicken"
  commande: ""            // lien Uber Eats / Deliveroo / commande en ligne, à compléter
};

window.CC_MENU = [
  { id: "naans", titre: "Naans spéciaux", sous: "Pain naan cuit au tandoor, garni selon la recette.", items: [
    { n: "Naan Tenders", p: 8.5, d: "3 tenders de poulet, cheddar fondant, légumes et sauce au choix.", i: ["tender", "tender", "tender", "cheddar", "legumes", "sauce"] },
    { n: "Naan Tenders/Steak", p: 9.5, d: "2 steaks hachés, 1 tender de poulet, cheddar fondant, légumes et sauce au choix.", i: ["steak", "steak", "tender", "cheddar", "legumes", "sauce"] },
    { n: "Naan Steak", p: 8.5, d: "3 steaks hachés, cheddar fondant, légumes et sauce au choix.", i: ["steak", "steak", "steak", "cheddar", "legumes", "sauce"] },
    { n: "Naan Mix", p: 9.5, d: "2 tenders de poulet, 1 steak haché, 1 œuf, cheddar fondant, légumes et sauce au choix.", i: ["tender", "tender", "steak", "oeuf", "cheddar", "legumes", "sauce"] },
    { n: "Naan Tikka", p: 9.0, d: "250 g de poulet mariné à la sauce Tikka, cheddar fondant, légumes et sauce au choix.", i: ["poulet", "cheddar", "legumes", "sauce"] },
    { n: "Naan Curry", p: 9.0, d: "250 g de poulet mariné à la sauce Curry, cheddar fondant, légumes et sauce au choix.", i: ["poulet", "cheddar", "legumes", "sauce"] },
    { n: "Naan Suprême", p: 9.0, d: "3 steaks hachés, 1 œuf, cheddar fondant, légumes et sauce au choix.", i: ["steak", "steak", "steak", "oeuf", "cheddar", "legumes", "sauce"] },
    { n: "Naan Crispy Dynamite", p: 10.0, d: "2 tenders de poulet, 1 steak haché, 1 galette de pommes de terre, cheddar fondant, oignons frits et sauce Dynamite.", i: ["tender", "tender", "steak", "galette", "cheddar", "oignons", "sauce"], star: true },
    { n: "Naan Farmer", p: 9.0, d: "2 steaks hachés, 1 tender de poulet, cheddar fondant, légumes et sauce au choix.", i: ["steak", "steak", "tender", "cheddar", "legumes", "sauce"] },
    { n: "Cheese Naan", p: 2.5, d: "Naan maison au fromage fondant.", i: ["cheddar"] } ] },
  { id: "burgers", titre: "Burgers", items: [
    { n: "Cheeseburger", p: 3.9 },
    { n: "Double Cheeseburger", p: 5.9 },
    { n: "Big Steak Burger", p: 6.5, d: "3 steaks hachés, 2 tranches de cheddar fondant, salade et sauce burger.", i: ["steak", "steak", "steak", "cheddar", "salade", "sauce"] },
    { n: "Crispy Burger", p: 7.9, d: "2 tenders de poulet, 1 galette de pommes de terre, 2 tranches de cheddar fondant, salade et sauce mayonnaise au poivre.", i: ["tender", "tender", "galette", "cheddar", "salade", "sauce"], star: true },
    { n: "Crispy Twice Burger", p: 7.9, d: "3 tenders de poulet, 2 tranches de cheddar fondant, salade et sauce mayonnaise.", i: ["tender", "tender", "tender", "cheddar", "salade", "sauce"] } ] },
  { id: "wraps", titre: "Wraps", items: [
    { n: "Wrap Crispy Star", p: 8.5, d: "2 tenders de poulet, 1 galette de pommes de terre, cheddar fondant, salade et sauce mayonnaise au poivre.", i: ["tender", "tender", "galette", "cheddar", "salade", "sauce"], star: true },
    { n: "Wrap Tenders", p: 8.5, d: "3 tenders de poulet, cheddar fondant, salade et sauce mayonnaise au poivre.", i: ["tender", "tender", "tender", "cheddar", "salade", "sauce"] },
    { n: "Mini Wrap Tenders", p: 3.0, d: "1 tender de poulet, cheddar fondant, salade et sauce Biggy.", i: ["tender", "cheddar", "salade", "sauce"] } ] },
  { id: "wings", titre: "Wings & Tenders", items: [
    { n: "3 Wings", p: 4.0 }, { n: "6 Wings", p: 5.9 }, { n: "10 Wings", p: 9.5 },
    { n: "3 Tenders", p: 4.9 }, { n: "5 Tenders", p: 7.0 }, { n: "10 Tenders", p: 13.9 } ] },
  { id: "crousty", titre: "Crousty", sous: "Riz, poulet et sauce au choix.", items: [
    { n: "Crousty Mini", p: 5.0 }, { n: "Crousty Medium", p: 10.0 }, { n: "Crousty Max", p: 12.5 } ] },
  { id: "formules", titre: "Formules", sous: "Tous nos menus sont servis avec frites et boisson.", items: [
    { n: "Menu Étudiant", p: 10.0, d: "Naan Tenders ou 10 Wings, avec frites et boisson." },
    { n: "Menu Enfant", p: 7.0, d: "Mini Wrap, frites et boisson." },
    { n: "Menu Crousty Mini", p: 8.9, d: "Crousty Mini, frites et boisson." },
    { n: "Menu Mix", p: 10.0, d: "3 Wings + 3 Tenders, avec frites et boisson." } ] },
  { id: "family", titre: "Family Packs", items: [
    { n: "Family Box Wings", p: 25.0, d: "30 Wings." },
    { n: "Family Box Tenders", p: 26.5, d: "20 Chicken Tenders." },
    { n: "Family Mix Box", p: 25.9, d: "15 Wings + 10 Tenders." } ] },
  { id: "sides", titre: "Accompagnements", items: [
    { n: "Frites", p: 2.5 }, { n: "Frites au cheddar", p: 4.5 }, { n: "Tenders Cheese", p: 5.5 },
    { n: "Tenders Dynamite", p: 5.5 }, { n: "Pommes de terre en rondelles", p: 4.5 }, { n: "Onion Rings (6 pièces)", p: 3.5 } ] },
  { id: "desserts", titre: "Desserts", items: [
    { n: "Tiramisu", p: 3.5 }, { n: "Donut", p: 2.0 }, { n: "Tarte au Daim", p: 3.5 } ] },
  { id: "boissons", titre: "Boissons", items: [
    { n: "Boisson soft (33 cl)", p: 2.0 }, { n: "Eau", p: 1.5 }, { n: "Coca-Cola (1,5 L)", p: 4.0 } ] },
];

window.CC_ING = { tender: "Tender", steak: "Steak haché", cheddar: "Cheddar", legumes: "Légumes", sauce: "Sauce", salade: "Salade", oeuf: "Œuf", galette: "Galette", oignons: "Oignons frits", poulet: "Poulet mariné" };
window.ccPrix = p => p.toFixed(2).replace(".", ",") + " €";
