# habilitations_app/services.py
"""
Services métier pour la gestion des formations et formateurs
"""
from .models import ProfilUtilisateur, FormateurCompetence, FormateurAffectation


def formateurs_of(entreprise):
    """
    Retourne tous les formateurs actifs affectés à cet organisme de formation.
    
    Args:
        entreprise: Instance Entreprise (type_entreprise='of')
    
    Returns:
        QuerySet de ProfilUtilisateur avec role='formateur'
    """
    return ProfilUtilisateur.objects.filter(
        role='formateur',
        affectations__entreprise=entreprise,
        affectations__actif=True,
        actif=True
    ).distinct()


def specialisations_proposees_of(entreprise):
    """
    Retourne les spécialisations proposées par cet OF via TenantFormation.
    
    Args:
        entreprise: Instance Entreprise (type_entreprise='of')
    
    Returns:
        QuerySet de Specialisation
    """
    from .models import Specialisation
    tenant = getattr(entreprise, 'tenant_of', None)
    if not tenant:
        return Specialisation.objects.none()
    return Specialisation.objects.filter(
        propositions_of__tenant=tenant,
        propositions_of__actif=True
    ).distinct()


def sync_formateur_competences(formateur_profil, specialisations_qs):
    """
    Synchronise les compétences d'un formateur avec la liste sélectionnée.
    
    - Ajoute/active FormateurCompetence pour les spécialisations cochées
    - Désactive FormateurCompetence pour les spécialisations décochées
    
    Args:
        formateur_profil: Instance ProfilUtilisateur
        specialisations_qs: QuerySet ou list de Specialisation à activer
    
    Returns:
        dict avec clés 'added', 'updated', 'deactivated'
    """
    selected_ids = set(specialisations_qs.values_list('id', flat=True)) if hasattr(specialisations_qs, 'values_list') else set(s.id for s in specialisations_qs)
    
    existing = FormateurCompetence.objects.filter(formateur_profil=formateur_profil)
    existing_ids = set(existing.values_list('specialisation_id', flat=True))
    
    added = []
    updated = []
    deactivated = []
    
    # Ajouter/activer pour les cochées
    for spec_id in selected_ids:
        comp, created = FormateurCompetence.objects.get_or_create(
            formateur_profil=formateur_profil,
            specialisation_id=spec_id,
            defaults={'actif': True}
        )
        if created:
            added.append(comp)
        elif not comp.actif:
            comp.actif = True
            comp.save(update_fields=['actif'])
            updated.append(comp)
    
    # Désactiver pour les décochées
    for comp in existing:
        if comp.specialisation_id not in selected_ids and comp.actif:
            comp.actif = False
            comp.save(update_fields=['actif'])
            deactivated.append(comp)
    
    return {
        'added': added,
        'updated': updated,
        'deactivated': deactivated
    }