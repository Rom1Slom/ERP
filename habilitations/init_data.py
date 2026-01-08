#!/usr/bin/env python
"""
Script pour initialiser le projet Django avec les données d'exemple
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import Entreprise, Habilitation
from datetime import date

def create_test_data():
    """Crée les données d'exemple"""
    
    # Créer une entreprise
    print("Création de l'entreprise...")
    ent, created = Entreprise.objects.get_or_create(
        nom='ACME Électrique',
        defaults={
            'email': 'contact@acme-electrique.fr',
            'telephone': '01 23 45 67 89',
            'adresse': '123 rue de la Paix',
            'code_postal': '75000',
            'ville': 'Paris'
        }
    )
    if created:
        print("✓ Entreprise créée")
    else:
        print("ℹ Entreprise déjà existante")

    # Créer les habilitations courantes
    habilitations_data = [
        {
            'code': 'B1V',
            'nom': 'Exécution de travaux sous tension - Basse Tension',
            'categorie': '1',
            'niveau': 'Exécutant',
            'savoirs': 'Connaissances techniques BT\nNormes et réglementations\nRisques électriques\nProcédures de sécurité',
            'savoirs_faire': 'Utilisation d\'équipements de protection\nRéalisation de câblages\nTests de sécurité\nMesures électriques'
        },
        {
            'code': 'B1X',
            'nom': 'Travaux de proximité - Basse Tension',
            'categorie': '1',
            'niveau': 'Exécutant',
            'savoirs': 'Sécurité en basse tension\nDéfinitions des zones\nRisques de court-circuit',
            'savoirs_faire': 'Respect des distances\nConnaissance des zones\nProcédures de travail'
        },
        {
            'code': 'B2V',
            'nom': 'Exécution de travaux sous tension - Haute Tension',
            'categorie': '2',
            'niveau': 'Exécutant',
            'savoirs': 'Connaissances techniques HT\nNormes spécifiques HT\nRisques HT\nProcédures emergence HT',
            'savoirs_faire': 'Utilisation équipements HT\nMesures en HT\nConnaissance du matériel'
        },
        {
            'code': 'BR',
            'nom': 'Interventions sur les installations électriques',
            'categorie': '1',
            'niveau': 'Standard',
            'savoirs': 'Principes d\'électricité\nNormes de sécurité\nRisques des installations',
            'savoirs_faire': 'Vérification des installations\nMise en œuvre des protections\nRéparations d\'urgence'
        },
    ]

    print("\nCréation des habilitations...")
    for hab_data in habilitations_data:
        hab, created = Habilitation.objects.get_or_create(
            code=hab_data['code'],
            defaults=hab_data
        )
        if created:
            print(f"✓ Habilitation {hab_data['code']} créée")
        else:
            print(f"ℹ Habilitation {hab_data['code']} déjà existante")

    print("\n" + "="*50)
    print("✓ Initialisation terminée!")
    print("="*50)
    print("\nVous pouvez maintenant:")
    print("1. Accéder à http://127.0.0.1:8000/admin/")
    print("2. Créer des stagiaires")
    print("3. Créer des formations")
    print("4. Gérer les validations et titres")

if __name__ == '__main__':
    create_test_data()
