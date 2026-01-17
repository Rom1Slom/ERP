"""
Vues pour la gestion du catalogue de formations (TenantFormation)
Admin OF et secrétariat uniquement
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction

from .decorators import role_required
from .models import TenantFormation, TypeFormation, Specialisation, Tenant
from .forms_catalogue import TenantFormationForm


@login_required
@role_required(['admin_of', 'secretariat'])
def catalogue_formations_list(request):
    """Récupère le catalogue de formations pour l'OF courant (AJAX)"""
    profil = request.user.profil
    tenant = profil.tenant
    
    if not tenant:
        return JsonResponse({'error': 'Tenant non trouvé'}, status=400)
    
    formations = TenantFormation.objects.filter(tenant=tenant).select_related('type_formation')
    
    data = {
        'formations': [
            {
                'id': f.id,
                'nom': f.type_formation.nom,
                'code': f.type_formation.code,
                'actif': f.actif,
                'specialisations': list(f.spécialisations.values_list('code', flat=True)),
                'date_activation': f.date_activation.strftime('%d/%m/%Y'),
            }
            for f in formations
        ]
    }
    return JsonResponse(data)


@login_required
@role_required(['admin_of', 'secretariat'])
@require_POST
def catalogue_formations_add(request):
    """Ajoute une formation au catalogue (AJAX)"""
    profil = request.user.profil
    tenant = profil.tenant
    
    if not tenant:
        return JsonResponse({'error': 'Tenant non trouvé'}, status=400)
    
    with transaction.atomic():
        type_formation_id = request.POST.get('type_formation')
        
        # NOUVEAU : Si "autre", créer TypeFormation custom
        if type_formation_id == 'autre':
            custom_nom = request.POST.get('custom_nom', '').strip()
            if not custom_nom:
                return JsonResponse({
                    'success': False,
                    'errors': {'custom_nom': ['Ce champ est requis']}
                }, status=400)
            
            # Générer un code unique
            import re
            code = re.sub(r'[^a-zA-Z0-9]', '', custom_nom)[:20].upper()
            code = f"CUSTOM_{tenant.id}_{code}"
            
            # Créer TypeFormation custom
            type_formation = TypeFormation.objects.create(
                code=code,
                nom=custom_nom,
                created_by_tenant=tenant
            )
        else:
            # Formation globale existante
            try:
                type_formation = TypeFormation.objects.get(pk=type_formation_id)
            except TypeFormation.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'errors': {'type_formation': ['Formation non trouvée']}
                }, status=400)
        
        # Récupérer spécialisations (uniquement si formation existante)
        specialisations_ids = request.POST.getlist('spécialisations')
        # Convertir en entiers et filtrer les valeurs invalides
        specialisations_ids = []
        for sid in request.POST.getlist('spécialisations'):
            if sid and sid != '[]':
                try:
                    specialisations_ids.append(int(sid))
                except (ValueError, TypeError):
                    pass
        specialisations = Specialisation.objects.filter(id__in=specialisations_ids)
        
        # Vérifier que des spécialisations sont sélectionnées
        if not specialisations.exists():
            return JsonResponse({
                'success': False,
                'errors': {'spécialisations': ['Sélectionnez au moins une spécialisation']}
            }, status=400)
        
        # Vérifier si cette combinaison exacte existe déjà
        specialisations_ids_set = set(specialisations_ids)
        existing_formations = TenantFormation.objects.filter(
            tenant=tenant,
            type_formation=type_formation
        )
        
        for existing in existing_formations:
            existing_specs = set(existing.spécialisations.values_list('id', flat=True))
            if existing_specs == specialisations_ids_set:
                return JsonResponse({
                    'success': False,
                    'errors': {'global': ['Cette formation avec ces spécialisations existe déjà dans votre catalogue']}
                }, status=400)
        
        # Créer NOUVELLE entrée (pas de get_or_create pour permettre plusieurs combinaisons)
        tenant_form = TenantFormation.objects.create(
            tenant=tenant,
            type_formation=type_formation,
            actif=True
        )
        
        # Assigner spécialisations
        tenant_form.spécialisations.set(specialisations)
        
        messages.success(request, f"Formation '{type_formation.nom}' ajoutée au catalogue")
    
    return JsonResponse({
        'success': True,
        'formation_id': tenant_form.id,
        'nom': type_formation.nom
    })

@login_required
@role_required(['admin_of', 'secretariat'])
@require_POST
def catalogue_formations_delete(request, pk):
    """Supprime une formation du catalogue"""
    profil = request.user.profil
    tenant = profil.tenant
    
    if not tenant:
        messages.error(request, "Tenant non trouvé")
        return redirect('dashboard_admin_of')
    
    tenant_form = get_object_or_404(TenantFormation, pk=pk, tenant=tenant)
    nom_formation = tenant_form.type_formation.nom
    
    tenant_form.delete()
    messages.success(request, f"Formation '{nom_formation}' supprimée du catalogue")
    
    return redirect('dashboard_admin_of')


@login_required
@role_required(['admin_of', 'secretariat'])
@require_POST
def catalogue_formations_toggle(request, pk):
    """Active/désactive une formation du catalogue"""
    profil = request.user.profil
    tenant = profil.tenant
    
    if not tenant:
        return JsonResponse({'error': 'Tenant non trouvé'}, status=400)
    
    tenant_form = get_object_or_404(TenantFormation, pk=pk, tenant=tenant)
    tenant_form.actif = not tenant_form.actif
    tenant_form.save(update_fields=['actif'])
    
    return JsonResponse({
        'success': True,
        'actif': tenant_form.actif,
        'statut': 'Actif' if tenant_form.actif else 'Inactif'
    })
