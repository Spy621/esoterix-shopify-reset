# 🔥 GUIDE RESET COMPLET SHOPIFY

**Script:** `esoterix_shopify_reset_complete.py`

Ce script effectue **4 phases** en sécurité complète:
1. ✅ **SAUVEGARDE** - Exporte tous vos produits en CSV
2. 🗑️ **SUPPRESSION** - Supprime les 3000 produits (avec confirmation)
3. 📥 **SCRAPING** - Récupère tous les produits d'Esoterix
4. ✨ **RECRÉATION** - Crée proprement dans Shopify

---

## 📋 Avant de lancer

**Vérifications:**
- [ ] Vous avez sauvegardé vos données ailleurs (au cas où)
- [ ] Pas de commandes en cours avec ces produits
- [ ] Vous êtes 100% sûr de vouloir recommencer

---

## 🚀 LANCEMENT DU RESET

### Option 1: Lancer localement (pour tester)

```bash
# Installation des dépendances
pip install -r requirements.txt

# Créez un fichier .env avec:
ESOTERIX_EMAIL=votre_email
ESOTERIX_PASSWORD=votre_password
SHOPIFY_STORE=universdelaura
SHOPIFY_ACCESS_TOKEN=shss_851964f70bcf9fd694d8f6877b163a

# Lancez le script
python esoterix_shopify_reset_complete.py
```

### Option 2: Une seule fois sur Render (recommandé)

Créez un service Render temporaire:

1. Allez sur **render.com/dashboard**
2. **+ New** → **Web Service**
3. Connectez votre repo GitHub
4. Remplissez:
   - **Name**: `esoterix-shopify-reset`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python esoterix_shopify_reset_complete.py`

5. Ajoutez les variables d'environnement
6. Déployez
7. Allez dans **Logs** et confirmez la suppression (taper: `OUI JE CONFIRME SUPPRESSION`)
8. Attendez la fin (~30-45 min pour 3000 produits)

---

## ⚙️ LE PROCESSUS DÉTAILLÉ

### Phase 1: SAUVEGARDE (2-5 min)

```
💾 SAUVEGARDE EN COURS...
📊 1000 produits téléchargés...
📊 2000 produits téléchargés...
📊 3000 produits téléchargés...
✅ SAUVEGARDE COMPLÈTE: backup_shopify_universdelaura_20260910_143022.csv
📊 Total: 3000 produits sauvegardés
```

**Fichier créé:** `backup_shopify_universdelaura_YYYYMMDD_HHMMSS.csv`
→ Vous pouvez le télécharger comme sécurité

### Phase 2: SUPPRESSION (5-15 min)

```
🔴 3000 produits à supprimer

⚠️  ATTENTION - OPÉRATION IRRÉVERSIBLE!

Vous êtes sur le point de SUPPRIMER 3000 PRODUITS de Shopify.

Cette action est PERMANENTE et NON REVERSIBLE.

Les produits seront complètement supprimés de votre boutique.
Une sauvegarde CSV a été créée comme précaution.

Pour confirmer, tapez exactement: OUI JE CONFIRME SUPPRESSION

✓ Votre réponse: OUI JE CONFIRME SUPPRESSION

✅ Confirmation acceptée. Suppression en cours...
🔥 SUPPRESSION EN COURS...
🗑️  100/3000 produits supprimés...
🗑️  200/3000 produits supprimés...
...
🔥 SUPPRESSION COMPLÈTE: 3000/3000 produits supprimés
```

**⚠️ Important:** Vous DEVEZ taper exactement `OUI JE CONFIRME SUPPRESSION` pour confirmer.

### Phase 3: SCRAPING ESOTERIX (10-20 min)

```
🔓 Connexion à Esoterix...
✅ Connecté à Esoterix
🔍 Récupération des catégories...
✅ 25 catégories trouvées
📄 Encens - Page 1
📄 Encens - Page 2
...
✅ Total: 3050 produits scrapés
```

### Phase 4: RECRÉATION (15-30 min)

```
🚀 RECRÉATION EN COURS: 3050 produits
[50/3050] Recréation en cours...
[100/3050] Recréation en cours...
...
✅ Recréation terminée: 3050 créés, 0 échoués
```

---

## 📊 RÉSUMÉ FINAL

```
======================================================================
📊 RÉSUMÉ FINAL
======================================================================
✅ Sauvegarde: backup_shopify_universdelaura_20260910_143022.csv
🗑️  Supprimés: 3000 produits
📥 Scrapés: 3050 produits Esoterix
✨ Créés: 3050 produits
❌ Échoués: 0 produits
======================================================================
```

---

## ✅ APRÈS LE RESET - Vérifications

### 1. Vérifier dans Shopify Admin

```
Products → Vous devez voir ~3050 produits
          avec les catégories:
          ├─ Encens
          ├─ Minéraux
          ├─ Bougies
          ├─ Bijoux
          └─ ... (25+ collections)
```

### 2. Vérifier les détails d'un produit

Cliquez sur un produit, vérifiez:
- ✅ **Titre** = Nom Esoterix
- ✅ **SKU** = Généré automatiquement
- ✅ **Prix** = Prix Esoterix × 4
- ✅ **Description** = Avec keywords SEO
- ✅ **Image** = Téléchargée depuis Esoterix
- ✅ **Stock** = Synchronisé
- ✅ **Collection** = Catégorie Esoterix

### 3. Vérifier une image

Cliquez sur un produit avec image → Vérifiez que l'image s'affiche correctement.

### 4. Vérifier le pricing

```
Esoterix: 5€
Shopify: 20€ (5€ × 4) ✓
```

---

## 🕐 TEMPS ESTIMÉS

| Phase | Temps |
|-------|-------|
| Sauvegarde | 5 min |
| Suppression | 15 min |
| Scraping Esoterix | 20 min |
| Recréation Shopify | 30 min |
| **TOTAL** | **~70 min** |

---

## 🆘 TROUBLESHOOTING

### ❌ "Timeout lors de la suppression"
```
Solution: Relancez le script
Le script reprendra depuis où il s'est arrêté
```

### ❌ "Chrome ne démarre pas"
```
Solution: Render installe automatiquement ChromeDriver
Si local: pip install webdriver-manager
```

### ❌ "Certains produits n'ont pas d'image"
```
Solution: Esoterix n'avait pas d'image pour ces produits
Vous pouvez les ajouter manuellement après
```

### ❌ "Stocks incorrects"
```
Solution: Vérifiez que Esoterix avait les bons stocks
Le script utilise les stocks d'Esoterix directement
```

### ❌ "Erreur API Shopify"
```
Solution: 
1. Vérifiez le token dans les variables d'env
2. Vérifiez que le store name est correct
3. Vérifiez la limite API Shopify (2000 req/min)
```

---

## 💾 APRÈS LE RESET

### Vous pouvez:
- ✅ Modifier les prix (si vous le souhaitez)
- ✅ Ajouter des descriptions additionnelles
- ✅ Ajouter des collections personnalisées
- ✅ Modifier les images
- ✅ Activer des fonctionnalités Shopify

### Le script continuera:
- ✅ À synchroniser les stocks chaque semaine (version 1.0)
- ✅ À mettre à jour les prix (× 4)
- ✅ À récupérer les nouveaux produits

---

## 🔄 APRÈS LE RESET - Retour à la sync automatique

Une fois le reset terminé:

1. **Supprimez le service Render temporaire** (reset)
2. **Créez un Cron Job Render** avec `esoterix_shopify_sync.py` (sync hebdo)
3. **Schedule**: `0 2 * * 0` (lundi 2h du matin)

La sync automatique mettra à jour:
- ✅ Stocks
- ✅ Prix (reste × 4)
- ✅ Images
- ✅ Ajoute nouveaux produits

---

## ⚠️ POINTS IMPORTANTS

1. **Sauvegarde automatique** 
   - Un CSV est créé avant suppression
   - Téléchargez-le comme sécurité supplémentaire

2. **Confirmation explicite**
   - Vous devez taper `OUI JE CONFIRME SUPPRESSION`
   - Pas de confirmation silencieuse

3. **Logs détaillés**
   - Tous les logs sont enregistrés
   - Vous pouvez les consulter après

4. **SKU uniques**
   - Chaque produit reçoit un SKU unique (hash du nom)
   - Évite les doublons lors des syncs futures

5. **Collections automatiques**
   - Une collection par catégorie Esoterix
   - Créées automatiquement pendant la recréation

---

## ✅ Checklist avant de lancer

- [ ] J'ai vérifié qu'il n'y a pas de commandes en cours
- [ ] J'ai noté ma sauvegarde au cas où
- [ ] Je sais que c'est irréversible
- [ ] J'ai mes credentials Esoterix et Shopify
- [ ] Je suis prêt(e) à attendre ~70 minutes
- [ ] Je comprends que tous les produits seront supprimés et recréés

---

**Quand vous êtes prêt(e), lancez le script!** 🚀

Les produits seront recréés proprement avec:
- ✅ SKU uniques
- ✅ Descriptions SEO
- ✅ Prix × 4
- ✅ Images
- ✅ Stocks
- ✅ Collections organisées
