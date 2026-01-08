"""
Décorateurs et Mixins pour la gestion des rôles et permissions B2B2C
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from .models import ProfilUtilisateur


def role_required(roles):
    """Décorateur pour vérifier le rôle de l'utilisateur
    
    Args:
        roles: str ou list - Rôle(s) autorisé(s)
    """
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                profil = request.user.profil
                if profil.role in roles or profil.est_super_admin:
                    return view_func(request, *args, **kwargs)
            except (AttributeError, ProfilUtilisateur.DoesNotExist):
                pass
            
            messages.error(request, f"Accès réservé aux rôles: {', '.join(roles)}")
            return redirect('home')
        
        return wrapper
    return decorator


def super_admin_required(view_func):
    """Décorateur pour les vues réservées au Super Admin"""
    return role_required(['super_admin'])(view_func)


def admin_of_required(view_func):
    """Décorateur pour les vues réservées aux Admin OF"""
    return role_required(['admin_of'])(view_func)


def secretariat_required(view_func):
    """Décorateur pour les vues réservées au secrétariat OF"""
    return role_required(['secretariat'])(view_func)


def formateur_required(view_func):
    """Décorateur pour les vues réservées aux formateurs OF"""
    return role_required(['formateur'])(view_func)


def responsable_pme_required(view_func):
    """Décorateur pour les vues réservées aux Responsables PME"""
    return role_required(['responsable_pme'])(view_func)


# Anciens décorateurs pour compatibilité
def client_required(view_func):
    """Décorateur pour les vues réservées aux clients (ancien nom)"""
    return role_required(['responsable_pme'])(view_func)


def of_required(view_func):
    """Décorateur pour les vues réservées aux organismes de formation (ancien nom)"""
    return role_required(['admin_of'])(view_func)


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin pour vérifier le rôle dans les vues basées sur des classes"""
    required_role = None
    permission_denied_message = "Accès réservé."
    
    def test_func(self):
        if not self.required_role:
            return True
        
        try:
            profil = self.request.user.profil
            return profil.role == self.required_role
        except ProfilUtilisateur.DoesNotExist:
            return False
    
    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('home')


class ClientRequiredMixin(RoleRequiredMixin):
    """Mixin pour les vues réservées aux clients"""
    required_role = 'client'
    permission_denied_message = "Accès réservé aux clients."


class OFRequiredMixin(RoleRequiredMixin):
    """Mixin pour les vues réservées aux organismes de formation"""
    required_role = 'of'
    permission_denied_message = "Accès réservé aux organismes de formation."
