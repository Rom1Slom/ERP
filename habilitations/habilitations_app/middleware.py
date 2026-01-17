"""Middleware et helpers d'isolation multi-tenant B2B2C.

Supporte les rôles super_admin, admin_of, secretariat, formateur, responsable_pme, stagiaire.
Résout le tenant depuis le sous-domaine ou le profil utilisateur et injecte des helpers sur la requête.
"""

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from .models import Tenant


class MultiTenantMiddleware:
    """Middleware pour l'isolation multi-tenant"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.tenant = resolve_tenant_from_host(request)

        # Récupération du profil utilisateur
        if request.user.is_authenticated:
            try:
                profil = request.user.profil
                request.profil = profil
                # Si le profil n'a pas de tenant explicite, tenter de dériver depuis l'entreprise OF
                if not request.tenant:
                    request.tenant = (
                        getattr(profil, 'tenant', None)
                        or getattr(profil.entreprise, 'tenant_of', None)
                        or getattr(profil.entreprise, 'tenant', None)
                    )

                request.is_super_admin = profil.est_super_admin
                request.is_admin_of = profil.est_admin_of
                request.is_secretariat = profil.est_secretariat
                request.is_formateur = profil.est_formateur
                request.is_responsable_pme = profil.est_responsable_pme
                request.is_stagiaire = profil.est_stagiaire
            except Exception:
                request.profil = None
                request.is_super_admin = False
                request.is_admin_of = False
                request.is_secretariat = False
                request.is_formateur = False
                request.is_responsable_pme = False
                request.is_stagiaire = False
        else:
            request.profil = None
            request.is_super_admin = False
            request.is_admin_of = False
            request.is_secretariat = False
            request.is_formateur = False
            request.is_responsable_pme = False
            request.is_stagiaire = False
        
        response = self.get_response(request)
        return response


def resolve_tenant_from_host(request):
    """Résout le tenant à partir du sous-domaine ou du domaine complet."""

    host = request.get_host().split(':')[0].lower()
    if host in ['localhost', '127.0.0.1']:
        return None

    base_domain = getattr(settings, 'SITE_DOMAIN', '').lower()
    subdomain = None

    if base_domain and host.endswith(base_domain):
        parts = host.replace(base_domain, '').strip('.')
        subdomain = parts.split('.')[0] if parts else None
    else:
        # Domaine dédié par tenant (domaine plein)
        subdomain = None

    # Cherche par domaine dédié
    tenant = Tenant.objects.filter(domaine__iexact=host, actif=True).first()
    if tenant:
        return tenant

    if subdomain:
        return Tenant.objects.filter(slug=subdomain, actif=True).first()
    return None


def get_accessible_stagiaires(user):
    """Retourne la liste des stagiaires accessibles selon le rôle de l'utilisateur"""
    from .models import Stagiaire
    
    if not user.is_authenticated:
        return Stagiaire.objects.none()
    
    try:
        profil = user.profil
    except:
        return Stagiaire.objects.none()
    
    # Super Admin : tous les stagiaires
    if profil.est_super_admin:
        return Stagiaire.objects.all()
    
    tenant = getattr(profil, 'tenant', None)
    
    # Admin OF / Secrétariat : stagiaires du tenant
    if profil.est_admin_of or profil.est_secretariat:
        qs = Stagiaire.objects.all()
        if tenant:
            qs = qs.filter(tenant=tenant)
        else:
            qs = qs.filter(organisme_formation=profil.entreprise)
        return qs

    # Formateur : stagiaires présents dans ses sessions
    if profil.est_formateur:
        return Stagiaire.objects.filter(formations__session__formateur=user).distinct()
    
    # Responsable PME : employés de sa PME uniquement
    if profil.est_responsable_pme:
        return Stagiaire.objects.filter(entreprise=profil.entreprise)
    
    # Stagiaire : son propre dossier uniquement
    if profil.est_stagiaire:
        try:
            return Stagiaire.objects.filter(user=user)
        except:
            return Stagiaire.objects.none()
    
    return Stagiaire.objects.none()


def get_accessible_entreprises(user):
    """Retourne la liste des entreprises accessibles selon le rôle de l'utilisateur"""
    from .models import Entreprise
    
    if not user.is_authenticated:
        return Entreprise.objects.none()
    
    try:
        profil = user.profil
    except:
        return Entreprise.objects.none()
    
    # Super Admin : toutes les entreprises
    if profil.est_super_admin:
        return Entreprise.objects.all()
    
    tenant = getattr(profil, 'tenant', None)

    # Admin OF / Secrétariat : son OF + Clients rattachés au tenant
    if profil.est_admin_of or profil.est_secretariat:
        from django.db.models import Q
        qs = Entreprise.objects.filter(
            Q(pk=profil.entreprise.pk) |
            Q(type_entreprise='client', stagiaires__organisme_formation=profil.entreprise)
        )
        if tenant:
            qs = qs.filter(Q(tenant=tenant) | Q(pk=profil.entreprise.pk))
        return qs.distinct()

    # Formateur : accès lecture aux PME des stagiaires de ses sessions
    if profil.est_formateur:
        return Entreprise.objects.filter(stagiaires__formations__session__formateur=user).distinct()
    
    # Responsable PME : sa PME uniquement
    if profil.est_responsable_pme:
        return Entreprise.objects.filter(pk=profil.entreprise.pk)
    
    # Stagiaire : aucune entreprise
    return Entreprise.objects.none()


def get_accessible_demandes_formation(user):
    """Retourne les demandes de formation accessibles selon le rôle"""
    from .models import DemandeFormation
    
    if not user.is_authenticated:
        return DemandeFormation.objects.none()
    
    try:
        profil = user.profil
    except:
        return DemandeFormation.objects.none()
    
    # Super Admin : toutes les demandes
    if profil.est_super_admin:
        return DemandeFormation.objects.all()
    
    tenant = getattr(profil, 'tenant', None)

    # Admin OF / Secrétariat : demandes reçues par le tenant
    if profil.est_admin_of or profil.est_secretariat:
        qs = DemandeFormation.objects.filter(organisme_formation=profil.entreprise)
        if tenant:
            qs = qs.filter(tenant=tenant)
        return qs

    # Formateur : lecture seule sur les demandes déjà intégrées dans ses sessions
    if profil.est_formateur:
        return DemandeFormation.objects.filter(session_creee__formateur=user)
    
    # Responsable PME : demandes émises par sa PME
    if profil.est_responsable_pme:
        return DemandeFormation.objects.filter(entreprise_demandeuse=profil.entreprise)
    
    # Stagiaire : aucune demande
    return DemandeFormation.objects.none()
