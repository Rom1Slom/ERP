"""
Créer un super admin avec profil
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from habilitations_app.models import ProfilUtilisateur

@transaction.atomic
def create_super_admin():
    # Créer ou récupérer le superuser
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@kompetans.fr',
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'Super',
            'last_name': 'Admin',
        }
    )
    
    if created or not user.check_password('admin123'):
        user.set_password('admin123')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print("✓ Super utilisateur créé/mis à jour : admin / admin123")
    else:
        print("✓ Super utilisateur existant : admin")
    
    # Créer ou récupérer le profil super_admin
    profil, profil_created = ProfilUtilisateur.objects.get_or_create(
        user=user,
        defaults={
            'entreprise': None,  # Pas d'entreprise pour super admin
            'role': 'super_admin',
            'actif': True
        }
    )
    
    if profil_created:
        print("✓ Profil Super Admin créé")
    else:
        # Mettre à jour si nécessaire
        profil.entreprise = None
        profil.role = 'super_admin'
        profil.actif = True
        profil.save()
        print("✓ Profil Super Admin mis à jour")
    
    print("\n" + "="*60)
    print("SUPER ADMIN PRÊT")
    print("="*60)
    print(f"Login        : admin")
    print(f"Password     : admin123")
    print(f"Rôle         : Super Admin (Éditeur SaaS)")
    print(f"Admin Django : http://127.0.0.1:8000/admin/")
    print(f"Dashboard    : http://127.0.0.1:8000/")
    print("="*60)
    print("\nVous pouvez maintenant :")
    print("1. Créer des entreprises OF")
    print("2. Créer des utilisateurs OF (admin_of)")
    print("3. Gérer toute la plateforme")

if __name__ == "__main__":
    create_super_admin()
