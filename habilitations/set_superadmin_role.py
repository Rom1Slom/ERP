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

# Changer le rôle en super_admin
profil.role = 'super_admin'
profil.entreprise = None  # Super admin n'a pas d'entreprise
profil.tenant = None  # Super admin n'a pas de tenant
profil.save()

print(f'✓ {admin.username} est maintenant Super Admin')
print(f'  Rôle: {profil.get_role_display()}')
