#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import ProfilUtilisateur, Entreprise, Tenant

# Récupérer ou créer l'entreprise Kompetans
entreprise, created_entreprise = Entreprise.objects.get_or_create(
    nom='Kompetans',
    defaults={
        'type_entreprise': 'of',
        'adresse': '123 rue de la Formation, Paris',
        'telephone': '0123456789',
        'email': 'contact@kompetans.fr'
    }
)
print(f'{"✓ Entreprise créée" if created_entreprise else "✓ Entreprise existante"}: {entreprise.nom}')

# Récupérer ou créer le tenant Kompetans
tenant, created_tenant = Tenant.objects.get_or_create(
    organisme_formation=entreprise,
    defaults={
        'nom_public': 'Kompetans Formation',
        'slug': 'kompetans',
        'actif': True
    }
)
print(f'{"✓ Tenant créé" if created_tenant else "✓ Tenant existant"}: {tenant.nom_public}')

# Mettre à jour les profils des utilisateurs admin_of sans entreprise
for username in ['Kompetans', 'WattElse']:
    try:
        user = User.objects.get(username=username)
        profil = user.profil
        
        # Créer l'entreprise si elle n'existe pas
        if profil.role == 'admin_of' and not profil.entreprise:
            # Récupérer ou créer l'entreprise
            entreprise_user, created_ent = Entreprise.objects.get_or_create(
                nom=username,
                defaults={
                    'type_entreprise': 'of',
                    'adresse': f'Adresse {username}',
                    'telephone': '0123456789',
                    'email': f'contact@{username.lower()}.fr'
                }
            )
            
            # Récupérer ou créer le tenant
            tenant_user, created_ten = Tenant.objects.get_or_create(
                organisme_formation=entreprise_user,
                defaults={
                    'nom_public': f'{username} Formation',
                    'slug': username.lower(),
                    'actif': True
                }
            )
            
            profil.entreprise = entreprise_user
            profil.tenant = tenant_user
            profil.save()
            
            print(f'✓ {username}: Entreprise {"créée" if created_ent else "existante"}, Tenant {"créé" if created_ten else "existant"}')
            print(f'  - Entreprise: {profil.entreprise}')
            print(f'  - Tenant: {profil.tenant}')
    except User.DoesNotExist:
        print(f'✗ Utilisateur {username} non trouvé')
