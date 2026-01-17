"""
Vues pour la gestion des invitations Clients par les OF
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from .decorators import admin_of_required
from .models import Entreprise, InvitationEntreprise, ProfilUtilisateur
from .forms import EntrepriseForm, InvitationEntrepriseForm


@login_required
@admin_of_required
def creer_client(request):
    """Créer un Client (Admin OF) - sans invitation"""
    profil = request.user.profil
    organisme_formation = profil.entreprise
    
    if request.method == 'POST':
        entreprise_form = EntrepriseForm(request.POST)
        
        if entreprise_form.is_valid():
            # Créer le client
            client = entreprise_form.save(commit=False)
            client.type_entreprise = 'client'
            client.save()
            
            messages.success(request, f"Client '{client.nom}' créé avec succès.")
            return redirect('liste_invitations')
    else:
        entreprise_form = EntrepriseForm()
    
    return render(request, 'habilitations_app/client_create.html', {
        'form': entreprise_form,
        'organisme_formation': organisme_formation,
    })


@login_required
@admin_of_required
def inviter_client(request, client_id=None):
    """Inviter un Client existant (Admin OF)"""
    profil = request.user.profil
    organisme_formation = profil.entreprise
    
    # Si client_id est fourni, c'est une invitation pour un client existant
    client = None
    if client_id:
        client = get_object_or_404(Entreprise, id=client_id, type_entreprise='client')
    
    if request.method == 'POST':
        # Créer l'invitation
        invitation_form = InvitationEntrepriseForm(request.POST)
        
        if invitation_form.is_valid():
            # Déterminer le client
            if client:
                # Invitation pour un client existant
                client_obj = client
            else:
                # Créer un nouveau client ET inviter
                entreprise_form = EntrepriseForm(request.POST)
                if not entreprise_form.is_valid():
                    messages.error(request, "Erreur lors de la création du client.")
                    return render(request, 'habilitations_app/client_invite.html', {
                        'form': invitation_form,
                        'entreprise_form': entreprise_form,
                        'organisme_formation': organisme_formation,
                        'client': client,
                    })
                
                client_obj = entreprise_form.save(commit=False)
                client_obj.type_entreprise = 'client'
                client_obj.save()
            
            # Créer l'invitation
            invitation = invitation_form.save(commit=False)
            invitation.organisme_formation = organisme_formation
            invitation.entreprise_client = client_obj
            invitation.created_by = request.user
            invitation.save()
            
            # Lien d'invitation
            lien = request.build_absolute_uri(f"/invite/{invitation.token}/")
            messages.success(request, f"Invitation envoyée pour '{client_obj.nom}'. Lien: {lien}")
            
            return render(request, 'habilitations_app/invitation_success.html', {
                'entreprise': client_obj,
                'invitation': invitation,
                'lien': lien,
            })
    else:
        invitation_form = InvitationEntrepriseForm()
    
    context = {
        'form': invitation_form,
        'organisme_formation': organisme_formation,
        'client': client,
    }
    
    if not client:
        # Si pas de client fourni, on ajoute aussi le formulaire pour créer un client
        context['entreprise_form'] = EntrepriseForm()
    
    return render(request, 'habilitations_app/client_invite.html', context)


@login_required
@admin_of_required
def creer_entreprise_et_invitation(request):
    """Créer un Client ET envoyer une invitation (Admin OF) - Legacy"""
    # Cette fonction est gardée pour la compatibilité, elle redirige vers inviter_client
    return inviter_client(request)


@login_required
@admin_of_required
def liste_invitations(request):
    """Liste des invitations créées par l'OF"""
    profil = request.user.profil
    invitations = InvitationEntreprise.objects.filter(organisme_formation=profil.entreprise)
    return render(request, 'habilitations_app/invitation_list.html', {
        'invitations': invitations,
    })


def accepter_invitation(request, token):
    """Acceptation d'une invitation via token"""
    invitation = get_object_or_404(InvitationEntreprise, token=token)
    
    if invitation.statut != 'pending' or invitation.is_expired:
        messages.error(request, "Invitation invalide ou expirée.")
        return render(request, 'habilitations_app/invitation_invalid.html', {'invitation': invitation})
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "Veuillez renseigner un identifiant et un mot de passe.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Cet identifiant est déjà pris.")
        else:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=invitation.email_contact,
                password=password
            )
            # Créer le profil Responsable PME
            ProfilUtilisateur.objects.create(
                user=user,
                entreprise=invitation.entreprise_client,
                role='responsable_pme',
                actif=True
            )
            
            # Marquer invitation comme acceptée
            invitation.statut = 'accepted'
            invitation.accepted_by = user
            invitation.date_accepted = timezone.now()
            invitation.save()
            
            # Connecter et rediriger
            auth_login(request, user)
            messages.success(request, "Compte créé. Bienvenue sur Oxalis !")
            return redirect('dashboard_responsable_pme')
    
    return render(request, 'habilitations_app/invitation_accept.html', {
        'invitation': invitation,
    })
