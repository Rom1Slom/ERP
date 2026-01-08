# Guide complet de gestion des habilitations électriques

## 🚀 Démarrage

### 1. Activez l'environnement virtuel

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Lancez le serveur

```bash
python manage.py runserver
```

### 3. Accédez à l'application

- **Accueil**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/ (identifiants: admin / admin123)
- **Dashboard**: http://localhost:8000/dashboard/ (après connexion)

---

## 👤 Connexion et authentification

### Créer un nouvel utilisateur

1. Allez à http://localhost:8000/admin/
2. Connectez-vous avec les identifiants admin
3. Cliquez sur "Utilisateurs"
4. Cliquez sur "Ajouter utilisateur"
5. Remplissez le formulaire
6. Attribuez les permissions appropriées

### Rôles par défaut

- **Administrateur**: Accès complet au système
- **Secrétaire**: Peut gérer les stagiaires et formations
- **Formateur**: Peut valider les compétences et créer les avis

---

## 🏢 Gestion des entreprises

### Créer une entreprise

1. Allez à http://localhost:8000/admin/
2. Cliquez sur "Entreprises"
3. Cliquez sur "Ajouter une entreprise"
4. Remplissez les champs:
   - **Nom**: Nom de l'entreprise
   - **Email**: Email de contact
   - **Téléphone**: Numéro de contact
   - **Adresse**: Adresse complète
   - **Code postal**: Code postal
   - **Ville**: Ville

### Habilitations par défaut

Les habilitations suivantes sont disponibles:

| Code | Nom | Catégorie | Description |
|------|-----|-----------|-------------|
| **B1V** | Exécution de travaux sous tension - BT | Basse Tension | Travaux en présence de tension |
| **B1X** | Travaux de proximité - BT | Basse Tension | Travaux à proximité de zones dangereuses |
| **B2V** | Exécution de travaux sous tension - HT | Haute Tension | Travaux HT sous tension |
| **BR** | Interventions sur installations | Basse Tension | Maintenance et réparation |

---

## 👥 Gestion des stagiaires

### Créer un stagiaire

1. Cliquez sur "Stagiaires" dans la navigation
2. Cliquez sur "Nouveau stagiaire"
3. Remplissez les informations:
   - **Nom**: Nom de famille
   - **Prénom**: Prénom
   - **Email**: Email professionnel (unique)
   - **Téléphone**: Numéro de téléphone
   - **Poste**: Intitulé du poste
   - **Date d'embauche**: Date d'arrivée en entreprise
   - **Actif**: Case à cocher pour activer le profil

### Consulter le profil d'un stagiaire

1. Allez à "Stagiaires"
2. Cliquez sur un stagiaire dans la liste
3. Consultez:
   - Les informations personnelles
   - Les formations suivies
   - Les titres obtenus
   - L'historique

### Actions rapides depuis le profil

- **Modifier**: Mettez à jour les informations
- **Nouvelle formation**: Enregistrez une nouvelle formation

---

## 📚 Gestion des formations

### Créer une formation

#### Option 1: Depuis le profil du stagiaire

1. Ouvrez le profil du stagiaire
2. Cliquez sur "Nouvelle formation"
3. Sélectionnez l'habilitation
4. Entrez les dates de début et fin prévues
5. Complétez les informations optionnelles
6. Cliquez sur "Enregistrer"

#### Option 2: Depuis la liste des formations

1. Allez à "Formations"
2. Cliquez sur "Nouvelle formation"
3. Sélectionnez le stagiaire et l'habilitation
4. Entrez les dates
5. Cliquez sur "Enregistrer"

### Statuts de formation

- **En cours**: Formation actuellement en progress
- **Complétée**: Formation terminée avec succès
- **Abandonnée**: Formation arrêtée prématurément

### Modifier une formation

1. Ouvrez la formation
2. Cliquez sur "Modifier"
3. Changez les informations nécessaires
4. Cliquez sur "Enregistrer"

---

## ✅ Validation des compétences

### Valider les compétences

Pour chaque formation, validez les savoirs théoriques et savoir-faire pratiques:

1. Ouvrez la formation
2. Cliquez sur l'onglet "Compétences"
3. Cliquez sur "Valider les compétences"
4. Cochez les compétences validées:
   - **Savoirs théoriques**: Connaissances acquises
   - **Savoir-faire pratiques**: Compétences démontrées
5. Ajoutez des commentaires si nécessaire
6. Cliquez sur "Valider"

### Compétences pour B1V (exemple)

**Savoirs théoriques:**
- Connaissances techniques BT
- Normes et réglementations
- Risques électriques
- Procédures de sécurité

**Savoir-faire pratiques:**
- Utilisation d'équipements de protection
- Réalisation de câblages
- Tests de sécurité
- Mesures électriques

---

## 📋 Avis de formation

### Créer un avis après formation

L'avis est complété par le formateur après la formation:

1. Ouvrez la formation (statut doit être "Complétée")
2. Cliquez sur l'onglet "Avis"
3. Cliquez sur "Créer un avis"
4. Remplissez les champs:
   - **Avis**: Favorable / Favorable avec conditions / Défavorable
   - **Observations**: Commentaires généraux
   - **Points forts**: Ce qui a bien marché
   - **Points d'amélioration**: Ce qui pourrait être mieux
   - **Recommandations**: Conseils pour la suite
   - **Nom du formateur**: Formateur responsable
   - **Signature du formateur**: Upload de la signature (optionnel)
5. Cliquez sur "Enregistrer"

### Avis possibles

- **Favorable** ✅: Le candidat est apte à exercer
- **Favorable avec conditions** ⚠️: Apte sous certaines conditions
- **Défavorable** ❌: N'a pas acquis les compétences

---

## 🏆 Délivrance de titres

### Conditions pour délivrer un titre

- La formation doit être "Complétée"
- Un avis de formation doit avoir été créé
- Les compétences doivent être validées

### Délivrer un titre

1. Ouvrez la formation
2. Cliquez sur l'onglet "Titre"
3. Cliquez sur "Délivrer un titre"
4. Remplissez les champs:
   - **Numéro de titre**: Numéro unique (ex: HAB-2024-0001)
   - **Date de délivrance**: Date du jour
   - **Date d'expiration**: Calculée selon la validité (36 mois par défaut)
   - **Statut**: "Délivré"
   - **Notes**: Observations spéciales
5. Cliquez sur "Enregistrer"

### Format du numéro de titre

Recommandation: `HAB-AAAA-NNNN` où:
- HAB = Habilitation
- AAAA = Année
- NNNN = Numéro séquentiel

Exemples:
- HAB-2024-0001
- HAB-2024-0002
- HAB-2024-0003

---

## 🔄 Gestion des renouvellements

### Alertes de renouvellement

Un titre est signalé pour renouvellement si:
- Il expire dans moins de 90 jours
- Affiche un badge rouge "Expire bientôt"

### Planifier un renouvellement

1. Allez à "Titres d'habilitation"
2. Trouvez le titre qui expire bientôt
3. Cliquez sur "Renouveler"
4. Entrez la "Date de renouvellement prévue"
5. Ajoutez des notes si nécessaire
6. Cliquez sur "Planifier le renouvellement"

### Suivi des renouvellements

1. Allez à "Renouvellements d'habilitations"
2. Consultez le statut:
   - **Planifié**: En attente
   - **En cours**: Formation en cours
   - **Renouvelé**: Titre renouvelé avec succès
   - **Expiré**: Titre expiré

3. Les renouvellements en retard s'affichent en rouge

---

## 📊 Tableau de bord (Dashboard)

Le tableau de bord offre une vue d'ensemble:

### Statistiques principales

- **Total de stagiaires**: Nombre de stagiaires actifs
- **En formation**: Formations en cours
- **Titres valides**: Titres actuellement valides
- **Expiration proche**: Titres expirant dans 90 jours

### Alertes

Les titres expirant bientôt s'affichent dans une alerte rouge avec:
- Nom du stagiaire
- Habilitation
- Date d'expiration

### Formations récentes

Liste des formations complétées récemment avec:
- Stagiaire
- Habilitation
- Date de fin
- Lien vers les détails

### Actions rapides

Boutons rapides pour:
- Créer un nouveau stagiaire
- Voir la liste des stagiaires
- Gérer les formations
- Consulter les titres

---

## 📱 Fonctionnalités avancées

### Recherche

- Recherchez les stagiaires par nom, prénom, email ou poste
- Filtrez les formations par statut
- Consultez les renouvellements planifiés

### Filtrage

- Filtrez les formations par statut (en cours, complétée, abandonnée)
- Triez par date
- Groupez par stagiaire ou habilitation

### Journal d'audit

Toutes les actions sont enregistrées dans le journal:
- Création de stagiaires
- Création de formations
- Validations de compétences
- Délivrance de titres
- Renouvellements

---

## ⚙️ Configuration avancée

### Modifier la durée de validité des titres

1. Allez à http://localhost:8000/admin/
2. Cliquez sur "Habilitations"
3. Sélectionnez une habilitation
4. Modifiez "Durée de validité (mois)"
   - Par défaut: 36 mois (3 ans)
   - Exemple: 24 mois = 2 ans

### Modifier les savoirs et savoir-faire

1. Allez à l'habilitation dans l'admin
2. Modifiez les champs:
   - **Savoirs**: Un par ligne (Ctrl+Entrée pour nouvelle ligne)
   - **Savoir-faire**: Un par ligne

### Ajouter des secrétaires

1. Allez à http://localhost:8000/admin/
2. Cliquez sur "Secrétaires"
3. Cliquez sur "Ajouter une secrétaire"
4. Sélectionnez un utilisateur
5. Sélectionnez l'entreprise
6. Cliquez sur "Enregistrer"

---

## 🔐 Sécurité et recommandations

### Bonnes pratiques

1. **Authentification**: Utilisez des mots de passe forts
2. **Sauvegardes**: Sauvegardez régulièrement la base de données
3. **Mises à jour**: Tenez Django à jour
4. **HTTPS**: Utilisez HTTPS en production
5. **Confidentialité**: Respectez la confidentialité des données personnelles

### En production

1. Changez `DEBUG = False` dans settings.py
2. Définissez une nouvelle `SECRET_KEY`
3. Configurez un serveur de base de données (PostgreSQL)
4. Activez HTTPS et CSRF protection
5. Configurez les emails

---

## 🆘 Dépannage

### Le serveur ne démarre pas

```bash
# Vérifiez que les migrations sont appliquées
python manage.py migrate

# Vérifiez que tous les packages sont installés
pip install -r requirements.txt
```

### Erreur de permission (Permission denied)

```bash
# Modifiez les permissions
chmod -R 755 .
```

### Problème de base de données

```bash
# Supprimez la base de données et recommencez
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 📞 Support et documentation

- Documentation Django: https://docs.djangoproject.com/
- Bootstrap 5: https://getbootstrap.com/
- Crispy Forms: https://django-crispy-forms.readthedocs.io/

## Version

- Django: 4.2.7
- Python: 3.8+
- Bootstrap: 5.3.0

---

**Dernière mise à jour**: Janvier 2026
