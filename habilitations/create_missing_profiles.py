#!/usr/bin/env python
"""
Script pour créer les ProfilUtilisateur manquants pour tous les utilisateurs existants
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import ProfilUtilisateur

def create_missing_profiles():
    """Créer les profils manquants pour tous les utilisateurs"""
    users_without_profile = []
    
    for user in User.objects.all():
        if not hasattr(user, 'profil'):
            users_without_profile.append(user)
    
    if not users_without_profile:
        print("✓ Tous les utilisateurs ont déjà un profil.")
        return
    
    print(f"Création de {len(users_without_profile)} profil(s) manquant(s)...")
    
    for user in users_without_profile:
        profil = ProfilUtilisateur.objects.create(user=user)
        print(f"  ✓ Profil créé pour : {user.username}")
    
    print(f"\n✓ {len(users_without_profile)} profil(s) créé(s) avec succès.")
    print("\nN'oubliez pas de configurer les rôles et entreprises dans l'admin Django (/admin).")

if __name__ == '__main__':
    create_missing_profiles()
