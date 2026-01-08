"""
Script pour créer rapidement un utilisateur OF (Organisme de Formation)

Usage:
    python create_of_user.py

Le script vous guidera pour créer :
1. Une entreprise OF (si elle n'existe pas déjà)
2. Un utilisateur avec le rôle admin_of
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from habilitations_app.models import Entreprise, ProfilUtilisateur


def create_of_user():
    """Créer un utilisateur OF de manière interactive"""
    print("=" * 60)
    print("CRÉATION D'UN UTILISATEUR ORGANISME DE FORMATION")
    print("=" * 60)
    
    # 1. Choisir ou créer l'entreprise OF
    print("\n📋 ÉTAPE 1: Entreprise OF")
    print("-" * 60)
    
    of_existants = Entreprise.objects.filter(type_entreprise='of')
    if of_existants.exists():
        print("\nEntreprises OF existantes:")
        for i, of in enumerate(of_existants, 1):
            print(f"  {i}. {of.nom} - {of.ville}")
        
        choix = input("\nUtiliser une entreprise existante ? (numéro) ou 'n' pour nouvelle: ").strip()
        
        if choix.lower() == 'n':
            of = creer_entreprise_of()
        else:
            try:
                index = int(choix) - 1
                of = list(of_existants)[index]
                print(f"\n✓ Entreprise sélectionnée: {of.nom}")
            except (ValueError, IndexError):
                print("❌ Choix invalide. Annulation.")
                return
    else:
        print("\nAucune entreprise OF existante. Création nécessaire.")
        of = creer_entreprise_of()
    
    # 2. Créer l'utilisateur
    print("\n👤 ÉTAPE 2: Utilisateur")
    print("-" * 60)
    
    username = input("Nom d'utilisateur (login): ").strip()
    if User.objects.filter(username=username).exists():
        print(f"❌ L'utilisateur '{username}' existe déjà.")
        return
    
    email = input("Email: ").strip()
    password = input("Mot de passe: ").strip()
    
    first_name = input("Prénom (optionnel): ").strip()
    last_name = input("Nom (optionnel): ").strip()
    
    # 3. Créer tout en transaction
    try:
        with transaction.atomic():
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Créer le profil
            profil = ProfilUtilisateur.objects.create(
                user=user,
                entreprise=of,
                role='admin_of',
                actif=True
            )
            
            print("\n" + "=" * 60)
            print("✅ UTILISATEUR OF CRÉÉ AVEC SUCCÈS!")
            print("=" * 60)
            print(f"\n👤 Utilisateur: {user.username}")
            print(f"📧 Email: {user.email}")
            print(f"🏢 Entreprise: {of.nom}")
            print(f"🎭 Rôle: Administrateur OF")
            print(f"\n🔑 Identifiants de connexion:")
            print(f"   - Login: {username}")
            print(f"   - Mot de passe: {password}")
            print("\n" + "=" * 60)
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la création: {e}")
        import traceback
        traceback.print_exc()


def creer_entreprise_of():
    """Créer une nouvelle entreprise OF"""
    print("\n🏢 Création d'une nouvelle entreprise OF")
    print("-" * 60)
    
    nom = input("Nom de l'organisme de formation: ").strip()
    email = input("Email: ").strip()
    telephone = input("Téléphone: ").strip()
    adresse = input("Adresse: ").strip()
    code_postal = input("Code postal: ").strip()
    ville = input("Ville: ").strip()
    
    of = Entreprise.objects.create(
        nom=nom,
        type_entreprise='of',
        email=email,
        telephone=telephone,
        adresse=adresse,
        code_postal=code_postal,
        ville=ville
    )
    
    print(f"\n✓ Entreprise OF créée: {of.nom}")
    return of


def lister_utilisateurs_of():
    """Lister tous les utilisateurs OF existants"""
    print("\n" + "=" * 60)
    print("UTILISATEURS OF EXISTANTS")
    print("=" * 60)
    
    profils = ProfilUtilisateur.objects.filter(role='admin_of').select_related('user', 'entreprise')
    
    if not profils.exists():
        print("\nAucun utilisateur OF pour le moment.")
    else:
        for profil in profils:
            statut = "✓ Actif" if profil.actif else "✗ Inactif"
            print(f"\n👤 {profil.user.username} ({profil.user.email})")
            print(f"   🏢 {profil.entreprise.nom}")
            print(f"   {statut}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        lister_utilisateurs_of()
    else:
        create_of_user()
