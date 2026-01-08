"""
Vues pour la gestion des invitations PME par les OF
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
def creer_entreprise_et_invitation(request):
    """Créer une PME et envoyer une invitation (Admin OF)"""
    profil = request.user.profil
    organisme_formation = profil.entreprise
    
    if request.method == 'POST':
        entreprise_form = EntrepriseForm(request.POST)
        invitation_form = InvitationEntrepriseForm(request.POST)
        
        if entreprise_form.is_valid() and invitation_form.is_valid():
            # Créer la PME
            pme: Entreprise = entreprise_form.save(commit=False)
            pme.type_entreprise = 'client'
            pme.save()
            
            # Créer l'invitation
            invitation: InvitationEntreprise = invitation_form.save(commit=False)
            invitation.organisme_formation = organisme_formation
            invitation.entreprise_client = pme
            invitation.created_by = request.user
            invitation.save()
            
            # Lien d'invitation
            lien = request.build_absolute_uri(f"/invite/{invitation.token}/")
            messages.success(request, f"PME créée et invitation envoyée. Lien: {lien}")
            
            return render(request, 'habilitations_app/invitation_success.html', {
                'entreprise': pme,
                'invitation': invitation,
                'lien': lien,
            })
    else:
        entreprise_form = EntrepriseForm()
        invitation_form = InvitationEntrepriseForm()
    
    return render(request, 'habilitations_app/invitation_create.html', {
        'entreprise_form': entreprise_form,
        'invitation_form': invitation_form,
        'organisme_formation': organisme_formation,
    })


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
