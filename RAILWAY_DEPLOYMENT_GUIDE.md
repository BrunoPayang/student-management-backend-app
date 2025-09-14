# Guide de Déploiement Railway avec GitLab

Ce guide vous accompagnera étape par étape pour déployer votre application de gestion d'étudiants sur Railway avec GitLab.

## 📋 Prérequis

- Compte GitLab
- Compte Railway (gratuit)
- Code source de votre application prêt

## 🚀 Étapes de Déploiement

### 1. Préparation du Repository GitLab

#### 1.1 Créer un nouveau repository GitLab
1. Allez sur [GitLab](https://gitlab.com) et connectez-vous
2. Cliquez sur "New project" → "Create blank project"
3. Nommez votre repository (ex: `student-management-backend`)
4. Choisissez "Public" ou "Private" selon vos besoins
5. **Ne cochez PAS** "Initialize repository with a README" (votre projet en a déjà un)
6. Cliquez sur "Create project"

#### 1.2 Pousser votre code vers GitLab
```bash
# Dans votre terminal, naviguez vers votre projet
cd C:\Users\bgano\Desktop\project\student-management-backend-app

# Initialisez git si ce n'est pas déjà fait
git init

# Ajoutez tous les fichiers
git add .

# Créez le commit initial
git commit -m "Initial commit: Student Management Backend"

# Ajoutez votre repository GitLab comme origine
git remote add origin https://gitlab.com/VOTRE_USERNAME/VOTRE_REPO_NAME.git

# Poussez vers GitLab
git push -u origin main
```

### 2. Configuration Railway

#### 2.1 Créer un compte Railway
1. Allez sur [Railway](https://railway.app)
2. Cliquez sur "Login" et connectez-vous avec GitLab
3. Autorisez Railway à accéder à vos repositories GitLab

#### 2.2 Créer un nouveau projet
1. Dans le dashboard Railway, cliquez sur "New Project"
2. Sélectionnez "Deploy from GitLab repo"
3. Choisissez votre repository `student-management-backend`
4. Railway va automatiquement détecter votre `railway.json` et `Dockerfile`

### 3. Configuration des Variables d'Environnement

#### 3.1 Variables essentielles à configurer
Dans votre projet Railway, allez dans l'onglet "Variables" et ajoutez :

```bash
# Django Configuration
DEBUG=False
SECRET_KEY=votre-clé-secrète-très-longue-et-complexe
DJANGO_SETTINGS_MODULE=schoolconnect.settings.production

# Database (Railway fournira automatiquement DATABASE_URL)
# Pas besoin de la configurer manuellement

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://votre-frontend-domain.com,https://votre-app-mobile.com

# Firebase Configuration (optionnel)
FIREBASE_ENABLED=False

# Email Configuration (pour les notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=votre-email@gmail.com

# File Upload Settings
ALLOWED_FILE_TYPES=.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif
MAX_FILE_SIZE_MB=10

# Notification Settings
ENABLE_FCM_NOTIFICATIONS=True
ENABLE_EMAIL_NOTIFICATIONS=True
```

#### 3.2 Générer une clé secrète Django
```python
# Exécutez cette commande dans votre terminal Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 4. Configuration de la Base de Données

#### 4.1 Ajouter PostgreSQL
1. Dans votre projet Railway, cliquez sur "New Service"
2. Sélectionnez "Database" → "PostgreSQL"
3. Railway créera automatiquement une base de données
4. La variable `DATABASE_URL` sera automatiquement ajoutée

#### 4.2 Migrations automatiques
Railway exécutera automatiquement les migrations lors du déploiement grâce à votre `Dockerfile`.

### 5. Déploiement

#### 5.1 Déploiement automatique
1. Railway détectera automatiquement votre `railway.json`
2. Le déploiement commencera automatiquement
3. Surveillez les logs dans l'onglet "Deployments"

#### 5.2 Vérification du déploiement
Une fois déployé, vous obtiendrez une URL comme : `https://votre-projet-production.up.railway.app`

Testez votre API :
```bash
# Test de santé
curl https://votre-projet-production.up.railway.app/api/health/

# Test des endpoints principaux
curl https://votre-projet-production.up.railway.app/api/schools/
```

### 6. Configuration du Domaine Personnalisé (Optionnel)

#### 6.1 Ajouter un domaine personnalisé
1. Dans votre projet Railway, allez dans "Settings"
2. Section "Domains"
3. Ajoutez votre domaine personnalisé
4. Configurez les enregistrements DNS selon les instructions Railway

### 7. Surveillance et Maintenance

#### 7.1 Logs et Monitoring
- Consultez les logs dans l'onglet "Deployments"
- Surveillez les métriques dans l'onglet "Metrics"

#### 7.2 Mises à jour
Pour mettre à jour votre application :
```bash
# Faites vos modifications localement
git add .
git commit -m "Update: Description des modifications"
git push origin main

# Railway déploiera automatiquement les changements
```

## 🔧 Dépannage

### Problèmes Courants

#### 1. Erreur de Build
- Vérifiez que tous les fichiers requis sont dans votre repository
- Assurez-vous que `requirements/production.txt` est correct

#### 2. Erreur de Base de Données
- Vérifiez que PostgreSQL est bien configuré
- Assurez-vous que `DATABASE_URL` est définie

#### 3. Erreur CORS
- Vérifiez `CORS_ALLOWED_ORIGINS` dans les variables d'environnement
- Ajoutez votre domaine frontend à la liste

#### 4. Erreur de Fichiers Statiques
- Les fichiers statiques sont automatiquement collectés par le `Dockerfile`
- Vérifiez que `STATICFILES_STORAGE` est configuré dans `production.py`

### Commandes Utiles

```bash
# Vérifier les logs Railway
railway logs

# Accéder à la base de données
railway connect

# Redéployer manuellement
railway redeploy
```

## 📱 Configuration Frontend

Une fois déployé, mettez à jour votre application frontend avec la nouvelle URL :

```javascript
// Dans votre configuration frontend
const API_BASE_URL = 'https://votre-projet-production.up.railway.app/api/';
```

## 🔐 Sécurité

### Recommandations
1. **Jamais** commitez de clés secrètes dans votre code
2. Utilisez toujours HTTPS en production
3. Configurez des domaines autorisés dans `ALLOWED_HOSTS`
4. Activez les notifications d'erreur avec Sentry (optionnel)

### Variables Sensibles
- `SECRET_KEY` : Générée automatiquement
- `DATABASE_URL` : Fournie par Railway
- `EMAIL_HOST_PASSWORD` : Mot de passe d'application Gmail

## 📊 Monitoring

Railway fournit :
- Logs en temps réel
- Métriques de performance
- Surveillance de la santé de l'application
- Alertes automatiques

## 🎉 Félicitations !

Votre application est maintenant déployée sur Railway ! 

**URL de votre API** : `https://votre-projet-production.up.railway.app/api/`

**Documentation API** : `https://votre-projet-production.up.railway.app/api/schema/swagger-ui/`

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez les logs Railway
2. Vérifiez la configuration des variables d'environnement
3. Testez localement avec les mêmes paramètres
4. Consultez la documentation Railway : https://docs.railway.app
