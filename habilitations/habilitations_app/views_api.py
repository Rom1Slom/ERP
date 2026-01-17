"""
API AJAX pour le catalogue de formations
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import TypeFormation, Specialisation


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

