"""
Script pour tester rapidement les rôles et l'authentification
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import Entreprise, ProfilUtilisateur

def create_test_users():
    """Créer des utilisateurs de test pour les 2 rôles"""
    
    print("=== Création d'utilisateurs de test ===\n")
    
    # Créer les entreprises
    client_ent, _ = Entreprise.objects.get_or_create(
        nom='ACME Corp',
        defaults={
            'type_entreprise': 'client',
            'email': 'contact@acme.fr',
            'telephone': '01.00.00.00.01',
            'adresse': '10 Rue de la Paix',
            'code_postal': '75001',
            'ville': 'Paris',
        }
    )
    print(f"✓ Entreprise Client créée: {client_ent.nom}")
    
    of_ent, created = Entreprise.objects.get_or_create(
        nom='Kompetans.fr',
        defaults={
            'type_entreprise': 'of',
            'email': 'contact@kompetans.fr',
            'telephone': '01.00.00.00.02',
            'adresse': '123 Avenue de la Formation',
            'code_postal': '75002',
            'ville': 'Paris',
        }
    )
    if created:
        print(f"✓ Entreprise OF créée: {of_ent.nom}")
    else:
        of_ent.type_entreprise = 'of'
        of_ent.save()
        print(f"✓ Entreprise OF mise à jour: {of_ent.nom}")
    
    print()
    
    # Créer les utilisateurs clients
    client_user, created = User.objects.get_or_create(
        username='client_user',
        defaults={
            'email': 'client@acme.fr',
            'first_name': 'Jean',
            'last_name': 'Dupont',
        }
    )
    if created:
        client_user.set_password('password123')
        client_user.save()
        print(f"✓ Utilisateur Client créé: {client_user.username}")
    else:
        print(f"✓ Utilisateur Client existe: {client_user.username}")
    
    # Créer le profil client
    profil_client, created = ProfilUtilisateur.objects.get_or_create(
        user=client_user,
        defaults={
            'entreprise': client_ent,
            'role': 'client',
        }
    )
    if created:
        print(f"  → ProfilUtilisateur créé: {profil_client.user.username} (Client)")
    else:
        profil_client.role = 'client'
        profil_client.save()
        print(f"  → ProfilUtilisateur mis à jour: {profil_client.user.username} (Client)")
    
    print()
    
    # Créer les utilisateurs OF
    of_user, created = User.objects.get_or_create(
        username='of_user',
        defaults={
            'email': 'formateur@kompetans.fr',
            'first_name': 'Marie',
            'last_name': 'Martin',
        }
    )
    if created:
        of_user.set_password('password123')
        of_user.save()
        print(f"✓ Utilisateur OF créé: {of_user.username}")
    else:
        print(f"✓ Utilisateur OF existe: {of_user.username}")
    
    # Créer le profil OF
    profil_of, created = ProfilUtilisateur.objects.get_or_create(
        user=of_user,
        defaults={
            'entreprise': of_ent,
            'role': 'of',
        }
    )
    if created:
        print(f"  → ProfilUtilisateur créé: {profil_of.user.username} (OF)")
    else:
        profil_of.role = 'of'
        profil_of.save()
        print(f"  → ProfilUtilisateur mis à jour: {profil_of.user.username} (OF)")
    
    print()
    print("=" * 50)
    print("UTILISATEURS DE TEST CRÉÉS AVEC SUCCÈS")
    print("=" * 50)
    print()
    print("Identifiants Client:")
    print(f"  Pseudo: client_user")
    print(f"  Mot de passe: password123")
    print()
    print("Identifiants OF:")
    print(f"  Pseudo: of_user")
    print(f"  Mot de passe: password123")
    print()
    print("Prochaines étapes:")
    print("1. Lancez le serveur: python manage.py runserver")
    print("2. Allez à: http://localhost:8000/accounts/login/")
    print("3. Connectez-vous avec client_user -> Dashboard Client")
    print("4. Connectez-vous avec of_user -> Dashboard OF")
    print()


if __name__ == '__main__':
    create_test_users()
