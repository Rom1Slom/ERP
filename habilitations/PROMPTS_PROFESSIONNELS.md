# 📝 Prompts Professionnels - Habilitations

> Archive des prompts utilisés pour développer ce projet  
> **Objectif :** Réutiliser ces patterns pour les prochaines features

---

## Template pour chaque prompt

```markdown
### Titre de la feature
- **Date :** JJ/MM/AAAA
- **Type :** Feature / Bugfix / Refactoring / Architecture
- **Contexte :** [Pourquoi on le fait ?]

**PROMPT BRUT (ce que tu as écrit) :**
```
Ton texte initial
```

**PROMPT PRO (version améliorée) :**
```
Version optimisée avec tous les détails
```

**AMÉLIORATIONS APPORTÉES :**
- Point 1 : Explication
- Point 2 : Explication

**RÉSULTAT :** 
- Fichiers modifiés : [liste]
- Migrations : [si applicable]
- Notes techniques : [points importants]

**APPRENTISSAGES :**
- Ce qu'on a découvert
- Pièges évités
- Bonnes pratiques appliquées
```

---

## 1. Refactoring Architecture Formations Multi-types

- **Date :** 10/01/2026
- **Type :** Architecture / Refactoring majeur
- **Contexte :** Étendre le projet de "Habilitations électriques" à tous types de formations (CACES, Travail en hauteur, AIPR, etc.)

### PROMPT BRUT (initial - gestion formateurs) :
```
Ajouter dans la sidebar de admin_of un champ formateurs qui ouvre un form pour créer ou supprimer des formateurs utilisés par l'OF.
```

### Évolution vers le refactoring complet :
```
Avant de faire la gestion des formateurs, faudrait peut-être faire une modif. On va étendre le projet à toutes sortes de formation. Donc lier un tenant (of) à une liste de formation (Habilitation, Caces, travail en hauteur, ou autre à définir par l'of). Chaque formation aura des sous-champs (B1, B2, BC, H1 etc pour les habilitation, Executant, manager pour l'AIPR etc.)
```

### PROMPT PRO (version finale) :

```markdown
Refactoriser complètement le modèle de formations pour supporter plusieurs types génériques avec spécialisations indépendantes :

**ARCHITECTURE DÉTAILLÉE :**

1. **Modèles de base (remplacer Habilitation)**

   a) Model `TypeFormation`
      - Champs : nom (str), code (str unique), description (text)
      - Exemples : "Habilitation électrique", "CACES", "Travail en hauteur", "AIPR"
      - Un OF propose plusieurs types
   
   b) Model `Specialisation`
      - Champs : type_formation (FK), code (str), nom (str), description (text), duree_validite_mois (int)
      - Exemples :
        * Type "Habilitation" → Codes "B1", "B2", "BC", "BR", "H0", "H1V", etc.
        * Type "CACES" → Codes "Cat1", "Cat3", "Cat5", etc.
        * Type "AIPR" → Codes "Executant", "Manager", "Superviseur"
      - Chaque spécialisation = compétence indépendante traçable

2. **Relations Tenant-Formations**
   
   c) Model `TenantFormation` (M2M optimisée)
      - Champs : tenant (FK), type_formation (FK), spécialisations (M2M Specialisation)
      - La liste des type_formation que l'OF peut choisir est dans un menu déroulant mis à jour par superadmin
      - Permet à chaque OF de choisir : "Je propose Habilitation (B1+B2+BC) mais pas CACES"
      - Exemple : Tenant "Kompetans" → TypeFormation "Habilitation" + Spécialisations [B1, B2, BC, BR]

3. **Formateurs - Compétences par spécialisation**
   
   d) Model `FormateurCompetence` (M2M)
      - Champs : formateur_profil (FK ProfilUtilisateur, role='formateur'), 
                 specialisation (FK), 
                 actif (bool), 
                 date_ajout (datetime)
      - Permet d'assigner chaque spécialisation individuellement
      - Exemple : Formateur "Alice" → Peut faire [Habilitation-B1, Habilitation-B2] mais PAS [Habilitation-BC]

4. **SessionFormation - Support multi-spécialisation**
   
   e) Modifier SessionFormation
      - Remplacer champ `habilitation` (FK) par `type_formation` (FK)
      - Ajouter `spécialisations` (M2M vers Specialisation)
      - Exemple : Session "Formation Électrique Janvier 2026" → Type "Habilitation", Spécialisations [B1, B2, BR]
      - Champ `formateur` (FK User) : Vérifier qu'il a les compétences pour TOUS les spécialisations de la session

5. **DemandeStagiaire/Titre/ValidationCompetence - Adaptation**
   
   f) DemandeStagiaire
      - Remplacer `habilitation` par `type_formation` + `specialisation`
      - Exemple : Demande "Stagiaire X veut faire Habilitation B1"
      - SIMPLIFICATION : DemandeStagiaire = UNIQUEMENT stagiaires indépendants (pas d'entreprise)
   
   g) ValidationCompetence
      - Remplacer `habilitation` par `specialisation` (FK directe)
      - Permet validation indépendante par spécialisation
   
   h) Titre
      - Remplacer `habilitation` par `specialisation`
      - Un titre = certification d'une spécialisation unique

6. **MIGRATION - Zéro rupture**
   
   i) Data migration Django
      - Créer TypeFormation "Habilitation électrique" automatiquement
      - Migrer chaque Habilitation existante → Specialisation du type "Habilitation"
      - Garder les IDs pour ne pas casser les FK existantes (nullable temporaire)
      - Vérifier : SessionFormation, DemandeStagiaire, Titre pointent aux bonnes Specialisation
   
   j) Compatibilité
      - Créer une view de translation : ancienne Habilitation → nouvelle Specialisation
      - Tests pour vérifier zéro donnée perdue

**CONSIDÉRATIONS IMPORTANTES :**
- Un formateur peut être inactif sur une spécialisation mais actif sur une autre
- Une session doit vérifier que son formateur maîtrise TOUTES ses spécialisations
- L'export de titres doit fonctionner avec la nouvelle structure
- Les filtres/recherches doivent marcher sur type_formation + specialisation
```

### AMÉLIORATIONS APPORTÉES :

| Brut | Pro | Pourquoi ? |
|------|-----|------------|
| "Ajouter formateurs" | Architecture complète multi-types | Identifier la dépendance avant de coder |
| Aucun détail modèles | 4 nouveaux modèles détaillés | Architecture scalable |
| Pas de migration | Plan migration + zéro rupture | Pas de perte de données |
| Flou sur "formations" | Distinction Type vs Specialisation | Granularité précise |
| Pas de validation | Validation formateur/compétences | Sécurité métier |

### RÉSULTAT :

**Fichiers modifiés :**
- `models.py` : 4 nouveaux modèles + 4 modèles modifiés
- `forms.py` : Import Specialisation, adaptation DemandeStagiaireForm
- `admin.py` : Adaptation DemandeStagiaireAdmin
- `migrations/` : 0011_*.py + 0012_add_indexes.py

**Nouveaux modèles créés :**
- `TypeFormation` : Catégories de formations (Habilitation, CACES, etc.)
- `Specialisation` : Sous-catégories (B1, B2, Cat1, Executant, etc.)
- `TenantFormation` : Lien OF → Formations proposées
- `FormateurCompetence` : Lien Formateur → Spécialisations maîtrisées

**Modèles modifiés :**
- `Habilitation` : Marqué LEGACY, ajout champ `specialisation_liee`
- `ValidationCompetence` : Ajout FK `specialisation`
- `Titre` : Ajout FK `specialisation`, `habilitation` devient optionnel
- `SessionFormation` : Ajout FK `type_formation` + M2M `spécialisations`, méthode `formateur_has_competences()`
- `DemandeStagiaire` : Ajout FK `type_formation` + M2M `spécialisations_demandees`, suppression champs `entreprise`, `poste`, `date_embauche`

**Migrations Django :**
```bash
python manage.py makemigrations
python manage.py migrate
# Note : Fix manuel migration 0011 (déplacer AddIndex après AddField)
```

### APPRENTISSAGES :

1. **Identifier les dépendances architecturales AVANT de coder**
   - Vouloir faire "gestion formateurs" → Découvrir besoin refactoring formations
   - Meilleur workflow : Architecture d'abord, features ensuite

2. **Simplification des modèles**
   - DemandeStagiaire : 2 cas d'usage → simplifié à 1 seul (indépendants)
   - DemandeFormation gère les salariés d'entreprise (1 ou plusieurs)
   - Plus clair, moins de confusion

3. **Migrations Django complexes**
   - Ordre des opérations important : AddField AVANT AddIndex
   - Pour refactoring majeur : supprimer BD + recréer proprement
   - Éditer manuellement la migration si nécessaire

4. **Patterns réutilisables**
   - M2M "through" pour granularité (FormateurCompetence)
   - Champs legacy nullable pour migration progressive
   - Méthodes de validation métier (@property, méthodes custom)

5. **Django Meta class**
   - `ordering` : Tri par défaut des requêtes
   - `indexes` : Performance sur combinaisons de champs
   - `unique_together` : Contraintes d'unicité multi-champs
   - `verbose_name` : Noms "humains" pour l'admin

---

## 2. Catalogue des Formations - Gestion des Spécialisations Multiples

- **Date :** 13/01/2026
- **Type :** Bugfix / Architecture
- **Contexte :** Corriger la logique d'ajout de formations au catalogue pour permettre plusieurs combinaisons Type+Spécialisations
- **Statut :** ✅ Implémenté

### PROMPT BRUT (initial) :
```
Sidebar / Renommer la section "Gérer les formations" par "Ajouter/Modifier une formation" :
L'ajout d'une formation dont le type est le meme qu'une formation existante mais pas la spécialisation ne devrait pas écraser la formation de meme type actuellement au catalogue. Deux ou plusieurs formations de meme type peuvent coexister pour peu que la spécialisation diffèrent.
```

### PROMPT PRO (version améliorée) :

```markdown
Corriger le système de gestion du catalogue de formations pour permettre plusieurs combinaisons Type+Spécialisations distinctes :

**PROBLÈME IDENTIFIÉ :**

1. **Architecture actuelle défectueuse**
   - `TenantFormation` a `unique_together = ('tenant', 'type_formation')`
   - Empêche un OF de proposer plusieurs spécialisations différentes du MÊME type de formation
   - Exemple BLOQUÉ : OF veut proposer "Habilitation B1+B2" ET "Habilitation BC+BR" séparément
   - Comportement actuel : Le 2e ajout ÉCRASE le 1er (remplace les spécialisations au lieu d'en créer une nouvelle)

2. **Cas d'usage métier**
   - Un OF peut vouloir organiser des sessions DIFFÉRENTES pour différentes spécialisations du même type
   - Session 1 : "Habilitation niveau basique" → [B1, B2]
   - Session 2 : "Habilitation niveau avancé" → [BC, BR, H1V]
   - Chaque session = tarif différent, durée différente, formateurs différents

**SOLUTION PROPOSÉE :**

1. **Refactoriser TenantFormation**
   
   a) **Supprimer la contrainte `unique_together`**
      - Permettre plusieurs entrées `TenantFormation` avec même `tenant` + `type_formation`
      - Différencier par leurs `spécialisations` (M2M)
   
   b) **Ajouter un champ descriptif optionnel**
      - `nom_package` (CharField, nullable) : Ex. "Pack Basique", "Pack Complet"
      - Permet à l'OF de nommer ses différentes offres de formation
   
   c) **Nouvelle contrainte unique**
      - Empêcher EXACTEMENT la même combinaison : même tenant + même type + mêmes spécialisations
      - Impossible à faire avec `unique_together` (ne marche pas avec M2M)
      - Solution : Validation au niveau de la vue (avant `save()`)

2. **Adapter la vue `catalogue_formations_add`**
   
   a) **Logique modifiée**
      ```python
      # AVANT (bugué) :
      tenant_form, created = TenantFormation.objects.get_or_create(
          tenant=tenant,
          type_formation=type_formation,  # ← Écrase si existe déjà
          defaults={'actif': True}
      )
      
      # APRÈS (corrigé) :
      # Vérifier si EXACTEMENT cette combinaison existe déjà
      existing = TenantFormation.objects.filter(
          tenant=tenant,
          type_formation=type_formation
      )
      
      # Filtrer par spécialisations identiques (si spécialisations fournies)
      if specialisations_ids:
          for tf in existing:
              if set(tf.spécialisations.values_list('id', flat=True)) == set(specialisations_ids):
                  # Combinaison identique déjà existante
                  return JsonResponse({
                      'success': False,
                      'errors': {'global': ['Cette formation avec ces spécialisations existe déjà']}
                  }, status=400)
      
      # Créer NOUVELLE entrée (pas de get_or_create)
      tenant_form = TenantFormation.objects.create(
          tenant=tenant,
          type_formation=type_formation,
          actif=True
      )
      
      # Assigner spécialisations
      if specialisations.exists():
          tenant_form.spécialisations.set(specialisations)
      ```
   
   b) **Validation supplémentaire**
      - Si aucune spécialisation sélectionnée : refuser (sauf types sans spécialisations)
      - Message d'erreur clair : "Sélectionnez au moins une spécialisation"

3. **Adapter l'affichage du catalogue (dashboard admin_of)**
   
   a) **Grouper visuellement par TypeFormation**
      ```html
      <h4>Habilitation électrique</h4>
      <ul>
        <li>Pack Basique (B1, B2) — Actif — [Modifier] [Désactiver]</li>
        <li>Pack Complet (BC, BR, H1V) — Actif — [Modifier] [Désactiver]</li>
      </ul>
      
      <h4>CACES</h4>
      <ul>
        <li>Cat 1, Cat 3 — Actif — [Modifier] [Désactiver]</li>
      </ul>
      ```
   
   b) **Badge pour différencier**
      - Afficher spécialisations sous forme de badges Bootstrap
      - Indiquer nombre de sessions liées à chaque combinaison

4. **Renommer UI**
   - Sidebar : "Gérer les formations" → **"Catalogue de formations"**
   - Bouton : "Ajouter formation" → **"Ajouter une offre"**
   - Plus clair sémantiquement

**MODÈLES CONCERNÉS :**
- `TenantFormation` : Supprimer `unique_together`, ajouter `nom_package`
- `views_catalogue.py` : Logique `catalogue_formations_add()`
- `templates/dashboard_admin_of.html` : Affichage groupé

**TESTS À VALIDER :**
- Ajouter "Habilitation [B1, B2]" → OK
- Ajouter "Habilitation [BC, BR]" → OK (nouvelle entrée)
- Ajouter "Habilitation [B1, B2]" à nouveau → ERREUR (doublon exact)
- Modifier spécialisations d'une offre existante → OK
```

### AMÉLIORATIONS APPORTÉES :

| Brut | Pro | Pourquoi ? |
|------|-----|------------|
| "ne devrait pas écraser" | Analyse du problème racine (`unique_together`) | Comprendre la cause technique |
| Pas de solution proposée | Solution complète avec code | Actionable immédiatement |
| UI vague | Renommage précis + wireframes HTML | UX claire |
| Pas de tests | Scénarios de validation | Éviter régressions |

---

## 3. Gestion des Formateurs (EN ATTENTE)

- **Date :** 10/01/2026
- **Type :** Feature
- **Contexte :** Permettre aux admin_of de gérer leurs formateurs et leurs compétences
- **Statut :** ⏸️ En pause - Architecture formations faite en prérequis

### PROMPT PRO (préparé) :

```markdown
Ajouter une section "Gestion des formateurs" dans le dashboard admin_of avec :

1. **Affichage des formateurs existants**
   - Liste des users avec `ProfilUtilisateur.role='formateur'` assignés à l'OF courant
   - Afficher : nom, email, statut actif/inactif
   - Bouton supprimer (avec confirmation) = Changer le rôle à inactif ou supprimer le profil
   - Pour chaque formateur : bouton "Modifier" → lien vers formulaire

2. **Formulaire d'ajout/modification de formateur**
   - **Option A (Ajout) :** Sélectionner un user existant OÙ créer un nouveau (nom, email, téléphone)
   - **Modification :** Pré-remplir les infos, pouvoir changer email/phone
   - Validation : Vérifier que le user n'a pas déjà le rôle 'formateur' pour cet OF
   - Assigner automatiquement `ProfilUtilisateur(user=..., role='formateur', entreprise=OF_courant, tenant=tenant_courant)`
   - **IMPORTANT** Assigner les formations qu'il peut dispenser :
     * Afficher toutes les spécialisations proposées par l'OF actuel
     * Cases à cocher pour chaque spécialisation
     * Créer les liens `FormateurCompetence` pour mémoriser les compétences du formateur

3. **Intégration dans l'interface**
   - **Sidebar:** Ajouter un lien "Formateurs" à côté de "Entreprises" et "Sessions"
   - Au clic : Afficher modal OU page avec la liste + bouton "Ajouter formateur"
   - Utiliser design Bootstrap cohérent (badges, boutons, icônes)
   - Permission : Accessible uniquement à `est_admin_of` et `est_secretariat`

4. **Backend (vues & logique)**
   - Créer une view GET pour afficher liste formateurs + formulaire
   - Créer une view POST pour ajouter/modifier formateur
   - Créer une view POST pour supprimer formateur (soft-delete = set inactif)
   - Filtrer strictement par `tenant` et/ou `entreprise` courants
   - Vérifier permissions à chaque requête : `est_admin_of or est_secretariat`
   - Gérer les FormateurCompetence (M2M)

**Modèles existants à utiliser :**
- `ProfilUtilisateur` : champ `role`, propriétés `est_formateur`, `est_admin_of`
- `SessionFormation` : champ `formateur` (FK User), méthode `formateur_has_competences()`
- `Specialisation` : Liste des spécialisations de l'OF
- `FormateurCompetence` : Lien formateur → spécialisations maîtrisées
```

**À implémenter quand architecture formations sera testée.**

---

## Prochains Prompts à Archiver

- [ ] Gestion des formateurs (sidebar admin_of)
- [ ] Système de notifications (titres expirant bientôt)
- [ ] Export PDF des titres
- [ ] Dashboard analytics
- [ ] API REST pour intégration externe

---

## 💡 Tips pour écrire des prompts pro

1. **Contexte d'abord** : Pourquoi on fait ça ?
2. **Détails techniques** : Modèles, champs, relations
3. **Contraintes** : Permissions, validations, sécurité
4. **Intégration** : Où ça va, design à respecter
5. **Backend** : Vues, logique métier, tests

**Pattern "CSIR" :**
- **C**ontexte : Problème à résoudre
- **S**tructure : Architecture/modèles
- **I**ntégration : UI/UX, design
- **R**ésultat : Validation, tests, edge cases
