"""
Créer rapidement un utilisateur OF de test
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from habilitations_app.models import Entreprise, ProfilUtilisateur

@transaction.atomic
def create_test_of():
    # Récupérer ou créer l'OF Kompetans
    of, created = Entreprise.objects.get_or_create(
        nom="Kompetans Formation",
        defaults={
            'type_entreprise': 'of',
            'email': 'contact@kompetans.fr',
            'telephone': '0102030405',
            'adresse': '123 Rue de la Formation',
            'code_postal': '75001',
            'ville': 'Paris',
        }
    )
    
    # Créer ou récupérer l'utilisateur
    user, user_created = User.objects.get_or_create(
        username='admin_of',
        defaults={
            'email': 'admin@kompetans.fr',
            'first_name': 'Admin',
            'last_name': 'OF',
        }
    )
    
    if user_created:
        user.set_password('admin123')
        user.save()
        print("✓ Utilisateur créé : admin_of / admin123")
    else:
        print("✓ Utilisateur existant : admin_of")
    
    # Créer ou récupérer le profil
    profil, profil_created = ProfilUtilisateur.objects.get_or_create(
        user=user,
        defaults={
            'entreprise': of,
            'role': 'admin_of',
            'actif': True
        }
    )
    
    if profil_created:
        print(f"✓ Profil créé pour {of.nom}")
    else:
        # Mettre à jour si nécessaire
        profil.entreprise = of
        profil.role = 'admin_of'
        profil.actif = True
        profil.save()
        print(f"✓ Profil mis à jour pour {of.nom}")
    
    print("\n" + "="*50)
    print("UTILISATEUR OF DE TEST PRÊT")
    print("="*50)
    print(f"Login    : admin_of")
    print(f"Password : admin123")
    print(f"OF       : {of.nom}")
    print(f"URL      : http://127.0.0.1:8000/")
    print("="*50)

if __name__ == "__main__":
    create_test_of()
