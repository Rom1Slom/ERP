# 🚀 Démarrage Rapide - Rôles Client & OF

## ⚡ 5 minutes pour tester

### 1️⃣ Préparer les données de test (30 secondes)

```bash
# Créer les utilisateurs de test
python create_test_users.py
```

**Output attendu:**
```
✓ Entreprise Client créée: ACME Corp
✓ Entreprise OF mise à jour: Kompetans.fr
✓ Utilisateur Client créé: client_user
✓ Utilisateur OF créé: of_user
```

### 2️⃣ Lancer le serveur (20 secondes)

```bash
# Démarrer Django
python manage.py runserver
```

**Output attendu:**
```
Starting development server at http://127.0.0.1:8000/
```

### 3️⃣ Tester la connexion Client (2 minutes)

**Accédez à:** `http://localhost:8000/accounts/login/`

**Identifiants:**
- Pseudo: `client_user`
- Mot de passe: `password123`

**Vérifications:**
1. ✅ Connexion réussie
2. ✅ Redirection vers `/dashboard/client/`
3. ✅ Badge "CLIENT" visible
4. ✅ Menu affiche options client:
   - Salariés
   - Formations
   - Habilitations
   - Demandes
5. ✅ Tableau de bord affiche statistiques client

### 4️⃣ Tester la connexion OF (2 minutes)

**Déconnectez-vous** puis reconnectez-vous:

**Identifiants:**
- Pseudo: `of_user`
- Mot de passe: `password123`

**Vérifications:**
1. ✅ Connexion réussie
2. ✅ Redirection vers `/dashboard/of/`
3. ✅ Badge "ORGANISME DE FORMATION" visible
4. ✅ Menu affiche options OF:
   - Sessions
   - Validation
   - Référence
5. ✅ Tableau de bord affiche statistiques OF

## 🎯 Points de contrôle importants

### Redirection après connexion
```
Client User → /dashboard/client/ ✅
OF User     → /dashboard/of/     ✅
```

### Menus affichés
```
Client Menu:              OF Menu:
├─ Dashboard         ✅   ├─ Dashboard         ✅
├─ Salariés         ✅   ├─ Sessions          ✅
├─ Formations       ✅   ├─ Validation        ✅
├─ Habilitations    ✅   ├─ Référence         ✅
└─ Demandes         ✅   └─ Demandes          ✅
```

### Vérification des rôles

```bash
# Vérifier en shell Django
python manage.py shell

>>> from django.contrib.auth.models import User
>>> from habilitations_app.models import ProfilUtilisateur
>>> 
>>> client = User.objects.get(username='client_user')
>>> client.profil.role
'client'
>>> client.profil.est_client
True
>>> client.profil.est_of
False
>>>
>>> of = User.objects.get(username='of_user')
>>> of.profil.role
'of'
>>> of.profil.est_of
True
>>> of.profil.est_client
False
```

## 🔒 Test d'accès restreint

### Tester la sécurité

**Client essayant d'accéder au dashboard OF:**
```
URL: http://localhost:8000/dashboard/of/
Résultat: ❌ Erreur d'accès (redirection ou message)
```

**OF essayant d'accéder au dashboard Client:**
```
URL: http://localhost:8000/dashboard/client/
Résultat: ❌ Erreur d'accès (redirection ou message)
```

## 📱 Parcours complet

### Parcours Client

```
1. Connexion (client_user)
   ↓
2. Dashboard Client
   ├─ Voir: 0 salariés
   ├─ Voir: 0 formations
   ├─ Voir: 0 habilitations
   └─ Voir: 0 demandes
   ↓
3. Cliquer "Ajouter un salarié"
   ↓
4. Remplir le formulaire
   ↓
5. Soumettre
   ↓
6. Retour au dashboard
   ↓
7. Voir le salarié ajouté (1)
```

### Parcours OF

```
1. Connexion (of_user)
   ↓
2. Dashboard OF
   ├─ Voir: 0 sessions
   ├─ Voir: 0 formations à valider
   └─ Voir: 0 demandes
   ↓
3. Cliquer "Créer une session"
   ↓
4. Remplir le formulaire
   ↓
5. Soumettre
   ↓
6. Retour au dashboard
   ↓
7. Voir la session créée
```

## 🐛 Troubleshooting rapide

### "ProfilUtilisateur DoesNotExist"

**Cause:** Utilisateur sans profil

**Solution:**
```bash
# Créer le profil manuellement
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from habilitations_app.models import Entreprise, ProfilUtilisateur
>>> user = User.objects.get(username='...')
>>> entreprise = Entreprise.objects.first()
>>> ProfilUtilisateur.objects.create(
...     user=user,
...     entreprise=entreprise,
...     role='client'
... )
```

### "Accès réservé aux clients"

**Cause:** Utilisateur avec mauvais rôle

**Solution:**
```bash
# Vérifier/modifier le rôle
python manage.py shell
>>> profil = User.objects.get(username='...').profil
>>> print(profil.role)
'of'  # ❌ Devrait être 'client'
>>> profil.role = 'client'
>>> profil.save()
>>> print(profil.est_client)
True  # ✅
```

### Menu ne s'affiche pas correctement

**Cause:** Template non rechargé

**Solution:**
1. Vider le cache du navigateur (Ctrl+F5)
2. Recharger la page
3. Vérifier la console du navigateur (F12 → Console)

## 📚 Documentation complète

Pour aller plus loin, consultez:

1. **ROLES_GUIDE.md** - Guide détaillé des rôles
2. **ROLES_SUMMARY.md** - Résumé des changements
3. **ARCHITECTURE_ROLES.md** - Diagrammes d'architecture
4. **FICHIERS_MODIFIES.md** - Liste complète des fichiers modifiés

## ✅ Checklist de vérification

### Avant de déployer

- [ ] Tests des deux rôles réussis
- [ ] Menu affiché correctement
- [ ] Redirection OK
- [ ] Accès restreint fonctionne
- [ ] Base de données OK
- [ ] Pas d'erreurs en console
- [ ] Admin Django fonctionne
- [ ] Utilisateurs de test créés
- [ ] Documentation lue

### Après déploiement

- [ ] Créer les utilisateurs réels
- [ ] Assigner les rôles corrects
- [ ] Tester en environnement réel
- [ ] Vérifier les logs
- [ ] Monitorer les performances

## 🎓 Prochaines étapes

### Immédiatement (1 heure)
1. Tester les deux rôles
2. Vérifier la sécurité
3. Consulter la documentation

### Demain (plusieurs heures)
1. Adapter les vues existantes avec les décorateurs
2. Ajouter les tests unitaires
3. Optimiser les performances

### Cette semaine (plusieurs jours)
1. Intégrer les permissions granulaires
2. Ajouter les logs d'audit
3. Documenter les APIs

## 💬 Besoin d'aide?

Consultez les fichiers:
- **ROLES_GUIDE.md** - Questions sur les rôles
- **ARCHITECTURE_ROLES.md** - Questions sur l'architecture
- **decorators.py** - Code des décorateurs
- **views.py** - Code des vues

---

**Bon test!** 🎉
