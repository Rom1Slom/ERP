# Guide de démarrage rapide

## Installation rapide

```bash
# 1. Créer un environnement virtuel
python -m venv venv

# 2. Activer l'environnement
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer un utilisateur admin
python manage.py createsuperuser

# 6. Charger les données d'exemple (optionnel)
python manage.py shell < fixtures_init.py

# 7. Lancer le serveur
python manage.py runserver
```

## URLs principales

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil |
| `/accounts/login/` | Connexion |
| `/dashboard/` | Tableau de bord |
| `/admin/` | Administration Django |
| `/stagiaires/` | Liste des stagiaires |
| `/formations/` | Liste des formations |
| `/titres/` | Liste des titres |
| `/renouvellements/` | Gestion des renouvellements |

## Premiers pas

1. **Connectez-vous** avec le compte administrateur créé
2. **Accédez à l'admin** (http://localhost:8000/admin/)
3. **Créez une entreprise** avec ses informations
4. **Créez des habilitations** (types de certifications électriques)
5. **Créez des stagiaires** et leurs formations
6. **Validez les compétences** et délivrez les titres

## Données d'exemple

Pour tester rapidement, créez des données:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from habilitations_app.models import Entreprise, Habilitation, Stagiaire
from datetime import date, timedelta

# Créer une entreprise
ent = Entreprise.objects.create(
    nom='EDF',
    email='contact@edf.fr',
    telephone='01 40 42 22 22',
    adresse='22-30 avenue de Wagram',
    code_postal='75382',
    ville='Paris'
)

# Créer une habilitation
hab = Habilitation.objects.create(
    code='B1V',
    nom='Exécution de travaux - Basse Tension',
    categorie='1',
    niveau='Standard',
    duree_validite_mois=36,
    savoirs='Normes de sécurité\nRisques électriques\nProcédures d\'urgence',
    savoirs_faire='Utilisation d\'équipements\nRéalisation de câblages\nTest de sécurité'
)

# Créer un stagiaire
stag = Stagiaire.objects.create(
    entreprise=ent,
    nom='Martin',
    prenom='Paul',
    email='paul.martin@edf.fr',
    telephone='06 12 34 56 78',
    poste='Électricien confirmé',
    date_embauche=date.today()
)

exit()
```

Vous pouvez maintenant explorer l'application avec ces données de test!
