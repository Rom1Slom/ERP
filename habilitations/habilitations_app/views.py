from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from datetime import timedelta
from django.utils import timezone
import csv
import io
from .models import (
    Entreprise, Stagiaire, Formation, ValidationCompetence, 
    Titre, AvisFormation, RenouvellementHabilitation, Habilitation,
    DemandeStagiaire, SessionFormation, ProfilUtilisateur
)
from .forms import (
    StagiaireForm, FormationForm, ValidationCompetenceForm, 
    AvisFormationForm, TitreForm, RenouvellementForm,
    DemandeStagiaireForm, SessionFormationForm, AssignerDemandeForm
)


class CustomLoginView(LoginView):
    """Vue de connexion personnalisée avec redirection selon le rôle B2B2C"""
    template_name = 'habilitations_app/login.html'
    
    def get_success_url(self):
        """Rediriger selon le rôle de l'utilisateur"""
        try:
            profil = self.request.user.profil
            
            if profil.est_super_admin:
                return reverse_lazy('dashboard_super_admin')
            elif profil.est_admin_of:
                return reverse_lazy('dashboard_admin_of')
            elif profil.est_secretariat:
                return reverse_lazy('dashboard_admin_of')
            elif profil.est_formateur:
                return reverse_lazy('dashboard_formateur')
            elif profil.est_responsable_pme:
                return reverse_lazy('dashboard_responsable_pme')
            elif profil.est_stagiaire:
                return reverse_lazy('dashboard_stagiaire')
            
        except (AttributeError, ProfilUtilisateur.DoesNotExist):
            messages.warning(self.request, "Profil utilisateur non configuré.")
        
        # Par défaut, rediriger vers la page d'accueil
        return reverse_lazy('home')


@login_required
def home(request):
    """Page d'accueil - redirection intelligente selon le rôle B2B2C"""
    try:
        profil = request.user.profil
        
        if profil.est_super_admin:
            return redirect('dashboard_super_admin')
        elif profil.est_admin_of:
            return redirect('dashboard_admin_of')
        elif profil.est_secretariat:
            return redirect('dashboard_admin_of')
        elif profil.est_formateur:
            return redirect('dashboard_formateur')
        elif profil.est_responsable_pme:
            return redirect('dashboard_responsable_pme')
        elif profil.est_stagiaire:
            return redirect('dashboard_stagiaire')
        
    except (AttributeError, ProfilUtilisateur.DoesNotExist):
        messages.warning(request, "Profil utilisateur non configuré.")
    
    return render(request, 'habilitations_app/home.html')


@login_required
def dashboard_client(request):
    """Tableau de bord pour les clients (gestion des salariés)"""
    profil = request.user.profil
    if not profil.est_client:
        messages.error(request, "Accès réservé aux clients.")
        return redirect('home')
    
    entreprise = profil.entreprise
    
    # Statistiques
    stagiaires = Stagiaire.objects.filter(entreprise=entreprise).count()
    formations_en_cours = Formation.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='en_cours'
    ).count()
    titres_valides = Titre.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='delivre'
    ).count()
    
    # Alertes
    titres_expiration_proche = Titre.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='delivre',
        date_expiration__lte=timezone.now().date() + timedelta(days=90),
        date_expiration__gte=timezone.now().date()
    )
    
    formations_completees_recentes = Formation.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='completee',
        date_fin_reelle__isnull=False
    ).order_by('-date_fin_reelle')[:5]
    
    context = {
        'stagiaires': stagiaires,
        'formations_en_cours': formations_en_cours,
        'titres_valides': titres_valides,
        'titres_expiration_proche': titres_expiration_proche,
        'formations_recentes': formations_completees_recentes,
    }
    
    return render(request, 'habilitations_app/dashboard_client.html', context)


@login_required
def dashboard_of(request):
    """Tableau de bord pour les OF (validation des formations)"""
    profil = request.user.profil
    if not profil.est_of:
        messages.error(request, "Accès réservé aux organismes de formation.")
        return redirect('home')
    
    entreprise = profil.entreprise
    
    # Statistiques pour l'OF
    sessions_en_cours = SessionFormation.objects.filter(
        organisme_formation=entreprise.nom,
        statut='en_cours'
    ).count()
    
    formations_en_attente = Formation.objects.filter(
        organisme_formation=entreprise.nom,
        statut='completee'
    ).exclude(avis__isnull=False).count()
    
    demandes_en_attente = DemandeStagiaire.objects.filter(
        statut='en_attente'
    ).count()
    
    # Récentes actions
    sessions_recentes = SessionFormation.objects.filter(
        organisme_formation=entreprise.nom
    ).order_by('-date_debut')[:5]
    
    context = {
        'sessions_en_cours': sessions_en_cours,
        'formations_en_attente': formations_en_attente,
        'demandes_en_attente': demandes_en_attente,
        'sessions_recentes': sessions_recentes,
    }
    
    return render(request, 'habilitations_app/dashboard_of.html', context)


class StagiaireListView(LoginRequiredMixin, ListView):
    """Liste des stagiaires"""
    model = Stagiaire
    template_name = 'habilitations_app/stagiaire_list.html'
    context_object_name = 'stagiaires'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Stagiaire.objects.filter(
            entreprise=self.request.user.profil.entreprise
        )
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(prenom__icontains=search) |
                Q(email__icontains=search) |
                Q(poste__icontains=search)
            )
        return queryset.order_by('nom', 'prenom')


class StagiaireDetailView(LoginRequiredMixin, DetailView):
    """Détail d'un stagiaire"""
    model = Stagiaire
    template_name = 'habilitations_app/stagiaire_detail.html'
    context_object_name = 'stagiaire'
    
    def get_object(self):
        return get_object_or_404(
            Stagiaire,
            pk=self.kwargs['pk'],
            entreprise=self.request.user.profil.entreprise
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formations'] = Formation.objects.filter(stagiaire=self.object)
        context['titres'] = Titre.objects.filter(stagiaire=self.object)
        return context


class StagiaireCreateView(LoginRequiredMixin, CreateView):
    """Créer un stagiaire"""
    model = Stagiaire
    form_class = StagiaireForm
    template_name = 'habilitations_app/stagiaire_form.html'
    success_url = reverse_lazy('stagiaire_list')
    
    def form_valid(self, form):
        profil = self.request.user.profil
        form.instance.entreprise = profil.entreprise
        form.instance.organisme_formation = getattr(profil.entreprise, 'tenant_of', None) or form.instance.organisme_formation
        form.instance.tenant = getattr(profil, 'tenant', None) or getattr(profil.entreprise, 'tenant', None)
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Stagiaire créé avec succès.')
        return reverse_lazy('stagiaire_list')


class StagiaireUpdateView(LoginRequiredMixin, UpdateView):
    """Modifier un stagiaire"""
    model = Stagiaire
    form_class = StagiaireForm
    template_name = 'habilitations_app/stagiaire_form.html'
    
    def get_object(self):
        return get_object_or_404(
            Stagiaire,
            pk=self.kwargs['pk'],
            entreprise=self.request.user.profil.entreprise
        )
    
    def get_success_url(self):
        messages.success(self.request, 'Stagiaire modifié avec succès.')
        return reverse_lazy('stagiaire_detail', kwargs={'pk': self.object.pk})


class FormationListView(LoginRequiredMixin, ListView):
    """Liste des formations"""
    model = Formation
    template_name = 'habilitations_app/formation_list.html'
    context_object_name = 'formations'
    paginate_by = 20
    
    def get_queryset(self):
        profil = self.request.user.profil

        if profil.est_formateur:
            queryset = Formation.objects.filter(session__formateur=self.request.user)
        elif profil.est_of:
            tenant = getattr(profil, 'tenant', None)
            queryset = Formation.objects.all()
            if tenant:
                queryset = queryset.filter(tenant=tenant)
        else:
            queryset = Formation.objects.filter(stagiaire__entreprise=profil.entreprise)

        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset.order_by('-date_debut')


class FormationDetailView(LoginRequiredMixin, DetailView):
    """Détail d'une formation"""
    model = Formation
    template_name = 'habilitations_app/formation_detail.html'
    context_object_name = 'formation'
    
    def get_object(self):
        profil = self.request.user.profil
        if profil.est_formateur:
            return get_object_or_404(
                Formation,
                pk=self.kwargs['pk'],
                session__formateur=self.request.user
            )
        if profil.est_of:
            tenant = getattr(profil, 'tenant', None)
            qs = Formation.objects.all()
            if tenant:
                qs = qs.filter(tenant=tenant)
            return get_object_or_404(qs, pk=self.kwargs['pk'])

        return get_object_or_404(
            Formation,
            pk=self.kwargs['pk'],
            stagiaire__entreprise=self.request.user.profil.entreprise
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validations'] = ValidationCompetence.objects.filter(formation=self.object)
        try:
            context['avis'] = AvisFormation.objects.get(formation=self.object)
        except AvisFormation.DoesNotExist:
            context['avis'] = None
        try:
            context['titre'] = Titre.objects.get(formation=self.object)
        except Titre.DoesNotExist:
            context['titre'] = None
        return context


class FormationCreateView(LoginRequiredMixin, CreateView):
    """Créer une formation"""
    model = Formation
    form_class = FormationForm
    template_name = 'habilitations_app/formation_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stagiaire_id'] = self.kwargs.get('stagiaire_id')
        return context
    
    def form_valid(self, form):
        stagiaire_id = self.kwargs.get('stagiaire_id')
        stagiaire = get_object_or_404(
            Stagiaire,
            pk=stagiaire_id,
            entreprise=self.request.user.profil.entreprise
        )
        form.instance.stagiaire = stagiaire
        form.instance.tenant = getattr(stagiaire, 'tenant', None)
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Formation créée avec succès.')
        return reverse_lazy('formation_detail', kwargs={'pk': self.object.pk})


class FormationUpdateView(LoginRequiredMixin, UpdateView):
    """Modifier une formation"""
    model = Formation
    form_class = FormationForm
    template_name = 'habilitations_app/formation_form.html'
    
    def get_object(self):
        return get_object_or_404(
            Formation,
            pk=self.kwargs['pk'],
            stagiaire__entreprise=self.request.user.profil.entreprise
        )
    
    def get_success_url(self):
        messages.success(self.request, 'Formation modifiée avec succès.')
        return reverse_lazy('formation_detail', kwargs={'pk': self.object.pk})


@login_required
def valider_competences(request, formation_id):
    """Valider les compétences d'une formation"""
    profil = request.user.profil
    if profil.est_formateur:
        formation = get_object_or_404(
            Formation,
            pk=formation_id,
            session__formateur=request.user
        )
    elif profil.est_of:
        qs = Formation.objects.all()
        tenant = getattr(profil, 'tenant', None)
        if tenant:
            qs = qs.filter(tenant=tenant)
        formation = get_object_or_404(qs, pk=formation_id)
    else:
        formation = get_object_or_404(
            Formation,
            pk=formation_id,
            stagiaire__entreprise=profil.entreprise
        )
    
    # Créer les validations de compétences si elles n'existent pas
    habilitation = formation.habilitation
    savoirs = [s.strip() for s in habilitation.savoirs.split('\n') if s.strip()]
    savoirs_faire = [sf.strip() for sf in habilitation.savoirs_faire.split('\n') if sf.strip()]
    
    validations = []
    for savoir in savoirs:
        val, created = ValidationCompetence.objects.get_or_create(
            formation=formation,
            titre_competence=savoir,
            defaults={'type_competence': 'savoir', 'tenant': formation.tenant}
        )
        validations.append(val)
    
    for sf in savoirs_faire:
        val, created = ValidationCompetence.objects.get_or_create(
            formation=formation,
            titre_competence=sf,
            defaults={'type_competence': 'savoir_faire', 'tenant': formation.tenant}
        )
        validations.append(val)
    
    if request.method == 'POST':
        for validation_id in request.POST.getlist('validations'):
            try:
                validation = ValidationCompetence.objects.get(
                    pk=validation_id,
                    formation=formation
                )
                validation.valide = validation_id in request.POST.getlist('validations_check')
                validation.validateur = request.user
                validation.date_validation = timezone.now()
                validation.save()
            except ValidationCompetence.DoesNotExist:
                pass
        
        messages.success(request, 'Compétences validées avec succès.')
        return redirect('formation_detail', pk=formation_id)
    
    context = {
        'formation': formation,
        'validations': ValidationCompetence.objects.filter(formation=formation),
    }
    
    return render(request, 'habilitations_app/valider_competences.html', context)


@login_required
def creer_avis_formation(request, formation_id):
    """Créer l'avis de formation"""
    profil = request.user.profil
    if profil.est_formateur:
        formation = get_object_or_404(
            Formation,
            pk=formation_id,
            session__formateur=request.user
        )
    elif profil.est_of:
        tenant = getattr(profil, 'tenant', None)
        qs = Formation.objects.all()
        if tenant:
            qs = qs.filter(tenant=tenant)
        formation = get_object_or_404(qs, pk=formation_id)
    else:
        formation = get_object_or_404(
            Formation,
            pk=formation_id,
            stagiaire__entreprise=profil.entreprise
        )
    
    try:
        avis = AvisFormation.objects.get(formation=formation)
    except AvisFormation.DoesNotExist:
        avis = None
    
    if request.method == 'POST':
        form = AvisFormationForm(request.POST, request.FILES, instance=avis)
        if form.is_valid():
            avis_obj = form.save(commit=False)
            avis_obj.formation = formation
            avis_obj.tenant = formation.tenant
            avis_obj.save()
            messages.success(request, 'Avis de formation enregistré.')
            return redirect('formation_detail', pk=formation_id)
    else:
        form = AvisFormationForm(instance=avis)
    
    context = {
        'form': form,
        'formation': formation,
        'avis': avis,
    }
    
    return render(request, 'habilitations_app/avis_form.html', context)


@login_required
def delivrer_titre(request, formation_id):
    """Délivrer un titre d'habilitation"""
    profil = request.user.profil
    if profil.est_formateur:
        formation = get_object_or_404(
            Formation,
            pk=formation_id,
            session__formateur=request.user,
            statut='completee'
        )
    elif profil.est_of:
        tenant = getattr(profil, 'tenant', None)
        qs = Formation.objects.filter(statut='completee')
        if tenant:
            qs = qs.filter(tenant=tenant)
        formation = get_object_or_404(qs, pk=formation_id)
    else:
        formation = get_object_or_404(
            Formation,
            pk=formation_id,
            stagiaire__entreprise=profil.entreprise,
            statut='completee'
        )
    
    try:
        titre = Titre.objects.get(formation=formation)
    except Titre.DoesNotExist:
        titre = None
    
    if request.method == 'POST':
        form = TitreForm(request.POST, instance=titre)
        if form.is_valid():
            titre_obj = form.save(commit=False)
            titre_obj.formation = formation
            titre_obj.stagiaire = formation.stagiaire
            titre_obj.habilitation = formation.habilitation
            titre_obj.delivre_par = request.user
            titre_obj.tenant = formation.tenant
            titre_obj.save()
            messages.success(request, 'Titre d\'habilitation délivré.')
            return redirect('formation_detail', pk=formation_id)
    else:
        form = TitreForm(instance=titre)
    
    context = {
        'form': form,
        'formation': formation,
        'titre': titre,
    }
    
    return render(request, 'habilitations_app/titre_form.html', context)


class TitreListView(LoginRequiredMixin, ListView):
    """Liste des titres d'habilitation"""
    model = Titre
    template_name = 'habilitations_app/titre_list.html'
    context_object_name = 'titres'
    paginate_by = 20
    
    def get_queryset(self):
        profil = self.request.user.profil
        if profil.est_formateur:
            return Titre.objects.filter(
                formation__session__formateur=self.request.user
            ).order_by('-date_delivrance')
        if profil.est_of:
            qs = Titre.objects.all()
            if getattr(profil, 'tenant', None):
                qs = qs.filter(tenant=profil.tenant)
            return qs.order_by('-date_delivrance')
        return Titre.objects.filter(
            stagiaire__entreprise=profil.entreprise
        ).order_by('-date_delivrance')


class RenouvellementListView(LoginRequiredMixin, ListView):
    """Liste des renouvellements"""
    model = RenouvellementHabilitation
    template_name = 'habilitations_app/renouvellement_list.html'
    context_object_name = 'renouvellements'
    paginate_by = 20
    
    def get_queryset(self):
        profil = self.request.user.profil
        if profil.est_formateur:
            return RenouvellementHabilitation.objects.filter(
                titre_precedent__formation__session__formateur=self.request.user
            ).order_by('date_renouvellement_prevue')
        if profil.est_of:
            qs = RenouvellementHabilitation.objects.all()
            if getattr(profil, 'tenant', None):
                qs = qs.filter(tenant=profil.tenant)
            return qs.order_by('date_renouvellement_prevue')
        return RenouvellementHabilitation.objects.filter(
            titre_precedent__stagiaire__entreprise=profil.entreprise
        ).order_by('date_renouvellement_prevue')


@login_required
def planifier_renouvellement(request, titre_id):
    """Planifier le renouvellement d'un titre"""
    titre = get_object_or_404(
        Titre,
        pk=titre_id,
        stagiaire__entreprise=request.user.profil.entreprise
    )
    
    if request.method == 'POST':
        form = RenouvellementForm(request.POST)
        if form.is_valid():
            renouvellement = form.save(commit=False)
            renouvellement.titre_precedent = titre
            renouvellement.tenant = titre.tenant
            renouvellement.save()
            messages.success(request, 'Renouvellement planifié.')
            return redirect('titre_list')
    else:
        form = RenouvellementForm()
    
    context = {
        'form': form,
        'titre': titre,
    }
    
    return render(request, 'habilitations_app/renouvellement_form.html', context)


# === GESTION DES DEMANDES DE STAGIAIRES (ENTREPRISE CLIENTE) ===

@login_required
def soumettre_demande_stagiaire(request):
    """Permet à une entreprise cliente de soumettre une demande de stagiaire"""
    try:
        entreprise = request.user.profil.entreprise
    except:
        messages.error(request, "Vous devez être associé à une entreprise pour soumettre une demande.")
        return redirect('home')
    
    if request.method == 'POST':
        form = DemandeStagiaireForm(request.POST, entreprise=entreprise)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.entreprise = entreprise
            demande.tenant = getattr(entreprise, 'tenant', None)
            demande.consentement_at = timezone.now()
            demande.consentement_ip = request.META.get('REMOTE_ADDR')
            demande.consentement_user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Si un stagiaire existant est sélectionné, on copie ses infos
            if form.cleaned_data.get('stagiaire_existant'):
                stagiaire = form.cleaned_data['stagiaire_existant']
                demande.stagiaire_existant = stagiaire
                demande.nom = stagiaire.nom
                demande.prenom = stagiaire.prenom
                demande.email = stagiaire.email
                demande.telephone = stagiaire.telephone
                demande.poste = stagiaire.poste
                demande.date_embauche = stagiaire.date_embauche
                demande.tenant = demande.tenant or getattr(stagiaire, 'tenant', None)
            
            demande.save()
            # Sauvegarder les habilitations (ManyToMany)
            form.save_m2m()
            
            # Vérifier si c'est un renouvellement (existence de titres précédents)
            if demande.stagiaire_existant:
                titres_precedents = Titre.objects.filter(
                    stagiaire=demande.stagiaire_existant,
                    habilitation__in=form.cleaned_data['habilitations_demandees']
                )
                if titres_precedents.exists():
                    demande.est_renouvellement = True
                    demande.titre_renouvelle = titres_precedents.first()
                    demande.save()
            
            nom_complet = f"{demande.prenom} {demande.nom}"
            messages.success(request, f"Demande soumise pour {nom_complet}. Nous vous contacterons bientôt.")
            return redirect('liste_demandes_stagiaires')
    else:
        form = DemandeStagiaireForm(entreprise=entreprise)
    
    context = {
        'form': form,
    }
    return render(request, 'habilitations_app/demande_stagiaire_form.html', context)


@login_required
def liste_demandes_stagiaires(request):
    """Liste des demandes de stagiaires pour l'entreprise cliente"""
    try:
        entreprise = request.user.profil.entreprise
    except:
        messages.error(request, "Vous devez être associé à une entreprise.")
        return redirect('home')
    
    demandes = DemandeStagiaire.objects.filter(entreprise=entreprise).order_by('-date_demande')
    
    context = {
        'demandes': demandes,
    }
    return render(request, 'habilitations_app/demande_stagiaire_list.html', context)


# === GESTION DES SESSIONS DE FORMATION (SECRÉTAIRE KOMPETANS) ===

@login_required
def creer_session_formation(request):
    """Créer une session de formation (secrétaire kompetans)"""
    profil = request.user.profil
    if not (profil.est_admin_of or profil.est_secretariat):
        messages.error(request, "Accès réservé au personnel OF.")
        return redirect('home')

    if request.method == 'POST':
        form = SessionFormationForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.createur = request.user
            session.tenant = getattr(profil, 'tenant', None)
            session.save()
            messages.success(request, f"Session {session.numero_session} créée avec succès.")
            return redirect('detail_session_formation', pk=session.pk)
    else:
        form = SessionFormationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'habilitations_app/session_formation_form.html', context)


@login_required
def liste_sessions_formation(request):
    """Liste des sessions de formation"""
    profil = request.user.profil
    if not (profil.est_admin_of or profil.est_secretariat or profil.est_formateur or profil.est_super_admin):
        messages.error(request, "Accès réservé aux organismes de formation.")
        return redirect('home')

    sessions = SessionFormation.objects.all().order_by('-date_debut')
    if getattr(profil, 'tenant', None):
        sessions = sessions.filter(tenant=profil.tenant)
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        sessions = sessions.filter(statut=statut)
    
    habilitation_id = request.GET.get('habilitation')
    if habilitation_id:
        sessions = sessions.filter(habilitation_id=habilitation_id)
    
    context = {
        'sessions': sessions,
        'habilitations': Habilitation.objects.all(),
    }
    return render(request, 'habilitations_app/session_formation_list.html', context)


@login_required
def detail_session_formation(request, pk):
    """Détail d'une session de formation avec possibilité d'assigner des demandes"""
    profil = request.user.profil
    session = get_object_or_404(SessionFormation, pk=pk)

    if not (profil.est_super_admin or profil.est_admin_of or profil.est_secretariat or profil.est_formateur):
        messages.error(request, "Accès réservé aux organismes de formation.")
        return redirect('home')

    if getattr(profil, 'tenant', None) and session.tenant and session.tenant != profil.tenant:
        messages.error(request, "Session hors de votre tenant.")
        return redirect('liste_sessions_formation')
    
    # Demandes en attente pour cette habilitation
    demandes_disponibles = DemandeStagiaire.objects.filter(
        statut='en_attente'
    )
    if hasattr(session, 'habilitation'):
        demandes_disponibles = demandes_disponibles.filter(habilitations_demandees=session.habilitation)
    if session.tenant:
        demandes_disponibles = demandes_disponibles.filter(tenant=session.tenant)
    
    # Demandes déjà assignées à cette session
    demandes_assignees = session.demandes.all()
    
    # Formations créées pour cette session
    formations_session = session.formations_session.all()
    
    if request.method == 'POST' and 'assigner_demandes' in request.POST:
        form = AssignerDemandeForm(request.POST, habilitation=session.habilitation)
        if form.is_valid():
            demandes_selectionnees = form.cleaned_data['demandes']
            for demande in demandes_selectionnees:
                if session.places_restantes > 0:
                    # Créer le stagiaire
                    stagiaire, created = Stagiaire.objects.get_or_create(
                        email=demande.email,
                        defaults={
                            'entreprise': demande.entreprise,
                            'organisme_formation': profil.entreprise,
                            'tenant': session.tenant or getattr(profil, 'tenant', None),
                            'nom': demande.nom,
                            'prenom': demande.prenom,
                            'telephone': demande.telephone,
                            'poste': demande.poste,
                            'date_embauche': demande.date_embauche,
                        }
                    )
                    
                    # Créer la formation
                    formation, created = Formation.objects.get_or_create(
                        stagiaire=stagiaire,
                        habilitation=session.habilitation,
                        defaults={
                            'session': session,
                            'date_debut': session.date_debut,
                            'date_fin_prevue': session.date_fin,
                            'numero_session': session.numero_session,
                            'organisme_formation': session.organisme_formation,
                            'tenant': session.tenant or getattr(profil, 'tenant', None),
                        }
                    )
                    
                    # Mettre à jour la demande
                    demande.statut = 'integree'
                    demande.session_assignee = session
                    demande.stagiaire_cree = stagiaire
                    demande.date_traitement = timezone.now()
                    demande.traite_par = request.user
                    demande.save()
                else:
                    messages.warning(request, f"Session complète. Impossible d'ajouter {demande.nom_complet}.")
                    break
            
            messages.success(request, f"{len(demandes_selectionnees)} stagiaire(s) intégré(s) à la session.")
            return redirect('detail_session_formation', pk=pk)
    else:
        form = AssignerDemandeForm(habilitation=session.habilitation)
    
    context = {
        'session': session,
        'demandes_disponibles': demandes_disponibles,
        'demandes_assignees': demandes_assignees,
        'formations_session': formations_session,
        'form': form,
    }
    return render(request, 'habilitations_app/session_formation_detail.html', context)


@login_required
def liste_demandes_admin(request):
    """Liste de toutes les demandes pour le secrétaire kompetans"""
    profil = request.user.profil
    if not (profil.est_admin_of or profil.est_secretariat or profil.est_super_admin):
        messages.error(request, "Accès réservé au secrétariat OF.")
        return redirect('home')

    demandes = DemandeStagiaire.objects.all().order_by('-date_demande')
    if getattr(profil, 'tenant', None):
        demandes = demandes.filter(tenant=profil.tenant)
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        demandes = demandes.filter(statut=statut)
    
    entreprise_id = request.GET.get('entreprise')
    if entreprise_id:
        demandes = demandes.filter(entreprise_id=entreprise_id)
    
    habilitation_id = request.GET.get('habilitation')
    if habilitation_id:
        demandes = demandes.filter(habilitation_demandee_id=habilitation_id)
    
    context = {
        'demandes': demandes,
        'entreprises': Entreprise.objects.all(),
        'habilitations': Habilitation.objects.all(),
    }
    return render(request, 'habilitations_app/demande_admin_list.html', context)


# === API / ENDPOINTS UTILITAIRES ===


@login_required
def api_import_csv(request):
    """Import CSV stagiaires + demandes (dry-run support)"""
    profil = request.user.profil
    if not (profil.est_admin_of or profil.est_secretariat or profil.est_super_admin):
        return JsonResponse({'error': 'Accès refusé'}, status=403)

    if request.method != 'POST' or 'file' not in request.FILES:
        return JsonResponse({'error': 'Fichier CSV manquant'}, status=400)

    tenant = getattr(profil, 'tenant', None)
    uploaded = request.FILES['file']
    dry_run = request.POST.get('dry_run', 'true') == 'true'

    data = uploaded.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(data))

    created_stagiaires = 0
    created_demandes = 0
    errors = []

    for idx, row in enumerate(reader, start=1):
        try:
            entreprise_nom = row.get('entreprise')
            email = row.get('email')
            if not entreprise_nom or not email:
                errors.append(f"Ligne {idx}: entreprise ou email manquant")
                continue

            entreprise, _ = Entreprise.objects.get_or_create(
                nom=entreprise_nom,
                defaults={'type_entreprise': 'client', 'email': 'na@example.com', 'telephone': '', 'adresse': '', 'code_postal': '', 'ville': '', 'tenant': tenant}
            )

            if not dry_run:
                stagiaire, created = Stagiaire.objects.get_or_create(
                    email=email,
                    defaults={
                        'nom': row.get('nom', ''),
                        'prenom': row.get('prenom', ''),
                        'entreprise': entreprise,
                        'organisme_formation': profil.entreprise,
                        'tenant': tenant,
                    }
                )
                if created:
                    created_stagiaires += 1

                hab_code = row.get('habilitation_code')
                if hab_code:
                    try:
                        hab = Habilitation.objects.get(code=hab_code)
                        demande = DemandeFormation.objects.create(
                            entreprise_demandeuse=entreprise,
                            organisme_formation=profil.entreprise,
                            tenant=tenant,
                            habilitation=hab,
                            statut='en_attente',
                            demandeur=request.user,
                            consentement_at=timezone.now(),
                        )
                        demande.stagiaires.add(stagiaire)
                        created_demandes += 1
                    except Habilitation.DoesNotExist:
                        errors.append(f"Ligne {idx}: habilitation {hab_code} inconnue")
        except Exception as exc:
            errors.append(f"Ligne {idx}: {exc}")

    return JsonResponse({
        'dry_run': dry_run,
        'created_stagiaires': created_stagiaires,
        'created_demandes': created_demandes,
        'errors': errors,
    })


@login_required
def api_aggregats_of(request):
    """Agrégats rapides pour un tenant OF"""
    profil = request.user.profil
    if not (profil.est_admin_of or profil.est_secretariat or profil.est_super_admin):
        return JsonResponse({'error': 'Accès refusé'}, status=403)

    tenant = getattr(profil, 'tenant', None)
    filt = {}
    if tenant:
        filt['tenant'] = tenant

    titres_expirant = Titre.objects.filter(**filt, statut='delivre', date_expiration__lte=timezone.now().date() + timedelta(days=90)).count()
    demandes_en_attente = DemandeFormation.objects.filter(**filt, statut='en_attente').count()
    sessions_en_cours = SessionFormation.objects.filter(**filt, statut='en_cours').count()

    return JsonResponse({
        'titres_expirant_90j': titres_expirant,
        'demandes_en_attente': demandes_en_attente,
        'sessions_en_cours': sessions_en_cours,
    })


@login_required
def api_valider_demande(request, demande_id):
    """Validation rapide d'une demande (Admin OF / Secrétariat)"""
    profil = request.user.profil
    if not (profil.est_admin_of or profil.est_secretariat or profil.est_super_admin):
        return JsonResponse({'error': 'Accès refusé'}, status=403)

    try:
        demande = DemandeFormation.objects.get(pk=demande_id)
    except DemandeFormation.DoesNotExist:
        return JsonResponse({'error': 'Demande introuvable'}, status=404)

    if getattr(profil, 'tenant', None) and demande.tenant and demande.tenant != profil.tenant:
        return JsonResponse({'error': 'Demande hors tenant'}, status=403)

    action = request.POST.get('action')
    commentaire = request.POST.get('commentaire', '')

    if action not in ['approuver', 'refuser']:
        return JsonResponse({'error': 'Action invalide'}, status=400)

    demande.statut = 'approuvee' if action == 'approuver' else 'refusee'
    demande.commentaire_reponse = commentaire
    demande.date_traitement = timezone.now()
    demande.traite_par = request.user
    demande.save()

    return JsonResponse({'status': demande.statut})


@login_required
def api_pdf_titre(request, titre_id):
    """Génération rapide d'un PDF de titre"""
    profil = request.user.profil
    try:
        titre = Titre.objects.get(pk=titre_id)
    except Titre.DoesNotExist:
        return JsonResponse({'error': 'Titre introuvable'}, status=404)

    # Contrôle d'accès tenant/rôle
    if not (profil.est_super_admin or profil.est_admin_of or profil.est_secretariat or profil.est_formateur or profil.est_responsable_pme):
        return JsonResponse({'error': 'Accès refusé'}, status=403)
    if getattr(profil, 'tenant', None) and titre.tenant and titre.tenant != profil.tenant:
        return JsonResponse({'error': 'Titre hors tenant'}, status=403)
    if profil.est_responsable_pme and titre.stagiaire.entreprise != profil.entreprise:
        return JsonResponse({'error': 'Titre hors entreprise'}, status=403)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        # Fallback texte
        content = f"Titre {titre.numero_titre} - {titre.stagiaire.nom_complet}"
        return HttpResponse(content, content_type='application/pdf')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setTitle(f"Titre {titre.numero_titre}")
    p.drawString(50, 800, f"Titre d'habilitation {titre.numero_titre}")
    p.drawString(50, 780, f"Stagiaire: {titre.stagiaire.nom_complet}")
    p.drawString(50, 760, f"Habilitation: {titre.habilitation.code} - {titre.habilitation.nom}")
    p.drawString(50, 740, f"Délivré le: {titre.date_delivrance}")
    p.drawString(50, 720, f"Expire le: {titre.date_expiration}")
    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f"attachment; filename=titre-{titre.numero_titre}.pdf"
    return response

