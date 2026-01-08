"""
Script d'initialisation pour les rôles Client et OF
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import Entreprise, ProfilUtilisateur

def init_roles():
    """Initialiser les rôles pour les données existantes"""
    
    # Mettre à jour les entreprises existantes
    for entreprise in Entreprise.objects.all():
        if not entreprise.type_entreprise:
            # Garder le type par défaut 'client'
            entreprise.save()
            print(f"✓ Entreprise mise à jour: {entreprise.nom}")
    
    # Mettre à jour les profils utilisateur existants
    for profil in ProfilUtilisateur.objects.all():
        if not profil.role or profil.role == 'client':
            profil.role = 'client'
            profil.save()
            print(f"✓ Profil utilisateur mis à jour: {profil.user.username} -> Client")
    
    print("\n✓ Initialisation des rôles terminée!")
    
    # Afficher un résumé
    clients_count = ProfilUtilisateur.objects.filter(role='client').count()
    of_count = ProfilUtilisateur.objects.filter(role='of').count()
    
    print(f"\nRésumé:")
    print(f"  - Clients: {clients_count}")
    print(f"  - Organismes de Formation: {of_count}")


def create_test_data():
    """Créer des données de test"""
    
    # Créer une entreprise de formation
    kompetans, created = Entreprise.objects.get_or_create(
        nom='Kompetans.fr',
        defaults={
            'type_entreprise': 'of',
            'email': 'contact@kompetans.fr',
            'telephone': '01.00.00.00.00',
            'adresse': '123 Rue de la Formation',
            'code_postal': '75000',
            'ville': 'Paris',
        }
    )
    
    if created:
        print(f"✓ Entreprise créée: {kompetans.nom} (OF)")
    else:
        kompetans.type_entreprise = 'of'
        kompetans.save()
        print(f"✓ Entreprise mise à jour: {kompetans.nom} (OF)")


if __name__ == '__main__':
    print("=== Initialisation des rôles ===\n")
    
    # Créer les données de test
    create_test_data()
    
    # Initialiser les rôles
    init_roles()
    
    print("\n✓ Initialisation complète!")
    print("\nProchaines étapes:")
    print("1. Accédez à l'administration: http://localhost:8000/admin/")
    print("2. Créez/modifiez les profils utilisateur avec les bons rôles")
    print("3. Connectez-vous pour vérifier la redirection par rôle")
