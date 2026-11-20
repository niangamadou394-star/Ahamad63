# CRM YOKK : installation gratuite (5 minutes)

Le site est en ligne sur **https://yokk-crm.onrender.com**. Les données sont enregistrées dans un Google Sheet du compte YOKK (séparé de celui de Maison Tinado).

1. Ouvrez https://sheets.new et nommez le tableau « YOKK - CRM ».
2. Menu **Extensions > Apps Script**. Effacez tout le code, collez le contenu de `apps-script/Code.gs`.
3. Ligne `const CODE_ACCES = "CHANGER-MOI";` : remplacez CHANGER-MOI par le code de l'équipe. Enregistrez.
4. **Déployer > Nouveau déploiement**. Type : **Application Web**. Exécuter en tant que : **Moi**. Qui a accès : **Tout le monde**. Déployez et autorisez.
5. Copiez l'URL qui finit par `/exec` et collez-la dans `static/config.js`.

Chaque membre se connecte avec son prénom et le code. Le bandeau « en ligne », la vue Équipe et le bureau 3D montrent qui est connecté et ce qu'il consulte.
