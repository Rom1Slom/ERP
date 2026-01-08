# Application Django - Gestion des Habilitations Électriques

Système de gestion complet pour les qualifications et certifications électriques en entreprise, permettant de gérer les stagiaires, formations, validation de compétences et délivrance de titres d'habilitation.

## Fonctionnalités principales

### 👥 Gestion des Stagiaires
- Création et modification des profils stagiaires
- Suivi des informations personnelles et professionnelles
- Gestion des postes et dates d'embauche
- Historique des formations et titres

### 📚 Suivi des Formations
- Enregistrement des formations à suivre
- Gestion des statuts (en cours, complétée, abandonnée)
- Intégration avec Kompetans.fr
- Calendrier de formation

### ✅ Validation des Compétences
- Validation des savoirs théoriques
- Validation des savoir-faire pratiques
- Suivi par compétence
- Commentaires des validateurs
- Avis de formation après la formation

### 🏆 Délivrance de Titres
- Génération automatique des numéros de titre
- Gestion des dates de validité
- Statut des titres (délivré, expiré)
- Export des titres

### 🔄 Gestion des Renouvellements
- Planification des renouvellements
- Alertes pour les titres expirant bientôt (90 jours)
- Suivi des renouvellements en retard
- Historique des renouvellements

### 📊 Tableau de bord
- Vue d'ensemble des statistiques
- Alertes sur les titres expirant
- Formations récentes
- Actions rapides

### 👨‍💼 Gestion des utilisateurs
- Authentification sécurisée
- Rôles (admin, secrétaire, formateur)
- Permissions basées sur l'entreprise
- Journal des actions

## Prérequis

- Python 3.8+
- pip
- Virtual Environment (recommandé)

## Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv
```

### 2. Activer l'environnement virtuel

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations

```bash
python manage.py migrate
```

### 5. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte administrateur.

### 6. Lancer le serveur de développement

```bash
python manage.py runserver
```

L'application sera disponible à l'adresse: `http://127.0.0.1:8000/`

## Accès à l'application

### Page d'accueil
http://127.0.0.1:8000/

### Connexion
http://127.0.0.1:8000/accounts/login/

### Tableau de bord (après connexion)
http://127.0.0.1:8000/dashboard/

### Admin Django
http://127.0.0.1:8000/admin/

## Structure du projet

```
habilitations/
├── habilitations_app/          # Application principale
│   ├── models.py              # Modèles de données
│   ├── views.py               # Vues et logique métier
│   ├── forms.py               # Formulaires
│   ├── admin.py               # Configuration admin
│   └── urls.py                # Routage d'URLs
├── config/                     # Configuration Django
│   ├── settings.py            # Paramètres du projet
│   ├── urls.py                # URLs principales
│   └── wsgi.py                # Configuration WSGI
├── templates/                  # Templates HTML
├── static/                     # Fichiers statiques (CSS, JS, images)
├── media/                      # Fichiers uploadés
├── manage.py                   # Gestionnaire Django
└── requirements.txt           # Dépendances Python
```

## Modèles de données

### Entreprise
- Informations de l'entreprise
- Coordonnées

### Stagiaire
- Informations personnelles
- Poste occupé
- Historique d'emploi

### Habilitation
- Types et codes d'habilitations électriques
- Savoirs théoriques requis
- Savoir-faire pratiques requis
- Durée de validité

### Formation
- Lien entre stagiaire et habilitation
- Dates de formation
- Statut (en cours, complétée, abandonnée)
- Notes

### ValidationCompetence
- Validation des compétences par formation
- Savoirs et savoir-faire
- Validateur et date de validation

### Titre
- Titre d'habilitation délivré
- Numéro unique
- Dates de validité
- Statut

### AvisFormation
- Avis après formation
- Observations du formateur
- Recommandations

### RenouvellementHabilitation
- Planification des renouvellements
- Suivi des renouvellements
- Alertes de retard

### Secretaire
- Gestion des secrétaires autorisés
- Permissions

### Journal
- Journal d'audit de toutes les actions
- Traçabilité complète

## Utilisation

### 1. Créer une entreprise
Accédez à l'admin Django et créez une entreprise.

### 2. Créer des stagiaires
- Allez à "Stagiaires" > "Nouveau stagiaire"
- Remplissez les informations personnelles

### 3. Créer des formations
- Ouvrez le profil d'un stagiaire
- Cliquez sur "Nouvelle formation"
- Sélectionnez l'habilitation et les dates

### 4. Valider les compétences
- Ouvrez une formation
- Cliquez sur "Compétences"
- Validez chaque savoir et savoir-faire

### 5. Créer un avis de formation
- Ouvrez une formation
- Cliquez sur "Avis"
- Complétez le formulaire d'avis

### 6. Délivrer un titre
- Complétez d'abord la formation
- Cliquez sur "Titre"
- Remplissez les informations du titre

### 7. Gérer les renouvellements
- Un titre expirant en moins de 90 jours affiche une alerte
- Cliquez sur "Renouveler"
- Planifiez la date de renouvellement

## Configuration

### Modification des paramètres

Éditez `config/settings.py` pour:

- **SECRET_KEY**: Changez en production
- **DATABASES**: Configurez votre base de données
- **LANGUAGE_CODE**: Langue par défaut
- **TIME_ZONE**: Fuseau horaire

### Email

Par défaut, l'application affiche les emails dans la console. Pour configurer un vrai serveur SMTP:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre@email.com'
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe'
```

## Données de test

Pour créer des données de test, créez un script:

```python
# test_data.py
from django.contrib.auth.models import User
from habilitations_app.models import Entreprise, Habilitation, Stagiaire

# Créer une entreprise
entreprise = Entreprise.objects.create(
    nom='ACME Corp',
    email='contact@acme.fr',
    telephone='01 23 45 67 89',
    adresse='123 rue de la Paix',
    code_postal='75000',
    ville='Paris'
)

# Créer une habilitation
habilitation = Habilitation.objects.create(
    code='B1V',
    nom='Exécution de travaux',
    categorie='1',
    niveau='Standard',
    savoirs='...',
    savoirs_faire='...'
)

# Créer un stagiaire
stagiaire = Stagiaire.objects.create(
    entreprise=entreprise,
    nom='Dupont',
    prenom='Jean',
    email='jean@example.com',
    telephone='06 12 34 56 78',
    poste='Électricien',
    date_embauche='2023-01-01'
)
```

Puis exécutez:
```bash
python manage.py shell
exec(open('test_data.py').read())
```

## Sécurité

- Utiliser HTTPS en production
- Mettre à jour la SECRET_KEY
- Configurer ALLOWED_HOSTS
- Utiliser des bases de données sécurisées
- Garder Django à jour

## Support et documentation

- [Documentation Django](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)
- [Crispy Forms](https://django-crispy-forms.readthedocs.io/)

## Licence

MIT License

## Auteur

Application de gestion des habilitations électriques.

## Roadmap

- [x] Gestion des stagiaires
- [x] Suivi des formations
- [x] Validation des compétences
- [x] Délivrance de titres
- [x] Alertes de renouvellement
- [ ] Export PDF des titres
- [ ] Intégration PDF pour avis de formation
- [ ] Export Excel des données
- [ ] API REST
- [ ] Application mobile
- [ ] Calendrier de formations
- [ ] Rapports avancés
- [ ] Intégration avec systèmes RH
