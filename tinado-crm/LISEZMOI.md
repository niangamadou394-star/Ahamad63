# CRM Maison Tinado : installation gratuite (5 minutes)

Le site est en ligne sur **https://tinado-gestion.onrender.com**. Les données sont enregistrées dans un Google Sheet de votre compte.

1. Ouvrez https://sheets.new (un nouveau Google Sheet) et nommez-le « Maison Tinado - Gestion ».
2. Menu **Extensions > Apps Script**. Effacez tout le code, collez le contenu de `apps-script/Code.gs`.
3. Sur la ligne `const CODE_ACCES = "CHANGER-MOI";`, remplacez CHANGER-MOI par le code d'accès choisi. Enregistrez (icône disquette).
4. Bouton **Déployer > Nouveau déploiement**. Type : **Application Web**. Exécuter en tant que : **Moi**. Qui a accès : **Tout le monde**. Cliquez **Déployer**, puis autorisez l'accès à votre compte (« Paramètres avancés > Accéder au projet »).
5. Copiez l'**URL de l'application Web** (elle finit par `/exec`) et envoyez-la à YOKK. YOKK la colle dans `static/config.js`, et le CRM est prêt.

Les données restent dans l'onglet « donnees » du Google Sheet : vous pouvez les consulter, mais ne les modifiez pas à la main.
