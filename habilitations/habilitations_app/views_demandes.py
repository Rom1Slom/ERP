"""
Vues pour la gestion des demandes de formation (B2B2C)

Workflow:
1. Responsable PME : Créer demande de formation pour ses employés
2. Admin OF : Recevoir et gérer les demandes
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import DemandeFormation, Stagiaire, Habilitation, SessionFormation, Formation
from .middleware import get_accessible_stagiaires, get_accessible_demandes_formation
from .decorators import role_required


@login_required
@role_required(['responsable_pme'])
def creer_demande_formation(request):
    """Vue pour créer une demande de formation (Responsable PME uniquement)"""
    profil = request.user.profil
    
    # Récupérer les stagiaires de la PME
    stagiaires = Stagiaire.objects.filter(entreprise=profil.entreprise, actif=True)
    
    # Récupérer l'OF qui gère cette PME (via les stagiaires)
    organisme_formation = None
    if stagiaires.exists():
        organisme_formation = stagiaires.first().organisme_formation
        tenant = stagiaires.first().tenant
    else:
        tenant = getattr(profil, 'tenant', None)
    
    if not organisme_formation:
        messages.error(request, "Aucun organisme de formation associé à votre entreprise.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        habilitation_id = request.POST.get('habilitation')
        stagiaires_ids = request.POST.getlist('stagiaires')
        date_souhaitee = request.POST.get('date_souhaitee')
        commentaire = request.POST.get('commentaire')
        
        if not habilitation_id or not stagiaires_ids:
            messages.error(request, "Veuillez sélectionner une habilitation et au moins un stagiaire.")
        else:
            # Créer la demande
            demande = DemandeFormation.objects.create(
                entreprise_demandeuse=profil.entreprise,
                organisme_formation=organisme_formation,
                tenant=tenant,
                habilitation_id=habilitation_id,
                date_souhaitee=date_souhaitee if date_souhaitee else None,
                commentaire_demande=commentaire,
                demandeur=request.user,
                statut='en_attente',
                consentement_at=timezone.now(),
                consentement_ip=request.META.get('REMOTE_ADDR'),
                consentement_user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Ajouter les stagiaires
            demande.stagiaires.set(stagiaires_ids)
            
            messages.success(
                request, 
                f"Demande de formation créée avec succès pour {demande.nombre_stagiaires} stagiaire(s). "
                f"L'organisme de formation sera notifié."
            )
            return redirect('liste_demandes_formation')
    
    habilitations = Habilitation.objects.filter(actif=True)
    
    context = {
        'stagiaires': stagiaires,
        'habilitations': habilitations,
        'organisme_formation': organisme_formation,
    }
    return render(request, 'habilitations_app/demande_formation_form.html', context)


@login_required
def liste_demandes_formation(request):
    """Liste des demandes de formation selon le rôle"""
    demandes = get_accessible_demandes_formation(request.user)
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        demandes = demandes.filter(statut=statut)
    
    habilitation_id = request.GET.get('habilitation')
    if habilitation_id:
        demandes = demandes.filter(habilitation_id=habilitation_id)
    
    context = {
        'demandes': demandes,
        'habilitations': Habilitation.objects.filter(actif=True),
        'est_admin_of': request.is_admin_of,
        'est_responsable_pme': request.is_responsable_pme,
    }
    return render(request, 'habilitations_app/demande_formation_list.html', context)


@login_required
def detail_demande_formation(request, pk):
    """Détail d'une demande de formation"""
    demande = get_object_or_404(DemandeFormation, pk=pk)
    
    # Vérifier les permissions
    profil = request.user.profil
    
    # Super admin : accès total
    if not profil.est_super_admin:
        # Admin OF / Secrétariat : uniquement demandes reçues par son OF
        if profil.est_admin_of or profil.est_secretariat:
            if demande.organisme_formation != profil.entreprise:
                messages.error(request, "Vous n'avez pas accès à cette demande.")
                return redirect('liste_demandes_formation')
        
        # Formateur : uniquement si la demande a été intégrée dans une de ses sessions
        elif profil.est_formateur:
            if not demande.session_creee or demande.session_creee.formateur != request.user:
                messages.error(request, "Demande non liée à vos sessions.")
                return redirect('liste_demandes_formation')

        # Responsable PME : uniquement demandes émises par sa PME
        elif profil.est_responsable_pme:
            if demande.entreprise_demandeuse != profil.entreprise:
                messages.error(request, "Vous n'avez pas accès à cette demande.")
                return redirect('liste_demandes_formation')
        
        # Autres rôles : pas d'accès
        else:
            messages.error(request, "Vous n'avez pas les permissions pour accéder à cette demande.")
            return redirect('home')
    
    context = {
        'demande': demande,
        'est_admin_of': request.is_admin_of,
    }
    return render(request, 'habilitations_app/demande_formation_detail.html', context)


@login_required
@role_required(['admin_of', 'secretariat'])
def traiter_demande_formation(request, pk):
    """Traiter une demande de formation (Admin OF uniquement)"""
    profil = request.user.profil
    demande = get_object_or_404(
        DemandeFormation, 
        pk=pk,
        organisme_formation=profil.entreprise,
        statut='en_attente'
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        commentaire_reponse = request.POST.get('commentaire_reponse')
        
        if action == 'approuver':
            demande.statut = 'approuvee'
            demande.commentaire_reponse = commentaire_reponse
            demande.date_traitement = timezone.now()
            demande.traite_par = request.user
            demande.save()
            
            messages.success(request, "Demande approuvée. Vous pouvez maintenant créer une session de formation.")
            return redirect('creer_session_from_demande', demande_pk=pk)
        
        elif action == 'refuser':
            demande.statut = 'refusee'
            demande.commentaire_reponse = commentaire_reponse
            demande.date_traitement = timezone.now()
            demande.traite_par = request.user
            demande.save()
            
            messages.info(request, "Demande refusée.")
            return redirect('liste_demandes_formation')
    
    context = {
        'demande': demande,
    }
    return render(request, 'habilitations_app/traiter_demande_formation.html', context)


@login_required
@role_required(['admin_of', 'secretariat'])
def creer_session_from_demande(request, demande_pk):
    """Créer une session de formation depuis une demande approuvée"""
    profil = request.user.profil
    demande = get_object_or_404(
        DemandeFormation,
        pk=demande_pk,
        organisme_formation=profil.entreprise,
        statut='approuvee'
    )
    
    if request.method == 'POST':
        # Créer la session
        session = SessionFormation.objects.create(
            habilitation=demande.habilitation,
            numero_session=request.POST.get('numero_session'),
            organisme_formation=profil.entreprise.nom,
            tenant=getattr(profil, 'tenant', None),
            date_debut=request.POST.get('date_debut'),
            date_fin=request.POST.get('date_fin'),
            nombre_places=int(request.POST.get('nombre_places', 20)),
            lieu=request.POST.get('lieu'),
            notes=request.POST.get('notes', '')
        )
        
        # Inscrire les stagiaires de la demande
        for stagiaire in demande.stagiaires.all():
            Formation.objects.create(
                stagiaire=stagiaire,
                habilitation=demande.habilitation,
                session=session,
                date_debut=session.date_debut,
                date_fin_prevue=session.date_fin,
                numero_session=session.numero_session,
                organisme_formation=session.organisme_formation,
                tenant=session.tenant,
                statut='en_cours'
            )
        
        # Lier la session à la demande
        demande.session_creee = session
        demande.save()
        
        messages.success(
            request,
            f"Session créée et {demande.nombre_stagiaires} stagiaire(s) inscrit(s) avec succès."
        )
        return redirect('detail_session_formation', pk=session.pk)
    
    context = {
        'demande': demande,
        'date_suggeree': demande.date_souhaitee,
    }
    return render(request, 'habilitations_app/creer_session_from_demande.html', context)
