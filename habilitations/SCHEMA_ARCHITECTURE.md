# 📐 Schéma d'Architecture - Système de Gestion des Habilitations B2B2C

> **Date**: Janvier 2026  
> **Architecture**: Django Multi-Tenant SaaS B2B2C  
> **Pattern**: MVC avec isolation par Tenant

---

## 🏗️ Vue d'ensemble de l'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ARCHITECTURE B2B2C                          │
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │ Super Admin  │      │  Admin OF    │      │ Responsable  │  │
│  │  (Éditeur)   │─────▶│ (Kompetans)  │─────▶│    PME       │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│                              │                      │            │
│                              │                      │            │
│                        ┌─────▼──────┐         ┌────▼────┐      │
│                        │ Formateurs │         │Stagiaires│      │
│                        │ Secrétariat│         │ Salariés │      │
│                        └────────────┘         └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Modèles de Données Principaux (models.py)

### 🏢 **Hiérarchie Organisationnelle**

```python
# TENANT SAAS - Isolation des données
┌──────────────────────────────────────────────────────────┐
│ Tenant                                                    │
├───────────────────────────────────────────────────────────┤
│ - organisme_formation: FK(Entreprise)  # OF propriétaire │
│ - slug: SlugField                      # of-kompetans    │
│ - nom_public: CharField                # "Kompetans"     │
│ - domaine: CharField                   # of.example.com  │
│ - logo: ImageField                                        │
│ - couleur_primaire: CharField          # #2c3e50         │
│ - couleur_secondaire: CharField        # #27ae60         │
│ - actif: BooleanField                                     │
├───────────────────────────────────────────────────────────┤
│ Relations inverses:                                       │
│ - entreprises (Entreprise)             # Clients PME     │
│ - sessions (SessionFormation)                             │
│ - stagiaires (Stagiaire)                                  │
│ - demandes_formation (DemandeFormation)                   │
│ - utilisateurs (ProfilUtilisateur)                        │
└───────────────────────────────────────────────────────────┘
         │
         │ OneToOne
         ▼
┌──────────────────────────────────────────────────────────┐
│ Entreprise                                                │
├───────────────────────────────────────────────────────────┤
│ - nom: CharField                                          │
│ - type_entreprise: CharField           # 'of' | 'client' │
│ - email: EmailField                                       │
│ - telephone: CharField                                    │
│ - adresse: TextField                                      │
│ - tenant: FK(Tenant)                   # Propriétaire    │
├───────────────────────────────────────────────────────────┤
│ Relations inverses:                                       │
│ - tenant_of (Tenant)                   # Si OF           │
│ - entreprises (Tenant)                 # Si Client       │
│ - stagiaires (Stagiaire)               # Employés        │
│ - utilisateurs (ProfilUtilisateur)     # Responsables    │
└───────────────────────────────────────────────────────────┘
```

### 👥 **Utilisateurs et Profils**

```python
┌──────────────────────────────────────────────────────────┐
│ User (Django)                                             │
│ - username, email, password, is_staff, is_superuser       │
└──────────────────────────────────────────────────────────┘
         │
         │ OneToOne
         ▼
┌──────────────────────────────────────────────────────────┐
│ ProfilUtilisateur                                         │
├───────────────────────────────────────────────────────────┤
│ - user: OneToOne(User)                                    │
│ - tenant: FK(Tenant)                   # Isolation        │
│ - entreprise: FK(Entreprise)           # OF ou PME       │
│ - role: CharField                      # Voir ci-dessous │
│ - actif: BooleanField                                     │
├───────────────────────────────────────────────────────────┤
│ Rôles (ROLES):                                            │
│ • 'super_admin'     → Éditeur SaaS (gère tous les OF)    │
│ • 'admin_of'        → Admin OF (gère clients + sessions) │
│ • 'secretariat'     → Secrétariat OF (sessions/imports)  │
│ • 'formateur'       → Formateur OF (validations/avis)    │
│ • 'responsable_pme' → Responsable PME (demandes)         │
│ • 'stagiaire'       → Stagiaire (consultation dossier)   │
├───────────────────────────────────────────────────────────┤
│ @property helpers:                                        │
│ - est_super_admin                                         │
│ - est_admin_of                                            │
│ - est_secretariat                                         │
│ - est_formateur                                           │
│ - est_responsable_pme                                     │
│ - est_stagiaire                                           │
└───────────────────────────────────────────────────────────┘
```

### 📚 **Formations et Spécialisations (Nouveau Système)**

```python
┌──────────────────────────────────────────────────────────┐
│ TypeFormation                                             │
├───────────────────────────────────────────────────────────┤
│ - code: CharField                      # HAB, CACES       │
│ - nom: CharField                       # Habilitation     │
│ - titre_officiel: CharField            # NF C18-510       │
│ - duree_validite_mois: IntegerField    # 36 mois          │
│ - created_by_tenant: FK(Tenant)        # Custom OF        │
├───────────────────────────────────────────────────────────┤
│ Relations inverses:                                       │
│ - specialisations (Specialisation)                        │
│ - sessions (SessionFormation)                             │
└───────────────────────────────────────────────────────────┘
         │
         │ M2M via
         ▼
┌──────────────────────────────────────────────────────────┐
│ Specialisation                                            │
├───────────────────────────────────────────────────────────┤
│ - type_formation: FK(TypeFormation)                       │
│ - code: CharField                      # B1, B2, BR, H0V  │
│ - nom: CharField                       # Exécutant B1     │
│ - savoirs: TextField                   # Théoriques       │
│ - savoirs_faire: TextField             # Pratiques        │
│ - duree_validite_mois: IntegerField    # Override         │
├───────────────────────────────────────────────────────────┤
│ Exemples:                                                 │
│ • TypeFormation "Habilitation" → B1, B2, BC, BR, H0V      │
│ • TypeFormation "CACES" → Cat1, Cat3, Cat5                │
├───────────────────────────────────────────────────────────┤
│ Relations inverses:                                       │
│ - formateurs (FormateurCompetence)                        │
│ - sessions.spécialisations (SessionFormation)             │
│ - titres (Titre)                                          │
└───────────────────────────────────────────────────────────┘
         │
         │ M2M
         ▼
┌──────────────────────────────────────────────────────────┐
│ TenantFormation                                           │
├───────────────────────────────────────────────────────────┤
│ - tenant: FK(Tenant)                                      │
│ - type_formation: FK(TypeFormation)                       │
│ - spécialisations: M2M(Specialisation)                    │
│ - nom_package: CharField               # "Pack Basique"  │
│ - actif: BooleanField                                     │
├───────────────────────────────────────────────────────────┤
│ Exemple:                                                  │
│ Kompetans propose:                                        │
│ - Type "Habilitation" + [B1, B2] = "Pack Basique"        │
│ - Type "Habilitation" + [BC, BR, H1V] = "Pack Avancé"    │
└───────────────────────────────────────────────────────────┘
```

### 👨‍🏫 **Formateurs et Compétences**

```python
┌──────────────────────────────────────────────────────────┐
│ ProfilUtilisateur (role='formateur')                      │
│ ─ Formateur lié à un OF via entreprise                   │
└───────────────────────────────────────────────────────────┘
         │
         │ M2M via FormateurCompetence
         ▼
┌──────────────────────────────────────────────────────────┐
│ FormateurCompetence                                       │
├───────────────────────────────────────────────────────────┤
│ - formateur_profil: FK(ProfilUtilisateur)                 │
│ - specialisation: FK(Specialisation)                      │
│ - actif: BooleanField                                     │
│ - notes: TextField                     # Certifications   │
├───────────────────────────────────────────────────────────┤
│ Logique:                                                  │
│ • Formateur "Alice" → [HAB-B1, HAB-B2]                   │
│ • Formateur "Bob" → [CACES-Cat1, CACES-Cat3]             │
│                                                           │
│ ⚠️  Validation: Pour animer une session, le formateur    │
│     DOIT maîtriser TOUTES les spécialisations            │
└───────────────────────────────────────────────────────────┘
         │
         │ M2M
         ▼
┌──────────────────────────────────────────────────────────┐
│ FormateurAffectation                                      │
├───────────────────────────────────────────────────────────┤
│ - formateur: FK(ProfilUtilisateur)                        │
│ - entreprise: FK(Entreprise)           # OF               │
│ - actif: BooleanField                                     │
└───────────────────────────────────────────────────────────┘
```

### 🎓 **Stagiaires et Parcours**

```python
┌──────────────────────────────────────────────────────────┐
│ Stagiaire                                                 │
├───────────────────────────────────────────────────────────┤
│ - user: OneToOne(User)                 # Optionnel        │
│ - organisme_formation: FK(Entreprise)  # OF responsable   │
│ - tenant: FK(Tenant)                                      │
│ - entreprise: FK(Entreprise)           # PME (NULL si     │
│                                        # indépendant)     │
│ - nom, prenom, email, telephone                           │
│ - poste, date_embauche                                    │
│ - actif: BooleanField                                     │
├───────────────────────────────────────────────────────────┤
│ @property est_independant: entreprise is None             │
├───────────────────────────────────────────────────────────┤
│ Relations inverses:                                       │
│ - formations (Formation)                                  │
│ - titres (Titre)                                          │
│ - demandes_formation (DemandeFormation)                   │
└───────────────────────────────────────────────────────────┘
         │
         │ M2M
         ▼
┌──────────────────────────────────────────────────────────┐
│ Formation                                                 │
├───────────────────────────────────────────────────────────┤
│ - stagiaire: FK(Stagiaire)                                │
│ - habilitation: FK(Habilitation)       # LEGACY           │
│ - tenant: FK(Tenant)                                      │
│ - session: FK(SessionFormation)                           │
│ - date_debut, date_fin_prevue, date_fin_reelle            │
│ - statut: CharField                    # en_cours/        │
│                                        # completee/       │
│                                        # abandonnee       │
├───────────────────────────────────────────────────────────┤
│ @property est_completee                                   │
│ @property jours_restants                                  │
├───────────────────────────────────────────────────────────┤
│ Relations inverses:                                       │
│ - validations (ValidationCompetence)                      │
│ - avis (AvisFormation)                                    │
└───────────────────────────────────────────────────────────┘
         │
         │ OneToOne
         ▼
┌──────────────────────────────────────────────────────────┐
│ Titre                                                     │
├───────────────────────────────────────────────────────────┤
│ - stagiaire: FK(Stagiaire)                                │
│ - formation: OneToOne(Formation)                          │
│ - tenant: FK(Tenant)                                      │
│ - specialisation: FK(Specialisation)   # Nouveau          │
│ - habilitation: FK(Habilitation)       # LEGACY           │
│ - numero_titre: CharField              # Unique           │
│ - date_delivrance, date_expiration                        │
│ - statut: CharField                    # attente/delivre/ │
│                                        # expire/renouvele │
├───────────────────────────────────────────────────────────┤
│ @property est_valide                                      │
│ @property jours_avant_expiration                          │
│ @property expire_bientot               # < 90 jours       │
└───────────────────────────────────────────────────────────┘
```

### 📅 **Sessions de Formation**

```python
┌──────────────────────────────────────────────────────────┐
│ SessionFormation                                          │
├───────────────────────────────────────────────────────────┤
│ - numero_session: CharField            # Unique           │
│ - tenant: FK(Tenant)                                      │
│ - type_formation: FK(TypeFormation)    # Nouveau          │
│ - spécialisations: M2M(Specialisation) # [B1, B2, ...]   │
│ - formateurs: M2M(ProfilUtilisateur)   # Multi-formateurs│
│ - habilitation: FK(Habilitation)       # LEGACY           │
│ - formateur: FK(User)                  # LEGACY           │
│ - date_debut, date_fin                                    │
│ - lieu: CharField                                         │
│ - statut: CharField                    # planifiee/       │
│                                        # en_cours/        │
│                                        # terminee/annulee │
│ - nombre_places: IntegerField                             │
├───────────────────────────────────────────────────────────┤
│ @property places_restantes                                │
│ @property est_complete                                    │
│ def formateur_has_competences()        # Validation       │
├───────────────────────────────────────────────────────────┤
│ Relations inverses:                                       │
│ - formations_session (Formation)                          │
│ - demandes_independants (DemandeStagiaire)                │
│ - demandes_origine (DemandeFormation)                     │
└───────────────────────────────────────────────────────────┘
```

### 📝 **Demandes de Formation (B2B2C)**

```python
┌──────────────────────────────────────────────────────────┐
│ DemandeFormation                                          │
│ ─ PME → OF (pour salariés)                               │
├───────────────────────────────────────────────────────────┤
│ - entreprise_demandeuse: FK(Entreprise) # PME            │
│ - organisme_formation: FK(Entreprise)   # OF              │
│ - tenant: FK(Tenant)                                      │
│ - habilitation: FK(Habilitation)                          │
│ - stagiaires: M2M(Stagiaire)           # Employés         │
│ - statut: CharField                    # en_attente/      │
│                                        # approuvee/       │
│                                        # refusee/annulee  │
│ - type_formation: CharField            # intra/inter      │
│ - lieu_formation: CharField            # sur_site/        │
│                                        # chez_of          │
│ - date_souhaitee: DateField                               │
│ - demandeur: FK(User)                  # Responsable PME  │
│ - session_creee: FK(SessionFormation)  # Si approuvée     │
├───────────────────────────────────────────────────────────┤
│ @property nombre_stagiaires                               │
└───────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ DemandeStagiaire                                          │
│ ─ Stagiaire indépendant → OF                             │
├───────────────────────────────────────────────────────────┤
│ - stagiaire_existant: FK(Stagiaire)    # Optionnel        │
│ - tenant: FK(Tenant)                                      │
│ - nom, prenom, email, telephone        # Si nouveau       │
│ - statut_professionnel: CharField      # Auto-entrepren.  │
│ - type_formation: FK(TypeFormation)    # Nouveau          │
│ - spécialisations_demandees: M2M(Specialisation)          │
│ - habilitations_demandees: M2M(Habilitation) # LEGACY     │
│ - statut: CharField                    # en_attente/      │
│                                        # validee/integree │
│ - session_assignee: FK(SessionFormation)                  │
│ - stagiaire_cree: FK(Stagiaire)        # Si créé          │
├───────────────────────────────────────────────────────────┤
│ @property nom_complet                                     │
└───────────────────────────────────────────────────────────┘
```

### ✅ **Validation et Certification**

```python
┌──────────────────────────────────────────────────────────┐
│ ValidationCompetence                                      │
├───────────────────────────────────────────────────────────┤
│ - formation: FK(Formation)                                │
│ - tenant: FK(Tenant)                                      │
│ - specialisation: FK(Specialisation)   # Nouveau          │
│ - type_competence: CharField           # savoir/          │
│                                        # savoir_faire     │
│ - titre_competence: CharField          # LEGACY           │
│ - valide: BooleanField                                    │
│ - validateur: FK(User)                 # Formateur        │
│ - commentaires_validateur: TextField                      │
└───────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ AvisFormation                                             │
├───────────────────────────────────────────────────────────┤
│ - formation: OneToOne(Formation)                          │
│ - tenant: FK(Tenant)                                      │
│ - avis: CharField                      # favorable/       │
│                                        # favorable_        │
│                                        # condition/        │
│                                        # defavorable      │
│ - observations, points_forts, points_amelioration         │
│ - formateur_nom: CharField                                │
│ - signature_formateur: ImageField                         │
└───────────────────────────────────────────────────────────┘
```

---

## 🎯 Vues et Contrôleurs (views.py)

### 📁 **Structure des Fichiers de Vues**

```
views.py                  # Vues principales (CRUD stagiaires/formations)
views_dashboards.py       # Tableaux de bord par rôle
views_demandes.py         # Gestion demandes de formation
views_formateurs.py       # Gestion formateurs (admin_of)
views_catalogue.py        # Catalogue formations OF
views_invitations.py      # Invitations clients PME
views_api.py              # API endpoints
```

### 🏠 **Dashboards par Rôle**

```python
# views_dashboards.py

@login_required
@role_required(['super_admin'])
def dashboard_super_admin(request):
    """Vue globale plateforme - Tous les OF"""
    context = {
        'total_of': Entreprise.objects.filter(type_entreprise='of').count(),
        'total_pme': Entreprise.objects.filter(type_entreprise='client').count(),
        'total_stagiaires': Stagiaire.objects.count(),
        'sessions_actives': SessionFormation.objects.filter(statut='en_cours').count(),
        'demandes_recentes': DemandeFormation.objects.all()[:10]
    }
    return render(request, 'dashboard_super_admin.html', context)

@login_required
@role_required(['admin_of', 'secretariat'])
def dashboard_admin_of(request):
    """Dashboard OF - Demandes + Sessions + Stagiaires"""
    profil = request.user.profil
    tenant = profil.tenant
    
    context = {
        'demandes_attente': DemandeFormation.objects.filter(
            tenant=tenant, statut='en_attente'
        ).count(),
        'sessions_actives': SessionFormation.objects.filter(
            tenant=tenant, statut__in=['planifiee', 'en_cours']
        ),
        'stagiaires_actifs': Stagiaire.objects.filter(
            tenant=tenant, actif=True
        ).count(),
        'titres_expires_bientot': Titre.objects.filter(
            tenant=tenant,
            date_expiration__lte=timezone.now().date() + timedelta(days=90)
        )
    }
    return render(request, 'dashboard_admin_of.html', context)

@login_required
@role_required(['responsable_pme'])
def dashboard_responsable_pme(request):
    """Dashboard PME - Mes employés + Mes demandes"""
    profil = request.user.profil
    entreprise = profil.entreprise
    
    context = {
        'stagiaires': Stagiaire.objects.filter(entreprise=entreprise),
        'demandes': DemandeFormation.objects.filter(
            entreprise_demandeuse=entreprise
        ),
        'formations_en_cours': Formation.objects.filter(
            stagiaire__entreprise=entreprise,
            statut='en_cours'
        )
    }
    return render(request, 'dashboard_responsable_pme.html', context)

@login_required
@role_required(['formateur'])
def dashboard_formateur(request):
    """Dashboard Formateur - Mes sessions + Validations"""
    profil = request.user.profil
    
    sessions = SessionFormation.objects.filter(
        formateurs=profil
    ) | SessionFormation.objects.filter(
        formateur=request.user  # LEGACY
    )
    
    context = {
        'sessions_actives': sessions.filter(statut='en_cours'),
        'sessions_a_venir': sessions.filter(statut='planifiee'),
        'formations_a_valider': Formation.objects.filter(
            session__in=sessions,
            statut='completee'
        ).exclude(avis__isnull=False)
    }
    return render(request, 'dashboard_formateur.html', context)

@login_required
@role_required(['stagiaire'])
def dashboard_stagiaire(request):
    """Dashboard Stagiaire - Mon dossier"""
    try:
        stagiaire = Stagiaire.objects.get(user=request.user)
        context = {
            'stagiaire': stagiaire,
            'formations': stagiaire.formations.all(),
            'titres': stagiaire.titres.filter(statut='delivre')
        }
    except Stagiaire.DoesNotExist:
        context = {'error': 'Aucun dossier stagiaire trouvé'}
    
    return render(request, 'dashboard_stagiaire.html', context)
```

### 📋 **Vues CRUD Principales**

```python
# views.py

# ─────── STAGIAIRES ───────
class StagiaireListView(LoginRequiredMixin, ListView):
    model = Stagiaire
    template_name = 'stagiaire_list.html'
    
    def get_queryset(self):
        # Isolation via middleware
        return get_accessible_stagiaires(self.request)

class StagiaireDetailView(LoginRequiredMixin, DetailView):
    model = Stagiaire
    template_name = 'stagiaire_detail.html'

class StagiaireCreateView(LoginRequiredMixin, CreateView):
    model = Stagiaire
    form_class = StagiaireForm
    template_name = 'stagiaire_form.html'

# ─────── FORMATIONS ───────
class FormationListView(LoginRequiredMixin, ListView):
    model = Formation
    template_name = 'formation_list.html'

class FormationCreateView(LoginRequiredMixin, CreateView):
    model = Formation
    form_class = FormationForm
    template_name = 'formation_form.html'

@login_required
def valider_competences(request, formation_id):
    """Formateur valide savoirs + savoir-faire"""
    formation = get_object_or_404(Formation, pk=formation_id)
    # Logique validation...
    return render(request, 'valider_competences.html', context)

@login_required
def creer_avis_formation(request, formation_id):
    """Formateur crée l'avis après formation"""
    formation = get_object_or_404(Formation, pk=formation_id)
    # Logique avis...
    return render(request, 'avis_form.html', context)

@login_required
def delivrer_titre(request, formation_id):
    """Admin/Secrétariat délivre le titre"""
    formation = get_object_or_404(Formation, pk=formation_id)
    # Logique délivrance...
    return redirect('titre_list')

# ─────── SESSIONS ───────
@login_required
def liste_sessions_formation(request):
    """Liste sessions (admin_of, secretariat)"""
    profil = request.user.profil
    sessions = SessionFormation.objects.filter(tenant=profil.tenant)
    return render(request, 'session_formation_list.html', {'sessions': sessions})

@login_required
def creer_session_formation(request):
    """Créer nouvelle session"""
    if request.method == 'POST':
        form = SessionFormationForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.tenant = request.user.profil.tenant
            session.save()
            return redirect('liste_sessions_formation')
    else:
        form = SessionFormationForm()
    return render(request, 'session_formation_form.html', {'form': form})

@login_required
def detail_session_formation(request, pk):
    """Détail + Assigner demandes"""
    session = get_object_or_404(SessionFormation, pk=pk)
    
    # Demandes disponibles
    demandes_disponibles = DemandeStagiaire.objects.filter(
        statut='en_attente',
        tenant=session.tenant
    )
    
    # Demandes assignées
    demandes_assignees = session.demandes_independants.all()
    
    # Formations créées
    formations_session = session.formations_session.all()
    
    return render(request, 'session_formation_detail.html', {
        'session': session,
        'demandes_disponibles': demandes_disponibles,
        'demandes_assignees': demandes_assignees,
        'formations_session': formations_session
    })
```

### 📨 **Demandes de Formation**

```python
# views_demandes.py

@login_required
@role_required(['responsable_pme'])
def creer_demande_formation(request):
    """PME crée demande pour ses employés"""
    profil = request.user.profil
    
    if request.method == 'POST':
        # Créer DemandeFormation
        demande = DemandeFormation.objects.create(
            entreprise_demandeuse=profil.entreprise,
            organisme_formation=profil.entreprise.tenant.organisme_formation,
            tenant=profil.entreprise.tenant,
            demandeur=request.user,
            # ... autres champs
        )
        demande.stagiaires.set(stagiaires_selectes)
        return redirect('liste_demandes_formation')
    
    return render(request, 'demande_formation_form.html')

@login_required
@role_required(['admin_of', 'secretariat'])
def traiter_demande_formation(request, pk):
    """OF traite la demande (approuve/refuse)"""
    demande = get_object_or_404(DemandeFormation, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approuver':
            demande.statut = 'approuvee'
            demande.traite_par = request.user
            demande.date_traitement = timezone.now()
            demande.save()
        elif action == 'refuser':
            demande.statut = 'refusee'
            demande.save()
        
        return redirect('liste_demandes_formation')
    
    return render(request, 'demande_formation_detail.html', {'demande': demande})
```

---

## 🔐 Middleware et Sécurité (middleware.py)

### 🛡️ **MultiTenantMiddleware**

```python
class MultiTenantMiddleware:
    """Résolution tenant + Injection helpers request"""
    
    def __call__(self, request):
        # 1. Résoudre tenant depuis sous-domaine ou profil
        request.tenant = resolve_tenant_from_host(request)
        
        # 2. Injecter profil utilisateur
        if request.user.is_authenticated:
            request.profil = request.user.profil
            request.tenant = request.profil.tenant or request.tenant
            
            # 3. Injecter flags de rôle
            request.is_super_admin = request.profil.est_super_admin
            request.is_admin_of = request.profil.est_admin_of
            request.is_secretariat = request.profil.est_secretariat
            request.is_formateur = request.profil.est_formateur
            request.is_responsable_pme = request.profil.est_responsable_pme
            request.is_stagiaire = request.profil.est_stagiaire
        
        response = self.get_response(request)
        return response

def resolve_tenant_from_host(request):
    """Extrait slug tenant depuis sous-domaine"""
    host = request.get_host().split(':')[0]
    # of-kompetans.example.com → slug='of-kompetans'
    if host.startswith('of-'):
        slug = host.split('.')[0]
        return Tenant.objects.filter(slug=slug, actif=True).first()
    return None

def get_accessible_stagiaires(request):
    """Filtre stagiaires selon rôle"""
    profil = request.profil
    
    if profil.est_super_admin:
        return Stagiaire.objects.all()
    elif profil.est_admin_of or profil.est_secretariat:
        return Stagiaire.objects.filter(tenant=profil.tenant)
    elif profil.est_formateur:
        sessions = SessionFormation.objects.filter(formateurs=profil)
        return Stagiaire.objects.filter(
            formations__session__in=sessions
        ).distinct()
    elif profil.est_responsable_pme:
        return Stagiaire.objects.filter(entreprise=profil.entreprise)
    elif profil.est_stagiaire:
        return Stagiaire.objects.filter(user=request.user)
    
    return Stagiaire.objects.none()
```

### 🔒 **Décorateurs de Sécurité**

```python
# decorators.py

def role_required(allowed_roles):
    """Restreint accès à certains rôles"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            profil = request.user.profil
            if profil.role not in allowed_roles:
                raise PermissionDenied("Accès refusé")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Utilisation:
# @role_required(['admin_of', 'secretariat'])
# def ma_vue(request):
#     ...
```

---

## 🌐 URLs et Routing (urls.py)

```python
urlpatterns = [
    # ──────── DASHBOARDS ────────
    path('', views.home, name='home'),
    path('dashboard/super-admin/', views_dashboards.dashboard_super_admin),
    path('dashboard/admin-of/', views_dashboards.dashboard_admin_of),
    path('dashboard/client/', views_dashboards.dashboard_responsable_pme),
    path('dashboard/formateur/', views_dashboards.dashboard_formateur),
    path('dashboard/stagiaire/', views_dashboards.dashboard_stagiaire),
    
    # ──────── STAGIAIRES ────────
    path('stagiaires/', views.StagiaireListView.as_view()),
    path('stagiaires/<int:pk>/', views.StagiaireDetailView.as_view()),
    path('stagiaires/nouveau/', views.StagiaireCreateView.as_view()),
    
    # ──────── FORMATIONS ────────
    path('formations/', views.FormationListView.as_view()),
    path('formations/<int:pk>/', views.FormationDetailView.as_view()),
    path('formations/<int:formation_id>/competences/', views.valider_competences),
    path('formations/<int:formation_id>/avis/', views.creer_avis_formation),
    path('formations/<int:formation_id>/titre/', views.delivrer_titre),
    
    # ──────── SESSIONS ────────
    path('sessions/', views.liste_sessions_formation),
    path('sessions/creer/', views.creer_session_formation),
    path('sessions/<int:pk>/', views.detail_session_formation),
    
    # ──────── DEMANDES B2B2C ────────
    path('demandes-formation/creer/', views_demandes.creer_demande_formation),
    path('demandes-formation/', views_demandes.liste_demandes_formation),
    path('demandes-formation/<int:pk>/', views_demandes.detail_demande_formation),
    path('demandes-formation/<int:pk>/traiter/', views_demandes.traiter_demande_formation),
    
    # ──────── FORMATEURS ────────
    path('dashboard/admin-of/formateurs/', views_formateurs.formateurs_list),
    path('dashboard/admin-of/formateurs/new/', views_formateurs.formateur_edit),
    
    # ──────── CATALOGUE ────────
    path('api/catalogue-formations/', views_catalogue.catalogue_formations_list),
    path('api/catalogue-formations/add/', views_catalogue.catalogue_formations_add),
    
    # ──────── CLIENTS (Invitations) ────────
    path('of/clients/', views_invitations.liste_invitations),
    path('of/clients/creer/', views_invitations.creer_client),
    path('invite/<str:token>/', views_invitations.accepter_invitation),
    
    # ──────── API ────────
    path('api/type-formations/', views_api.api_type_formations),
    path('api/type-formations/<int:type_id>/specialisations/', 
         views_api.api_type_formation_specialisations),
]
```

---

## 🎨 Templates Frontend

### 📂 **Structure Templates**

```
templates/habilitations_app/
├── base.html                          # Layout principal
│
├── ──────── DASHBOARDS ────────
├── dashboard_super_admin.html         # Super admin
├── dashboard_admin_of.html            # Admin OF
├── dashboard_responsable_pme.html     # PME
├── dashboard_formateur.html           # Formateur
├── dashboard_stagiaire.html           # Stagiaire
│
├── ──────── STAGIAIRES ────────
├── stagiaire_list.html                # Liste
├── stagiaire_detail.html              # Détail
├── stagiaire_form.html                # Création/Edition
│
├── ──────── FORMATIONS ────────
├── formation_list.html
├── formation_detail.html
├── formation_form.html
├── valider_competences.html           # Formateur valide
├── avis_form.html                     # Formateur avis
│
├── ──────── SESSIONS ────────
├── session_formation_list.html
├── session_formation_form.html
├── session_formation_detail.html      # + Assigner demandes
│
├── ──────── DEMANDES ────────
├── demande_formation_list.html
├── demande_formation_form.html
├── demande_formation_detail.html
│
├── ──────── FORMATEURS ────────
├── formateurs_list.html
├── formateur_form.html
│
└── ──────── UTILITAIRES ────────
    ├── catalogue_formations_modal.html
    ├── client_invite.html
    └── titre_list.html
```

### 🖼️ **Template Base**

```django
{# base.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Gestion Habilitations{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
</head>
<body>
    <nav class="navbar">
        {% if request.user.is_authenticated %}
            {% if request.profil.est_super_admin %}
                <a href="{% url 'dashboard_super_admin' %}">Dashboard Super Admin</a>
            {% elif request.profil.est_admin_of or request.profil.est_secretariat %}
                <a href="{% url 'dashboard_admin_of' %}">Dashboard OF</a>
                <a href="{% url 'liste_sessions_formation' %}">Sessions</a>
                <a href="{% url 'formateurs_list' %}">Formateurs</a>
            {% elif request.profil.est_formateur %}
                <a href="{% url 'dashboard_formateur' %}">Mes Sessions</a>
            {% elif request.profil.est_responsable_pme %}
                <a href="{% url 'dashboard_responsable_pme' %}">Dashboard</a>
                <a href="{% url 'creer_demande_formation' %}">Nouvelle Demande</a>
            {% endif %}
            <a href="{% url 'logout' %}">Déconnexion</a>
        {% endif %}
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

---

## 🔄 Flux de Données Principaux

### 📊 **Workflow 1: Demande Formation PME → OF**

```
1. Responsable PME (dashboard_responsable_pme.html)
   ↓ Clique "Nouvelle demande"
   
2. Formulaire (demande_formation_form.html)
   - Sélectionne stagiaires (employés)
   - Choisit habilitation
   - Date souhaitée
   ↓ POST à views_demandes.creer_demande_formation()
   
3. Création DemandeFormation
   - entreprise_demandeuse = PME
   - organisme_formation = OF du tenant
   - statut = 'en_attente'
   ↓
   
4. Admin OF voit demande (dashboard_admin_of.html)
   ↓ Clique "Traiter"
   
5. Détail demande (demande_formation_detail.html)
   ↓ Approuve ou Refuse
   
6. Si approuvée → Créer SessionFormation
   - Assigner stagiaires
   - Assigner formateurs
   ↓
   
7. Formations créées → Validation → Avis → Titre
```

### 📊 **Workflow 2: Stagiaire Indépendant → Session**

```
1. DemandeStagiaire créée
   - Par OF (secretariat)
   - Ou auto-inscription (futur)
   ↓
   
2. Secrétariat voir demandes (liste_demandes_admin)
   ↓
   
3. Depuis detail_session_formation
   - Assigner demande à session existante
   ↓ Crée Stagiaire + Formation
   
4. Formateur valide compétences
   ↓ ValidationCompetence
   
5. Formateur crée avis
   ↓ AvisFormation
   
6. Admin/Secrétariat délivre titre
   ↓ Titre (statut='delivre')
```

### 📊 **Workflow 3: Gestion Formateurs**

```
1. Admin OF (formateurs_list.html)
   ↓ Créer formateur
   
2. Créer ProfilUtilisateur
   - role = 'formateur'
   - entreprise = OF
   ↓
   
3. Assigner compétences (FormateurCompetence)
   - formateur_profil → [HAB-B1, HAB-B2]
   ↓
   
4. Lors création SessionFormation
   - Sélectionner formateurs
   - VALIDATION: formateurs doivent maîtriser
     TOUTES les spécialisations de la session
   ↓
   
5. Formateur voit ses sessions (dashboard_formateur)
   - Valider compétences stagiaires
   - Créer avis
```

---

## 🔑 Variables et Objets Clés

### Dans les Vues

```python
# Toujours disponibles via middleware
request.user                  # User Django
request.profil               # ProfilUtilisateur
request.tenant               # Tenant (résolu depuis sous-domaine ou profil)

# Flags de rôle
request.is_super_admin
request.is_admin_of
request.is_secretariat
request.is_formateur
request.is_responsable_pme
request.is_stagiaire

# Helpers d'isolation
get_accessible_stagiaires(request)
get_accessible_entreprises(request)
get_accessible_demandes_formation(request)
```

### Dans les Templates

```django
{% if request.profil.est_super_admin %}
{% if request.profil.est_admin_of %}
{% if request.is_formateur %}

{{ request.tenant.nom_public }}
{{ request.profil.entreprise.nom }}
```

---

## 📈 Statistiques et Agrégations

```python
# Nombre de places restantes
session.places_restantes  # @property

# Titres expirant bientôt
Titre.objects.filter(
    tenant=tenant,
    date_expiration__lte=timezone.now().date() + timedelta(days=90)
)

# Demandes en attente par OF
DemandeFormation.objects.filter(
    tenant=tenant,
    statut='en_attente'
).count()

# Formations à valider
Formation.objects.filter(
    session__in=sessions_formateur,
    statut='completee'
).exclude(avis__isnull=False)
```

---

## 🎓 Résumé Architecture

### Backend (Django)
- **Models**: 15+ modèles (Tenant, Entreprise, Stagiaire, Formation, etc.)
- **Views**: 6 fichiers (views, dashboards, demandes, formateurs, etc.)
- **Middleware**: MultiTenantMiddleware (isolation + injection helpers)
- **Decorators**: `@role_required(['admin_of', 'secretariat'])`

### Frontend (Templates)
- **Base**: base.html (navbar conditionnelle par rôle)
- **Dashboards**: 5 dashboards spécifiques (super_admin, admin_of, pme, formateur, stagiaire)
- **CRUD**: stagiaire_*, formation_*, session_*

### Sécurité
- **Multi-tenant**: Isolation par Tenant (sous-domaine ou profil)
- **RBAC**: 6 rôles (super_admin → stagiaire)
- **Middleware**: Injection automatique profil + tenant
- **Helpers**: Filtrage automatique des querysets

### Workflow Principal
1. **PME** crée demande → **OF** approuve → **Secrétariat** crée session
2. **Formateur** valide compétences + avis → **Admin** délivre titre
3. **Stagiaire indépendant** demande → **Secrétariat** assigne à session
