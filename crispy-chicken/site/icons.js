/* Ingrédients : vraies photos extraites des visuels produits */
(function () {
  const base = window.CC_IMG_BASE || "img/";
  const keys = ["tender", "steak", "cheddar", "legumes", "sauce", "salade", "oeuf", "galette", "oignons", "poulet"];
  window.CC_ICON = Object.fromEntries(keys.map(k => [k, `<img class="ingimg" src="${base}ing/${k}.webp" alt="">`]));
})();
