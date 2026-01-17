#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

print("Utilisateurs existants :\n")
for user in User.objects.all():
    try:
        profil = user.profil
        print(f"{user.username:20} role={profil.role:15} entreprise={profil.entreprise} tenant={profil.tenant}")
    except:
        print(f"{user.username:20} [PAS DE PROFIL]")
