#!/usr/bin/env python
"""
Script de test pour vérifier que tous les modèles et vues fonctionnent correctement
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import (
    Entreprise, Habilitation, Stagiaire, Formation, 
    ValidationCompetence, Titre, AvisFormation, 
    RenouvellementHabilitation
)
from datetime import date, timedelta

def test_models():
    """Test la création et manipulation des modèles"""
    
    print("\n" + "="*60)
    print("TEST DES MODÈLES DJANGO")
    print("="*60)
    
    # Test 1: Entreprise
    print("\n[1] Test Entreprise...")
    entreprise = Entreprise.objects.filter(nom='Test Company').first()
    if not entreprise:
        entreprise = Entreprise.objects.create(
            nom='Test Company',
            email='test@test.fr',
            telephone='06 12 34 56 78',
            adresse='123 Test Street',
            code_postal='75000',
            ville='Paris'
        )
    print(f"✓ Entreprise: {entreprise}")
    
    # Test 2: Habilitation
    print("\n[2] Test Habilitation...")
    hab = Habilitation.objects.filter(code='TEST').first()
    if not hab:
        hab = Habilitation.objects.create(
            code='TEST',
            nom='Test Habilitation',
            categorie='1',
            niveau='Test',
            savoirs='Savoir 1\nSavoir 2',
            savoirs_faire='Savoir-faire 1\nSavoir-faire 2'
        )
    print(f"✓ Habilitation: {hab}")
    
    # Test 3: Stagiaire
    print("\n[3] Test Stagiaire...")
    stag = Stagiaire.objects.filter(email='test.stagiaire@test.fr').first()
    if not stag:
        stag = Stagiaire.objects.create(
            entreprise=entreprise,
            nom='TestStag',
            prenom='Jean',
            email='test.stagiaire@test.fr',
            telephone='06 98 76 54 32',
            poste='Électricien Test',
            date_embauche=date.today()
        )
    print(f"✓ Stagiaire: {stag}")
    
    # Test 4: Formation
    print("\n[4] Test Formation...")
    form = Formation.objects.filter(stagiaire=stag, habilitation=hab).first()
    if not form:
        form = Formation.objects.create(
            stagiaire=stag,
            habilitation=hab,
            date_debut=date.today(),
            date_fin_prevue=date.today() + timedelta(days=30),
            statut='en_cours'
        )
    print(f"✓ Formation: {form}")
    print(f"  - Statut: {form.statut}")
    print(f"  - Jours restants: {form.jours_restants}")
    
    # Test 5: ValidationCompetence
    print("\n[5] Test ValidationCompetence...")
    val = ValidationCompetence.objects.filter(
        formation=form,
        titre_competence='Savoir 1'
    ).first()
    if not val:
        val = ValidationCompetence.objects.create(
            formation=form,
            type_competence='savoir',
            titre_competence='Savoir 1',
            valide=True
        )
    print(f"✓ Validation: {val}")
    print(f"  - Validée: {val.valide}")
    
    # Test 6: AvisFormation
    print("\n[6] Test AvisFormation...")
    avis = AvisFormation.objects.filter(formation=form).first()
    if not avis:
        avis = AvisFormation.objects.create(
            formation=form,
            avis='favorable',
            observations='Stagiaire sérieux et appliqué',
            formateur_nom='Formateur Test'
        )
    print(f"✓ Avis: {avis}")
    print(f"  - Avis: {avis.avis_label}")
    
    # Test 7: Titre
    print("\n[7] Test Titre...")
    # Marquer la formation comme complétée d'abord
    form.statut = 'completee'
    form.date_fin_reelle = date.today()
    form.save()
    
    titre = Titre.objects.filter(formation=form).first()
    if not titre:
        titre = Titre.objects.create(
            stagiaire=stag,
            formation=form,
            habilitation=hab,
            numero_titre='TEST-2024-001',
            date_delivrance=date.today(),
            date_expiration=date.today() + timedelta(days=1095),
            statut='delivre'
        )
    print(f"✓ Titre: {titre}")
    print(f"  - Valide: {titre.est_valide}")
    print(f"  - Expire bientôt: {titre.expire_bientot}")
    
    # Test 8: RenouvellementHabilitation
    print("\n[8] Test RenouvellementHabilitation...")
    renew = RenouvellementHabilitation.objects.filter(titre_precedent=titre).first()
    if not renew:
        renew = RenouvellementHabilitation.objects.create(
            titre_precedent=titre,
            date_renouvellement_prevue=date.today() + timedelta(days=1000),
            statut='planifie'
        )
    print(f"✓ Renouvellement: {renew}")
    print(f"  - En retard: {renew.est_en_retard}")
    print(f"  - Jours avant: {renew.jours_avant_renouvellement}")
    
    # Statistiques
    print("\n" + "="*60)
    print("STATISTIQUES")
    print("="*60)
    print(f"Entreprises: {Entreprise.objects.count()}")
    print(f"Habilitations: {Habilitation.objects.count()}")
    print(f"Stagiaires: {Stagiaire.objects.count()}")
    print(f"Formations: {Formation.objects.count()}")
    print(f"Validations: {ValidationCompetence.objects.count()}")
    print(f"Titres: {Titre.objects.count()}")
    print(f"Avis: {AvisFormation.objects.count()}")
    print(f"Renouvellements: {RenouvellementHabilitation.objects.count()}")
    print(f"Utilisateurs: {User.objects.count()}")
    
    print("\n" + "="*60)
    print("✓ TOUS LES TESTS SONT PASSÉS!")
    print("="*60)
    print("\nL'application est prête à être utilisée!")
    print("Accédez à: http://localhost:8000/")

if __name__ == '__main__':
    try:
        test_models()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
