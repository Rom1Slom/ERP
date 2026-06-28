"""
API AJAX pour le catalogue de formations
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import TypeFormation, Specialisation
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST


@login_required
def api_type_formations(request):
    """Retourne tous les types de formations avec leurs spécialisations (AJAX)"""
    profil = request.user.profil
    tenant = profil.tenant
    
    # Formations globales + formations custom de cet OF
    types = TypeFormation.objects.filter(
        Q(created_by_tenant__isnull=True) |  # Globales
        Q(created_by_tenant=tenant)           # Custom de cet OF
    )
    
    data = {
        'types': [
            {
                'id': t.id,
                'nom': t.nom,
                'code': t.code,
                'is_custom': t.created_by_tenant is not None,
                'spécialisations': [
                    {
                        'id': s.id,
                        'code': s.code,
                        'nom': s.nom
                    }
                    for s in t.specialisations.all()
                ]
            }
            for t in types
        ],
        # NOUVEAU : Option "Autre"
        'allow_custom': True
    }
    return JsonResponse(data)


@login_required
def api_type_formation_specialisations(request, type_id):
    """Retourne les spécialisations d'un type de formation (AJAX)"""
    type_formation = get_object_or_404(TypeFormation, pk=type_id)
    
    specialisations = type_formation.specialisations.all()
    
    data = {
        'type_formation': {
            'id': type_formation.id,
            'nom': type_formation.nom,
            'code': type_formation.code,
        },
        'spécialisations': [
            {
                'id': s.id,
                'code': s.code,
                'nom': s.nom,
                'description': s.description or ''
            }
            for s in specialisations
        ]
    }
    return JsonResponse(data)



@require_POST
@csrf_protect
def api_add_specialisation(request):
    code = request.POST.get('code')
    nom = request.POST.get('nom')
    type_id = request.POST.get('type_formation')
    errors = {}
    if not code:
        errors['code'] = ['Champ requis']
    if not nom:
        errors['nom'] = ['Champ requis']
    if not type_id:
        errors['type_formation'] = ['Champ requis']
    if errors:
        return JsonResponse({'success': False, 'errors': errors})
    try:
        type_obj = TypeFormation.objects.get(id=type_id)
        from django.db import IntegrityError
        try:
            spec = Specialisation.objects.create(code=code, nom=nom, type_formation=type_obj)
            return JsonResponse({'success': True, 'id': spec.id})
        except IntegrityError:
            return JsonResponse({'success': False, 'errors': {'__all__': ['Cette spécialisation existe déjà pour ce type de formation.']}})
    except TypeFormation.DoesNotExist:
        return JsonResponse({'success': False, 'errors': {'type_formation': ['Type introuvable']}})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})