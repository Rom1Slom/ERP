# Architecture B2B2C - Système de Gestion des Habilitations

## 📋 Vue d'ensemble

Cette application suit un modèle **B2B2C** (Business-to-Business-to-Consumer) où :

```
VOUS (Éditeur SaaS)
  │
  ├─ OF #1 (Organisme de Formation - client payant)
  │   ├─ Stagiaires indépendants
  │   ├─ PME A (client gratuit de l'OF)
  │   │   └─ Stagiaires employés
  │   └─ PME B (client gratuit de l'OF)
  │       └─ Stagiaires employés
  │
  └─ OF #2 (Organisme de Formation - client payant)
      ├─ Stagiaires indépendants
      └─ PME X (client gratuit de l'OF)
          └─ Stagiaires employés
```

## 🔑 Rôles utilisateurs

### 1. Super Admin (vous - éditeur SaaS)
- Gestion de tous les organismes de formation (OF)
- Vue globale de la plateforme
- Configuration système
- **Dashboard** : `dashboard_super_admin`

### 2. Admin OF (Organisme de Formation)
- Gestion de ses PME clientes
- Gestion de ses stagiaires indépendants
- Création de sessions de formation
- Validation des formations et délivrance de titres
- Traitement des demandes de formation reçues
- **Dashboard** : `dashboard_admin_of`

### 3. Responsable PME
- Consultation de ses employés stagiaires
- Création de demandes de formation (en 2 clics)
- Suivi des formations en cours
- Alertes d'expiration de titres
- **Dashboard** : `dashboard_responsable_pme`

### 4. Stagiaire
- Consultation de son propre dossier
- Suivi de ses formations
- Consultation de ses titres
- **Dashboard** : `dashboard_stagiaire`

## 🔄 Workflow : Demande de formation

### Étape 1 : Création de la demande (Responsable PME)
1. Le responsable PME se connecte
2. Il voit la liste de ses employés
3. Il clique sur "Demander une formation"
4. Il sélectionne :
   - Le type d'habilitation
   - Les stagiaires concernés
   - Date souhaitée (optionnelle)
   - Commentaire (optionnel)
5. La demande est envoyée à son OF

### Étape 2 : Réception de la demande (Admin OF)
1. L'Admin OF voit la demande dans son tableau de bord
2. Il peut :
   - Approuver → crée une session de formation
   - Refuser → avec commentaire
   - Reporter → garder en attente

### Étape 3 : Création de la session (Admin OF)
1. Si approuvée, l'OF crée une session :
   - Définit les dates
   - Définit le lieu
   - Définit le nombre de places
2. Les stagiaires de la demande sont automatiquement inscrits
3. La PME est notifiée

## 🗄️ Modèles de données principaux

### Entreprise
```python
- type_entreprise: 'of' | 'client' (PME)
- nom, email, téléphone, adresse
- date_creation
```

### Stagiaire
```python
- organisme_formation: FK vers Entreprise (type='of') - OBLIGATOIRE
- entreprise: FK vers Entreprise (type='client') - OPTIONNEL
  * Si NULL → stagiaire indépendant de l'OF
  * Si renseigné → stagiaire employé d'une PME
- nom, prenom, email, telephone
- poste, date_embauche
```

### DemandeFormation (nouveau)
```python
- entreprise_demandeuse: PME qui demande
- organisme_formation: OF qui reçoit la demande
- habilitation: Type d'habilitation demandée
- stagiaires: ManyToMany vers Stagiaire
- statut: 'en_attente' | 'approuvee' | 'refusee' | 'annulee'
- date_souhaitee, commentaire_demande, commentaire_reponse
- session_creee: Session créée si approuvée
```

### ProfilUtilisateur
```python
- role: 'super_admin' | 'admin_of' | 'responsable_pme' | 'stagiaire'
- entreprise: FK vers Entreprise (NULL pour super_admin)
- actif: Boolean
```

## 🔒 Isolation multi-tenant

Le middleware `MultiTenantMiddleware` garantit que :
- Chaque OF ne voit que ses données
- Chaque PME ne voit que ses employés
- Chaque stagiaire ne voit que son dossier
- Le Super Admin voit tout

### Fonctions d'isolation

```python
get_accessible_stagiaires(user)      # Filtre les stagiaires accessibles
get_accessible_entreprises(user)     # Filtre les entreprises accessibles
get_accessible_demandes_formation(user)  # Filtre les demandes accessibles
```

## 🎨 Templates et URLs

### URLs principales

```
/                                    → Redirection selon rôle
/dashboard/super-admin/              → Dashboard Super Admin
/dashboard/admin-of/                 → Dashboard Admin OF
/dashboard/responsable-pme/          → Dashboard Responsable PME
/dashboard/stagiaire/                → Dashboard Stagiaire

/demandes-formation/creer/           → Créer demande (PME)
/demandes-formation/                 → Liste demandes
/demandes-formation/<id>/            → Détail demande
/demandes-formation/<id>/traiter/    → Traiter demande (OF)
/demandes-formation/<id>/creer-session/  → Créer session depuis demande
```

### Templates créés

- `demande_formation_form.html` : Formulaire de création de demande
- `demande_formation_list.html` : Liste des demandes (PME et OF)
- `dashboard_super_admin.html` : À créer
- `dashboard_admin_of.html` : À créer
- `dashboard_responsable_pme.html` : À créer
- `dashboard_stagiaire.html` : À créer

## 📊 Migrations appliquées

Migration `0007_profilutilisateur_actif_and_more` :
- ✅ Ajout champ `organisme_formation` au modèle Stagiaire
- ✅ Modification champ `entreprise` (maintenant optionnel)
- ✅ Création modèle `DemandeFormation`
- ✅ Extension `ProfilUtilisateur` avec nouveaux rôles
- ✅ Ajout champ `actif` au ProfilUtilisateur

## 🚀 Prochaines étapes

1. **Créer les templates de dashboards** :
   - `dashboard_super_admin.html`
   - `dashboard_admin_of.html`
   - `dashboard_responsable_pme.html`
   - `dashboard_stagiaire.html`

2. **Créer les templates manquants** :
   - `demande_formation_detail.html`
   - `traiter_demande_formation.html`
   - `creer_session_from_demande.html`

3. **Configurer l'admin Django** pour les nouveaux modèles

4. **Créer des utilisateurs de test** pour chaque rôle

5. **Tester le workflow complet** :
   - Créer une PME
   - Créer un OF
   - Créer des stagiaires
   - Faire une demande de formation
   - Traiter la demande côté OF

## 💡 Points clés

### Monétisation
- **OF payent** un abonnement mensuel/annuel
- **PME ne payent pas** (gratuites pour les clients des OF)
- **Stagiaires ne payent pas**

### Flexibilité
- Un OF peut avoir :
  - Des stagiaires indépendants (inscrits directement)
  - Des PME clientes avec leurs employés
- Une PME peut demander des formations en 2 clics
- Un OF peut créer des sessions mixtes (stagiaires indépendants + employés de PME)

### Sécurité
- Isolation complète des données par tenant
- Permissions vérifiées à chaque action
- Middleware automatique pour filtrer les données

## 📝 Notes de compatibilité

Anciens noms de rôles conservés pour compatibilité :
- `client` → `responsable_pme`
- `of` → `admin_of`

Les méthodes `est_client` et `est_of` restent fonctionnelles.
