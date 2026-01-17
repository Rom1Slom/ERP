"""
Vues pour la gestion des formateurs (admin_of et secretariat)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction

from .decorators import role_required
from .models import ProfilUtilisateur, FormateurAffectation, FormateurCompetence, Specialisation
from .forms import FormateurForm, FormateurCompetencesForm
from .services import formateurs_of, specialisations_proposees_of, sync_formateur_competences


@login_required
@role_required(['admin_of', 'secretariat'])
def formateurs_list(request):
    """Liste les formateurs affectés à l'OF courant"""
    profil = request.user.profil
    of = profil.entreprise
    
    if not of:
        messages.error(request, "Votre profil n'est pas associé à un organisme de formation.")
        return redirect('home')
    
    # Récupérer les formateurs affectés
    formateurs = formateurs_of(of)
    
    context = {
        'formateurs': formateurs,
        'of': of,
    }
    return render(request, 'habilitations_app/formateurs_list.html', context)


@login_required
@role_required(['admin_of', 'secretariat'])
def formateur_edit(request, pk=None):
    """Créer ou modifier un formateur"""
    profil = request.user.profil
    of = profil.entreprise
    tenant = profil.tenant
    
    if not of:
        messages.error(request, "Votre profil n'est pas associé à un organisme de formation.")
        return redirect('home')
    
    # Récupérer spécialisations disponibles pour l'OF
    specs_qs = specialisations_proposees_of(of)
    
    # Si édition, récupérer le formateur existant
    existing_formateur = None
    if pk:
        existing_formateur = get_object_or_404(
            ProfilUtilisateur,
            pk=pk,
            role='formateur',
            affectations__entreprise=of
        )
    
    if request.method == 'POST':
        form = FormateurForm(request.POST)
        comp_form = FormateurCompetencesForm(request.POST, specialisations_qs=specs_qs)
        
        if form.is_valid() and comp_form.is_valid():
            with transaction.atomic():
                # Créer ou récupérer l'utilisateur
                if form.cleaned_data['user_id']:
                    user = form.cleaned_data['user_id']
                else:
                    # Créer un nouvel utilisateur
                    email = form.cleaned_data['email']
                    user, created = User.objects.get_or_create(
                        username=email,
                        defaults={
                            'email': email,
                            'first_name': form.cleaned_data['first_name'],
                            'last_name': form.cleaned_data['last_name'],
                        }
                    )
                    if created:
                        # Générer un mot de passe aléatoire
                        pwd = User.objects.make_random_password()
                        user.set_password(pwd)
                        user.save()
                        messages.info(request, f"Nouvel utilisateur créé. Mot de passe initial: {pwd}")
                
                # Créer/mettre à jour le profil
                prof, _ = ProfilUtilisateur.objects.get_or_create(
                    user=user,
                    defaults={'role': 'formateur', 'actif': form.cleaned_data['actif']}
                )
                prof.role = 'formateur'
                prof.actif = form.cleaned_data['actif']
                prof.save(update_fields=['role', 'actif'])
                
                # Créer/mettre à jour l'affectation
                affectation, _ = FormateurAffectation.objects.get_or_create(
                    formateur=prof,
                    entreprise=of,
                    defaults={'actif': form.cleaned_data['actif']}
                )
                affectation.actif = form.cleaned_data['actif']
                affectation.save(update_fields=['actif'])
                
                # Synchroniser les compétences
                selected_specs = comp_form.cleaned_data['spécialisations']
                sync_formateur_competences(prof, selected_specs)
                
                messages.success(request, "Formateur enregistré.")
                return redirect('formateurs_list')
    else:
        # Pré-remplir le formulaire en édition
        initial = {}
        comp_initial = []
        
        if existing_formateur:
            user = existing_formateur.user
            initial.update({
                'user_id': user,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'telephone': getattr(existing_formateur, 'telephone', ''),
                'actif': existing_formateur.actif,
            })
            # Récupérer les spécialisations actuelles
            comp_initial = list(
                FormateurCompetence.objects.filter(
                    formateur_profil=existing_formateur,
                    actif=True,
                    specialisation__in=specs_qs
                ).values_list('specialisation_id', flat=True)
            )
        
        form = FormateurForm(initial=initial)
        comp_form = FormateurCompetencesForm(
            initial={'spécialisations': comp_initial},
            specialisations_qs=specs_qs
        )
    
    context = {
        'form': form,
        'comp_form': comp_form,
        'editing': existing_formateur is not None,
        'of': of,
    }
    return render(request, 'habilitations_app/formateur_form.html', context)


@login_required
@role_required(['admin_of', 'secretariat'])
def formateur_toggle(request, pk):
    """Activer/désactiver un formateur"""
    profil = request.user.profil
    of = profil.entreprise
    
    if not of:
        messages.error(request, "Votre profil n'est pas associé à un organisme de formation.")
        return redirect('home')
    
    formateur = get_object_or_404(
        ProfilUtilisateur,
        pk=pk,
        role='formateur',
        affectations__entreprise=of
    )
    
    # Toggle actif
    formateur.actif = not formateur.actif
    formateur.save(update_fields=['actif'])
    
    # Mettre à jour aussi l'affectation et les compétences
    FormateurAffectation.objects.filter(
        formateur=formateur,
        entreprise=of
    ).update(actif=formateur.actif)
    
    FormateurCompetence.objects.filter(
        formateur_profil=formateur
    ).update(actif=formateur.actif)
    
    status = "activé" if formateur.actif else "désactivé"
    messages.success(request, f"Formateur {status}.")
    return redirect('formateurs_list')
