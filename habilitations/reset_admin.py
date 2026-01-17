#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import ProfilUtilisateur

# Supprimer tous les profils orphelins
ProfilUtilisateur.objects.filter(user__isnull=True).delete()

# Supprimer l'ancien admin et son profil
User.objects.filter(username='admin').delete()

# Créer le nouveau superadmin
u = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')

# Créer ou mettre à jour son profil
profil, created = ProfilUtilisateur.objects.get_or_create(
    user=u,
    defaults={'role': 'super_admin', 'actif': True}
)

if not created:
    profil.role = 'super_admin'
    profil.actif = True
    profil.save()

print(f'✓ Superuser créé: {u.username} avec password: admin123')
print(f'✓ Profil créé avec rôle: {profil.get_role_display()}')
