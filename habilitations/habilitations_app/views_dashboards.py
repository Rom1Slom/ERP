"""
Tableaux de bord spécifiques par rôle B2B2C
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from .models import (
    Entreprise, Stagiaire, Formation, Titre, SessionFormation, 
    DemandeFormation, Habilitation
)
from .decorators import role_required
from .middleware import (
    get_accessible_stagiaires, 
    get_accessible_entreprises,
    get_accessible_demandes_formation
)


@login_required
@role_required(['super_admin'])
def dashboard_super_admin(request):
    """Tableau de bord Super Admin - Vue globale de la plateforme"""
    
    # Statistiques globales
    total_of = Entreprise.objects.filter(type_entreprise='of').count()
    total_pme = Entreprise.objects.filter(type_entreprise='client').count()
    total_stagiaires = Stagiaire.objects.count()
    total_formations = Formation.objects.count()
    
    # OF actifs (ayant des sessions récentes)
    of_actifs = Entreprise.objects.filter(
        type_entreprise='of',
        stagiaires_of__formations__date_creation__gte=timezone.now() - timedelta(days=90)
    ).distinct().count()
    
    # Derniers OF créés
    derniers_of = Entreprise.objects.filter(type_entreprise='of').order_by('-date_creation')[:5]
    
    # Demandes de formation récentes
    demandes_recentes = DemandeFormation.objects.all().order_by('-date_demande')[:10]
    
    # Sessions actives
    sessions_actives = SessionFormation.objects.filter(
        statut='en_cours',
        date_fin__gte=timezone.now().date()
    ).count()
    
    context = {
        'total_of': total_of,
        'total_pme': total_pme,
        'total_stagiaires': total_stagiaires,
        'total_formations': total_formations,
        'of_actifs': of_actifs,
        'derniers_of': derniers_of,
        'demandes_recentes': demandes_recentes,
        'sessions_actives': sessions_actives,
    }
    
    return render(request, 'habilitations_app/dashboard_super_admin.html', context)


@login_required
@role_required(['admin_of', 'secretariat'])
def dashboard_admin_of(request):
    """Tableau de bord Admin OF - Gestion OF"""
    profil = request.user.profil
    organisme_formation = profil.entreprise
    
    # Stagiaires gérés par cet OF
    total_stagiaires = Stagiaire.objects.filter(organisme_formation=organisme_formation).count()
    stagiaires_independants = Stagiaire.objects.filter(
        organisme_formation=organisme_formation,
        entreprise__isnull=True
    ).count()
    
    # PME clientes
    pme_clientes = Entreprise.objects.filter(
        type_entreprise='client',
        stagiaires__organisme_formation=organisme_formation
    ).distinct()
    total_pme = pme_clientes.count()
    
    # Sessions
    sessions_en_cours = SessionFormation.objects.filter(
        organisme_formation=organisme_formation.nom,
        statut='en_cours',
        date_fin__gte=timezone.now().date()
    ).count()
    
    sessions_recentes = SessionFormation.objects.filter(
        organisme_formation=organisme_formation.nom
    ).order_by('-date_debut')[:5]
    
    # Demandes de formation reçues
    demandes_en_attente = DemandeFormation.objects.filter(
        organisme_formation=organisme_formation,
        statut='en_attente'
    )
    
    demandes_approuvees = DemandeFormation.objects.filter(
        organisme_formation=organisme_formation,
        statut='approuvee'
    ).count()
    
    # Formations en attente de validation
    formations_a_valider = Formation.objects.filter(
        stagiaire__organisme_formation=organisme_formation,
        statut='completee'
    ).exclude(avis__isnull=False).count()
    
    # Titres délivrés ce mois
    titres_mois = Titre.objects.filter(
        stagiaire__organisme_formation=organisme_formation,
        date_delivrance__gte=timezone.now().date().replace(day=1)
    ).count()
    
    context = {
        'organisme_formation': organisme_formation,
        'total_stagiaires': total_stagiaires,
        'stagiaires_independants': stagiaires_independants,
        'total_pme': total_pme,
        'pme_clientes': pme_clientes[:5],  # 5 premières PME
        'sessions_en_cours': sessions_en_cours,
        'sessions_recentes': sessions_recentes,
        'demandes_en_attente': demandes_en_attente,
        'demandes_approuvees': demandes_approuvees,
        'formations_a_valider': formations_a_valider,
        'titres_mois': titres_mois,
    }
    
    return render(request, 'habilitations_app/dashboard_admin_of.html', context)


@login_required
@role_required(['formateur'])
def dashboard_formateur(request):
    """Tableau de bord Formateur - sessions et validations"""
    profil = request.user.profil

    sessions_assignees = SessionFormation.objects.filter(formateur=request.user)
    if getattr(profil, 'tenant', None):
        sessions_assignees = sessions_assignees.filter(tenant=profil.tenant)

    sessions_en_cours = sessions_assignees.filter(statut='en_cours')
    formations_a_valider = Formation.objects.filter(
        session__in=sessions_assignees,
        statut='completee'
    ).exclude(avis__isnull=False)

    context = {
        'sessions_assignees': sessions_assignees[:5],
        'sessions_en_cours': sessions_en_cours.count(),
        'formations_a_valider': formations_a_valider.count(),
    }

    return render(request, 'habilitations_app/dashboard_formateur.html', context)


@login_required
@role_required(['responsable_pme'])
def dashboard_responsable_pme(request):
    """Tableau de bord Responsable PME - Suivi employés"""
    profil = request.user.profil
    entreprise = profil.entreprise
    
    # Récupérer l'OF qui gère cette PME
    stagiaire_exemple = Stagiaire.objects.filter(entreprise=entreprise).first()
    organisme_formation = stagiaire_exemple.organisme_formation if stagiaire_exemple else None
    
    # Stagiaires de la PME
    total_stagiaires = Stagiaire.objects.filter(entreprise=entreprise, actif=True).count()
    
    # Formations
    formations_en_cours = Formation.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='en_cours'
    ).count()
    
    formations_completees = Formation.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='completee'
    ).count()
    
    # Titres
    titres_valides = Titre.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='delivre',
        date_expiration__gte=timezone.now().date()
    ).count()
    
    # Alertes - Titres expirant dans 90 jours
    titres_expiration_proche = Titre.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='delivre',
        date_expiration__lte=timezone.now().date() + timedelta(days=90),
        date_expiration__gte=timezone.now().date()
    )
    
    # Demandes de formation
    demandes_en_attente = DemandeFormation.objects.filter(
        entreprise_demandeuse=entreprise,
        statut='en_attente'
    ).count()
    
    demandes_approuvees = DemandeFormation.objects.filter(
        entreprise_demandeuse=entreprise,
        statut='approuvee'
    ).count()
    
    # Dernières formations complétées
    formations_recentes = Formation.objects.filter(
        stagiaire__entreprise=entreprise,
        statut='completee'
    ).order_by('-date_fin_reelle')[:5]
    
    context = {
        'entreprise': entreprise,
        'organisme_formation': organisme_formation,
        'total_stagiaires': total_stagiaires,
        'formations_en_cours': formations_en_cours,
        'formations_completees': formations_completees,
        'titres_valides': titres_valides,
        'titres_expiration_proche': titres_expiration_proche,
        'demandes_en_attente': demandes_en_attente,
        'demandes_approuvees': demandes_approuvees,
        'formations_recentes': formations_recentes,
    }
    
    return render(request, 'habilitations_app/dashboard_responsable_pme.html', context)


@login_required
@role_required(['stagiaire'])
def dashboard_stagiaire(request):
    """Tableau de bord Stagiaire - Consultation personnelle"""
    
    try:
        stagiaire = Stagiaire.objects.get(user=request.user)
    except Stagiaire.DoesNotExist:
        messages.error(request, "Aucun profil stagiaire associé à votre compte.")
        return redirect('home')
    
    # Formations du stagiaire
    formations = Formation.objects.filter(stagiaire=stagiaire).order_by('-date_debut')
    formations_en_cours = formations.filter(statut='en_cours')
    formations_completees = formations.filter(statut='completee')
    
    # Titres du stagiaire
    titres = Titre.objects.filter(stagiaire=stagiaire).order_by('-date_delivrance')
    titres_valides = titres.filter(
        statut='delivre',
        date_expiration__gte=timezone.now().date()
    )
    titres_expires = titres.filter(
        statut='delivre',
        date_expiration__lt=timezone.now().date()
    )
    
    # Alertes - Titre expirant bientôt
    titre_expiration_proche = titres.filter(
        statut='delivre',
        date_expiration__lte=timezone.now().date() + timedelta(days=90),
        date_expiration__gte=timezone.now().date()
    ).first()
    
    context = {
        'stagiaire': stagiaire,
        'formations': formations,
        'formations_en_cours': formations_en_cours,
        'formations_completees': formations_completees,
        'titres': titres,
        'titres_valides': titres_valides,
        'titres_expires': titres_expires,
        'titre_expiration_proche': titre_expiration_proche,
    }
    
    return render(request, 'habilitations_app/dashboard_stagiaire.html', context)
