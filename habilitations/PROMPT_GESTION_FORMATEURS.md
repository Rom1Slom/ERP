# Prompt Professionnel : Gestion des Formateurs (Multi-OF)

## 🎯 Contexte du Besoin

**Demande initiale** : "Ajouter dans la sidebar de admin_of un champ formateurs"

**Architecture existante** :
- Application Django B2B2C : SuperAdmin → OF → PME → Stagiaires
- Système de rôles : super_admin, admin_of, secretariat, formateur, responsable_pme, stagiaire
- Architecture multi-tenant avec modèles Tenant, Entreprise, ProfilUtilisateur
- Système de formations avec TypeFormation, Specialisation, TenantFormation
- SessionFormation avec formateurs M2M (refactoring récent)

---

## 📋 Prompt Professionnel à Utiliser

```
Je développe une application Django de gestion de formations B2B2C avec architecture multi-tenant.

CONTEXTE TECHNIQUE :
- Django 4.2.7 avec architecture multi-tenant (Tenant, Entreprise, ProfilUtilisateur)
- Modèles existants :
  * ProfilUtilisateur (OneToOne avec User, champ role, FK entreprise, FK tenant)
  * SessionFormation (FK tenant, M2M formateurs, M2M spécialisations)
  * TypeFormation/Specialisation (types de formations et leurs variantes)
  * TenantFormation (M2M avec related_name='propositions_of' pour les spécialisations proposées par chaque OF)
- Rôles : super_admin, admin_of, secretariat, formateur, responsable_pme, stagiaire
- Permissions : Decorateur @role_required(['admin_of', 'secretariat'])
- Templates : base.html avec {% block page_content %}, Bootstrap 5

BESOIN :
Implémenter un système CRUD de gestion des formateurs pour les rôles admin_of et secretariat, avec les fonctionnalités suivantes :
1. Un formateur peut être affecté à PLUSIEURS Organismes de Formation (relation M2M)
2. Un formateur a des compétences (spécialisations qu'il peut enseigner)
3. Seules les spécialisations proposées par l'OF courant (via TenantFormation) doivent être sélectionnables
4. Système de soft-delete avec champ actif sur ProfilUtilisateur, FormateurAffectation, et FormateurCompetence
5. Interface accessible depuis la sidebar admin_of

ARCHITECTURE SOUHAITÉE :
- Service layer (services.py) pour logique métier
- Views modulaires (views_formateurs.py)
- Forms avec validation (FormateurForm + FormateurCompetencesForm)
- Templates Bootstrap 5 (formateurs_list.html, formateur_form.html)

CONTRAINTES IMPORTANTES :
- Les QuerySet doivent filtrer par tenant pour respect du multi-tenant
- FormateurAffectation avec unique_together (formateur, entreprise)
- FormateurCompetence avec unique_together (formateur_profil, specialisation)
- Utiliser related_name='propositions_of' pour accéder aux TenantFormation depuis Specialisation
- Les templates doivent utiliser {% block page_content %} et non {% block content %}
- Filtrer par tenant dans SessionFormation (pas organisme_formation qui a été supprimé)

LIVRABLES ATTENDUS :
1. Modèles : FormateurAffectation avec gestion multi-OF
2. Services : formateurs_of(entreprise), specialisations_proposees_of(entreprise), sync_formateur_competences()
3. Formulaires : FormateurForm (création user OU sélection existant), FormateurCompetencesForm (checkboxes spécialisations)
4. Vues : formateurs_list, formateur_edit (create/update), formateur_toggle (actif/inactif)
5. URLs : 4 routes sous /dashboard/admin-of/formateurs/
6. Templates : Liste avec badges Bootstrap, formulaire avec fieldsets
7. Sidebar : Lien dans section FORMATEUR

ERREURS À ÉVITER :
- Ne pas utiliser 'tenantformation' mais 'propositions_of' pour le related_name
- Ne pas utiliser {% block content %} mais {% block page_content %}
- Ne pas filtrer SessionFormation par organisme_formation (champ supprimé, utiliser tenant)
- Ne pas oublier unique_together pour éviter doublons
- Ne pas oublier le decorateur @transaction.atomic pour les opérations multi-modèles
```

---

## 🏗️ Architecture Implémentée

### 1. Modèles (models.py)

```python
class FormateurAffectation(models.Model):
    """
    Permet à un formateur de travailler pour PLUSIEURS OF
    Soft-delete avec champ actif pour historique
    """
    formateur = models.ForeignKey('ProfilUtilisateur', on_delete=models.CASCADE, related_name='affectations')
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='formateurs_affectes')
    date_debut_affectation = models.DateField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('formateur', 'entreprise')
        verbose_name = "Affectation formateur"

# FormateurCompetence (déjà existant, modifié pour actif=True)
# SessionFormation.formateurs M2M vers ProfilUtilisateur (limit_choices_to={'role': 'formateur'})
```

### 2. Service Layer (services.py)

```python
def formateurs_of(entreprise):
    """Retourne formateurs actifs affectés à l'OF"""
    return ProfilUtilisateur.objects.filter(
        role='formateur',
        affectations__entreprise=entreprise,
        affectations__actif=True,
        actif=True
    ).distinct()

def specialisations_proposees_of(entreprise):
    """Retourne spécialisations proposées par l'OF via TenantFormation"""
    tenant = getattr(entreprise, 'tenant_of', None)
    if not tenant:
        return Specialisation.objects.none()
    return Specialisation.objects.filter(
        propositions_of__tenant=tenant,  # ⚠️ related_name, pas 'tenantformation'
        propositions_of__actif=True
    ).distinct()

def sync_formateur_competences(formateur_profil, specialisations_qs):
    """
    Synchronise compétences : active sélectionnées, désactive autres
    Retourne dict {'added': [], 'updated': [], 'deactivated': []}
    """
    # get_or_create + update actif
```

### 3. Formulaires (forms.py)

```python
class FormateurForm(forms.Form):
    user_id = forms.ModelChoiceField(
        queryset=User.objects.filter(profil__role='formateur'),
        required=False,
        empty_label="-- Créer un nouvel utilisateur --"
    )
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    telephone = forms.CharField(required=False)
    actif = forms.BooleanField(required=False, initial=True)
    
    def clean(self):
        # Validation XOR : user_id OU (first_name + last_name + email)
        # Lever ValidationError si les deux ou aucun

class FormateurCompetencesForm(forms.Form):
    spécialisations = forms.ModelMultipleChoiceField(
        queryset=Specialisation.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    def __init__(self, *args, specialisations_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        if specialisations_qs:
            self.fields['spécialisations'].queryset = specialisations_qs
```

### 4. Vues (views_formateurs.py)

```python
@login_required
@role_required(['admin_of', 'secretariat'])
def formateurs_list(request):
    profil = request.user.profil
    formateurs = formateurs_of(profil.entreprise)
    return render(request, 'habilitations_app/formateurs_list.html', {
        'formateurs': formateurs,
        'of': profil.entreprise
    })

@login_required
@role_required(['admin_of', 'secretariat'])
def formateur_edit(request, pk=None):
    # GET/POST avec FormateurForm + FormateurCompetencesForm
    # transaction.atomic():
    #   - Créer/récupérer User
    #   - Créer/mettre à jour ProfilUtilisateur (role='formateur')
    #   - Créer/mettre à jour FormateurAffectation
    #   - sync_formateur_competences()

@login_required
@role_required(['admin_of', 'secretariat'])
def formateur_toggle(request, pk):
    # POST : basculer actif sur ProfilUtilisateur + FormateurAffectation + FormateurCompetence
```

### 5. URLs (urls.py)

```python
from . import views_formateurs

urlpatterns += [
    path('dashboard/admin-of/formateurs/', views_formateurs.formateurs_list, name='formateurs_list'),
    path('dashboard/admin-of/formateurs/new/', views_formateurs.formateur_edit, name='formateur_create'),
    path('dashboard/admin-of/formateurs/<int:pk>/edit/', views_formateurs.formateur_edit, name='formateur_edit'),
    path('dashboard/admin-of/formateurs/<int:pk>/toggle/', views_formateurs.formateur_toggle, name='formateur_toggle'),
]
```

### 6. Templates

**formateurs_list.html** :
- Table Bootstrap avec colonnes : Nom, Email, Statut (badge), Spécialisations (badges limités à 10)
- Actions : Modifier, Activer/Désactiver
- {% block page_content %} ⚠️ PAS {% block content %}

**formateur_form.html** :
- Fieldset 1 : Sélection utilisateur existant OU création nouveau
- Fieldset 2 : Checkboxes spécialisations (boucle sur comp_form.spécialisations.field.choices)
- Checkbox actif
- Affichage form.non_field_errors

---

## 🐛 Problèmes Rencontrés et Solutions

### Problème 1 : FieldError "Cannot resolve keyword 'organisme_formation'"

**Erreur** :
```
django.core.exceptions.FieldError: Cannot resolve keyword 'organisme_formation' into field.
Choices are: createur, date_debut, date_fin, formateurs, tenant, type_formation, ...
```

**Cause** : Le champ `organisme_formation` a été supprimé de `SessionFormation` lors du refactoring vers `tenant`.

**Solution** : Remplacer dans `views_dashboards.py` :
```python
# AVANT (incorrect)
SessionFormation.objects.filter(organisme_formation=organisme_formation.nom)

# APRÈS (correct)
tenant_of = getattr(organisme_formation, 'tenant_of', None)
if tenant_of:
    SessionFormation.objects.filter(tenant=tenant_of)
```

### Problème 2 : FieldError "Cannot resolve keyword 'tenantformation'"

**Erreur** :
```
Cannot resolve keyword 'tenantformation' into field.
Choices are: ..., propositions_of, ...
```

**Cause** : Utilisation du nom de classe au lieu du `related_name` dans le filtre ORM.

**Solution** : Dans `services.py`, utiliser le `related_name` défini dans le modèle :
```python
# AVANT (incorrect)
Specialisation.objects.filter(tenantformation__tenant=tenant)

# APRÈS (correct)
Specialisation.objects.filter(propositions_of__tenant=tenant)
```

**Référence modèle** :
```python
class TenantFormation(models.Model):
    spécialisations = models.ManyToManyField(
        Specialisation, 
        related_name='propositions_of'  # ← Utiliser ce nom !
    )
```

### Problème 3 : Page vide (formateurs_list.html)

**Erreur** : Template affiché vide, aucun contenu visible.

**Cause** : Utilisation de `{% block content %}` alors que `base.html` définit `{% block page_content %}`.

**Solution** : Remplacer dans tous les templates formateurs :
```html
<!-- AVANT (incorrect) -->
{% block content %}

<!-- APRÈS (correct) -->
{% block page_content %}
```

---

## ✅ Checklist de Validation

- [ ] Migration créée et appliquée (FormateurAffectation)
- [ ] Service layer avec 3 fonctions (formateurs_of, specialisations_proposees_of, sync_formateur_competences)
- [ ] 2 formulaires avec validation (FormateurForm.clean() pour XOR)
- [ ] 3 vues protégées par @role_required(['admin_of', 'secretariat'])
- [ ] 4 URLs configurées
- [ ] 2 templates utilisant {% block page_content %}
- [ ] Lien dans sidebar visible pour admin_of/secretariat
- [ ] Tests manuels :
  - [ ] Créer formateur (nouveau user)
  - [ ] Créer formateur (user existant)
  - [ ] Affecter spécialisations
  - [ ] Modifier spécialisations
  - [ ] Activer/désactiver formateur
  - [ ] Vérifier cascade soft-delete (ProfilUtilisateur.actif=False → FormateurAffectation.actif=False)

---

## 📚 Références Code

**Fichiers modifiés/créés** :
- `models.py` : FormateurAffectation (ligne 182-207), SessionFormation.formateurs M2M
- `services.py` : NOUVEAU fichier (99 lignes)
- `forms.py` : FormateurForm (ligne 440-470), FormateurCompetencesForm (ligne 473-485)
- `views_formateurs.py` : NOUVEAU fichier (187 lignes)
- `urls.py` : Import + 4 routes formateurs
- `templates/habilitations_app/formateurs_list.html` : NOUVEAU (89 lignes)
- `templates/habilitations_app/formateur_form.html` : NOUVEAU (110 lignes)
- `templates/habilitations_app/base.html` : Ajout lien sidebar "FORMATEUR"
- `views_dashboards.py` : Fix SessionFormation.filter(tenant=...) au lieu de organisme_formation

**Migration** : `0013_formateuraffectation_and_more.py`

---

## 💡 Leçons Apprises

1. **Multi-tenant avec M2M** : Utiliser table d'association (FormateurAffectation) pour relation N-N avec métadonnées (actif, date_debut)

2. **Service layer pattern** : Extraire logique métier (formateurs_of, sync_formateur_competences) pour réutilisation et testabilité

3. **Soft delete cascade** : Désactiver en cascade (ProfilUtilisateur → FormateurAffectation → FormateurCompetence) pour audit trail

4. **Related names** : TOUJOURS utiliser le `related_name` défini dans le modèle, jamais le nom de classe en minuscule

5. **Form validation** : Utiliser `clean()` pour validation inter-champs (XOR entre user_id et new user fields)

6. **Template blocks** : Vérifier le nom exact des blocks dans base.html avant de créer child templates

7. **QuerySet filtering** : Filtrer par `tenant` dans architecture multi-tenant pour isolation des données

8. **Transaction atomicity** : Utiliser `@transaction.atomic()` pour opérations multi-modèles (User + ProfilUtilisateur + FormateurAffectation + FormateurCompetence)

---

## 🔄 Pour Reproduire sur Autre Fonctionnalité

**Template du prompt** :
```
Je veux implémenter [FONCTIONNALITÉ] dans mon application Django [CONTEXTE].

ARCHITECTURE EXISTANTE :
- Modèles : [LISTER MODÈLES CONCERNÉS]
- Relations : [DÉCRIRE FK/M2M PERTINENTES]
- Permissions : [RÔLES QUI PEUVENT ACCÉDER]
- Templates : [STRUCTURE BASE.HTML ET BLOCKS]

BESOIN FONCTIONNEL :
[DÉCRIRE CAS D'USAGE ET WORKFLOWS]

CONTRAINTES TECHNIQUES :
- [MULTI-TENANT ?]
- [SOFT DELETE ?]
- [RELATED_NAMES IMPORTANTS]
- [CHAMPS SUPPRIMÉS/REFACTORISÉS]

LIVRABLES :
1. Modèles : [QUOI CRÉER/MODIFIER]
2. Services : [FONCTIONS MÉTIER]
3. Forms : [VALIDATION SPÉCIFIQUE]
4. Views : [LISTE DES ACTIONS]
5. URLs : [ROUTES]
6. Templates : [LISTE + FEATURES]
7. Navigation : [OÙ AJOUTER LIEN]

ERREURS À ÉVITER :
[LISTER LES PIÈGES CONNUS]
```

---

**Date de création** : 12 janvier 2026  
**Version Django** : 4.2.7  
**Complexité** : ⭐⭐⭐⭐ (Multi-tenant + M2M + Soft delete + Service layer)
