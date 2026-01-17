#!/usr/bin/env python
"""
Script pour configurer le profil de l'utilisateur Kompetans comme admin OF
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import ProfilUtilisateur, Entreprise, Tenant

def configure_kompetans():
    """Configurer le profil Kompetans comme admin OF"""
    
    # Trouver l'utilisateur Kompetans
    try:
        user = User.objects.get(username='Kompetans')
    except User.DoesNotExist:
        print("❌ Utilisateur 'Kompetans' introuvable.")
        return
    
    # Trouver l'entreprise Kompetans (OF)
    entreprise = Entreprise.objects.filter(
        type_entreprise='of',
        nom__icontains='Kompetans'
    ).first()
    
    if not entreprise:
        print("❌ Entreprise OF 'Kompetans' introuvable.")
        print("\nVeuillez créer l'entreprise Kompetans dans l'admin Django :")
        print("  - Type: Organisme de Formation (of)")
        print("  - Nom: Kompetans Formation (ou similaire)")
        return
    
    # Trouver ou créer le tenant
    tenant = None
    if hasattr(entreprise, 'tenant_of'):
        tenant = entreprise.tenant_of
    else:
        # Créer un tenant pour Kompetans si nécessaire
        print(f"⚠️  Aucun tenant trouvé pour {entreprise.nom}")
        print("   Veuillez créer un Tenant dans l'admin Django associé à cette entreprise.")
    
    # Mettre à jour le profil
    profil = user.profil
    profil.role = 'admin_of'
    profil.entreprise = entreprise
    profil.tenant = tenant
    profil.actif = True
    profil.save()
    
    print(f"✓ Profil de {user.username} configuré avec succès !")
    print(f"  - Rôle: Administrateur OF")
    print(f"  - Entreprise: {entreprise.nom}")
    print(f"  - Tenant: {tenant.nom_public if tenant else 'Non configuré'}")
    print(f"\n{user.username} peut maintenant accéder au dashboard OF.")

if __name__ == '__main__':
    configure_kompetans()
