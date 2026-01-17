#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import ProfilUtilisateur

# Récupérer l'admin
admin = User.objects.get(username='admin')
profil = admin.profil

print(f'User: {admin.username}')
print(f'Rôle actuel: {profil.role} ({profil.get_role_display()})')
print(f'est_super_admin: {profil.est_super_admin}')
print(f'Entreprise: {profil.entreprise}')
print(f'Tenant: {profil.tenant}')
print()

# Forcer le changement
profil.role = 'super_admin'
profil.entreprise = None
profil.tenant = None
profil.save()

print('✓ Rôle changé en super_admin')
print(f'Nouveau rôle: {profil.role} ({profil.get_role_display()})')
print(f'est_super_admin: {profil.est_super_admin}')
