# ⚡ RESET COMPLET - DÉMARRAGE RAPIDE (5 min de config)

**Opération:** Supprimer 3000 produits → Recréer proprement depuis Esoterix

---

## 🎯 En 3 étapes

### 1️⃣ Sur Render - Créer un service temporaire

```
https://render.com/dashboard

+ New → Cron Job

Name: esoterix-shopify-reset
Runtime: Python 3
Build: pip install -r requirements.txt
Start: python esoterix_shopify_reset_complete.py
Schedule: 0 0 * * * (tout de suite, pas important)

Environment:
ESOTERIX_EMAIL = votre_email
ESOTERIX_PASSWORD = votre_password
SHOPIFY_STORE = universdelaura
SHOPIFY_ACCESS_TOKEN = shss_851964f70bcf9fd694d8f6877b163a

Create
```

### 2️⃣ Regarder les logs

```
Dashboard → esoterix-shopify-reset → Logs

Vous verrez:
✅ Sauvegarde de vos 3000 produits (CSV)
🔴 Demande: "Tapez OUI JE CONFIRME SUPPRESSION"
   → TAPEZ EXACTEMENT: OUI JE CONFIRME SUPPRESSION
🗑️ Suppression (15 min)
📥 Scraping Esoterix (20 min)
✨ Recréation (30 min)
```

### 3️⃣ Attendre ~70 min

Le script va:
- Sauvegarder vos 3000 produits
- Les supprimer
- Scraper tous les produits Esoterix
- Les recréer proprement

---

## ✅ Après le reset

**Allez dans Shopify:**
```
Products → Vous devez voir ~3050 produits
           avec collections (Encens, Minéraux, etc.)
```

**Supprimez le service Render temporaire:**
```
Dashboard → esoterix-shopify-reset → Delete
```

**Créez le Cron Job de sync automatique (optionnel):**
```
Si vous voulez continuer à syncer chaque semaine:

+ New → Cron Job
Name: esoterix-shopify-sync
Runtime: Python 3
Build: pip install -r requirements.txt
Start: python esoterix_shopify_sync.py
Schedule: 0 2 * * 0 (chaque lundi 2h du matin)

Environment: (même que avant)
```

---

## ⏱️ Durée totale

**~70-90 minutes** (surtout les délais de scraping/création)

---

## 📋 Checklist rapide

- [ ] Variables d'env préparées
- [ ] Service Render créé
- [ ] Logs accessibles
- [ ] Je vais taper `OUI JE CONFIRME SUPPRESSION` quand demandé
- [ ] Je vais attendre la fin

---

**C'est tout !** Lancez et laissez faire. 🚀
