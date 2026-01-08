# Guide des Rôles et Authentification

## Vue d'ensemble

L'application supporte maintenant **2 rôles distincts** :

1. **Client** - Entreprises clientes de Kompetans
2. **OF** (Organisme de Formation) - Les prestataires de formation

## Architecture

### Modèles

#### Entreprise
- `type_entreprise`: Définit si c'est un `client` ou un `of`
- Chaque entreprise peut avoir plusieurs utilisateurs avec des rôles différents

#### ProfilUtilisateur
- Lie un utilisateur Django à une entreprise
- Contient le `role` : `client` ou `of`
- Propriétés utiles:
  - `est_client`: Retourne `True` si le rôle est 'client'
  - `est_of`: Retourne `True` si le rôle est 'of'

### Authentification

#### Flux de connexion

```
Connexion (ID + mot de passe)
         ↓
CustomLoginView (vérifie le rôle)
         ↓
┌────────┴────────┐
│                 │
v                 v
Client          OF
│                 │
v                 v
dashboard_client  dashboard_of
(gestion salariés) (validation formations)
```

#### Points d'entrée
- **Connexion**: `/accounts/login/`
- **Dashboard Client**: `/dashboard/client/`
- **Dashboard OF**: `/dashboard/of/`
- **Accueil**: `/` (redirige automatiquement selon le rôle)

### Vues et Décorateurs

#### Décorateurs disponibles

```python
from habilitations_app.decorators import (
    client_required,
    of_required,
    ClientRequiredMixin,
    OFRequiredMixin
)

# Pour les fonctions
@client_required
def ma_vue_client(request):
    pass

# Pour les classes
class MaVueClient(ClientRequiredMixin, ListView):
    pass
```

## Cas d'usage

### Client

**Ce qu'il peut faire:**
- ✓ Ajouter/modifier/supprimer des salariés
- ✓ Consulter les formations de ses salariés
- ✓ Consulter les habilitations/titres
- ✓ Soumettre des demandes de formation
- ✓ Suivre l'état des demandes

**Accès restreint:**
- ✗ Impossible de créer des sessions de formation
- ✗ Impossible de valider des avis de formation
- ✗ Impossible de gérer les demandes d'autres clients

### OF (Organisme de Formation)

**Ce qu'il peut faire:**
- ✓ Créer/modifier des sessions de formation
- ✓ Valider les avis de formation
- ✓ Traiter les demandes de formation
- ✓ Assigner les stagiaires à des sessions
- ✓ Consulter les formations complétées

**Accès restreint:**
- ✗ Impossible de créer des salariés (les clients le font)
- ✗ Impossible de modifier les données clients
- ✗ Impossible de voir d'autres OF

## Configuration

### Créer un utilisateur Client

1. Accédez à `/admin/`
2. Créez une `Entreprise` avec `type_entreprise = 'client'`
3. Créez un `User` Django
4. Créez un `ProfilUtilisateur`:
   - `user`: Sélectionnez l'utilisateur créé
   - `entreprise`: Sélectionnez l'entreprise client
   - `role`: Sélectionnez `'client'`

### Créer un utilisateur OF

1. Accédez à `/admin/`
2. Créez une `Entreprise` avec `type_entreprise = 'of'`
   - Exemple: "Kompetans.fr"
3. Créez un `User` Django
4. Créez un `ProfilUtilisateur`:
   - `user`: Sélectionnez l'utilisateur créé
   - `entreprise`: Sélectionnez l'entreprise OF
   - `role`: Sélectionnez `'of'`

## Menu contextuel

Le menu de navigation s'adapte automatiquement selon le rôle:

**Pour un Client:**
- Dashboard
- SALARIÉS (Consulter, Ajouter)
- SUIVI (Formations, Habilitations, Renouvellements)
- DEMANDES (Nouvelle demande, Mes demandes)

**Pour un OF:**
- Dashboard
- SESSIONS (Sessions, Créer session)
- VALIDATION (Formations à valider, Demandes en attente)
- RÉFÉRENCE (Habilitations délivrées)

## Messages d'erreur

- **"Accès réservé aux clients."** - Tentative d'accès Client par un OF
- **"Accès réservé aux organismes de formation."** - Tentative d'accès OF par un Client
- **"Profil utilisateur non configuré."** - L'utilisateur n'a pas de ProfilUtilisateur

## Fichiers clés

- **[models.py](habilitations_app/models.py)**: Modèles `Entreprise`, `ProfilUtilisateur`
- **[views.py](habilitations_app/views.py)**: `CustomLoginView`, `dashboard_client`, `dashboard_of`
- **[decorators.py](habilitations_app/decorators.py)**: Décorateurs et mixins de rôles
- **[base.html](templates/habilitations_app/base.html)**: Menu contextuel
- **[dashboard_client.html](templates/habilitations_app/dashboard_client.html)**: Dashboard Client
- **[dashboard_of.html](templates/habilitations_app/dashboard_of.html)**: Dashboard OF

## Prochaines améliorations

- [ ] Ajouter des tests unitaires pour les décorateurs
- [ ] Implémenter des permissions granulaires (Django Permissions)
- [ ] Ajouter des logs d'audit pour les actions sensibles
- [ ] Implémenter des restrictions au niveau des vues API (si REST API)
- [ ] Ajouter des templates d'erreur personnalisés par rôle
