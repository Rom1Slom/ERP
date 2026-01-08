"""
Script de migration pour passer à l'architecture B2B2C

Ce script :
1. Crée un OF par défaut si aucun OF n'existe
2. Migre les stagiaires existants vers le nouvel modèle
3. Crée les profils utilisateurs manquants
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from habilitations_app.models import Entreprise, Stagiaire, ProfilUtilisateur
from django.contrib.auth.models import User


@transaction.atomic
def migrate_to_b2b2c():
    """Migration vers l'architecture B2B2C"""
    
    print("=" * 60)
    print("MIGRATION VERS ARCHITECTURE B2B2C")
    print("=" * 60)
    
    # 1. Créer un OF par défaut si nécessaire
    of_default, created = Entreprise.objects.get_or_create(
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
    
    if created:
        print(f"\n✓ OF par défaut créé : {of_default.nom}")
    else:
        print(f"\n✓ OF par défaut existant : {of_default.nom}")
    
    # 2. Compter les entreprises par type
    nb_of = Entreprise.objects.filter(type_entreprise='of').count()
    nb_pme = Entreprise.objects.filter(type_entreprise='client').count()
    
    print(f"\n📊 Statistiques entreprises :")
    print(f"   - OF : {nb_of}")
    print(f"   - PME : {nb_pme}")
    
    # 3. Afficher le nombre de stagiaires
    nb_stagiaires = Stagiaire.objects.count()
    print(f"   - Stagiaires : {nb_stagiaires}")
    
    # 4. Créer des profils utilisateurs pour les users sans profil
    users_sans_profil = User.objects.filter(profil__isnull=True)
    nb_profils_crees = 0
    
    for user in users_sans_profil:
        if user.is_superuser:
            ProfilUtilisateur.objects.create(
                user=user,
                entreprise=None,
                role='super_admin',
                actif=True
            )
            nb_profils_crees += 1
            print(f"\n✓ Profil Super Admin créé pour : {user.username}")
    
    if nb_profils_crees == 0:
        print(f"\n   - Aucun profil utilisateur à créer")
    else:
        print(f"\n✓ {nb_profils_crees} profil(s) créé(s)")
    
    print("\n" + "=" * 60)
    print("PRÊT POUR LA MIGRATION")
    print("=" * 60)
    print(f"\nOF par défaut ID : {of_default.id}")
    print("\nProchaines étapes :")
    print("1. Assurez-vous que c'est correct")
    print("2. Lancez : python manage.py makemigrations")
    print("3. Quand demandé, utilisez l'ID : {}".format(of_default.id))
    print("4. Lancez : python manage.py migrate")
    print("\n" + "=" * 60)
    
    return of_default.id


if __name__ == "__main__":
    try:
        of_id = migrate_to_b2b2c()
        print(f"\n✅ Script terminé avec succès!")
        print(f"   Utilisez l'ID {of_id} comme valeur par défaut pour organisme_formation")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
