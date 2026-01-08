"""Seed data for OF 'WattElse Training' with tenant and test users.

Run with:
    python manage.py shell < seed_wattelse.py

Creates:
- Entreprise OF: WattElse Training
- Tenant: wattelse (colors + logo placeholder)
- Client PME: ACME Industrie
- Users:
    admin_of: wattelse_admin / password123
    secretariat: wattelse_sec / password123
    formateur: wattelse_formateur / password123
    client (responsable_pme): acme_resp / password123
- A sample habilitation if missing (B1V)
"""

import django
from django.contrib.auth.models import User
from django.utils import timezone

from habilitations_app.models import (
    Entreprise,
    Tenant,
    ProfilUtilisateur,
    Habilitation,
)

# Ensure Django is setup when run via `python seed_wattelse.py`
try:
    django.setup()
except Exception:
    pass

OF_NAME = "WattElse Training"
TENANT_SLUG = "wattelse"
CLIENT_NAME = "ACME Industrie"
DEFAULT_PWD = "password123"

# 1) Create / get OF enterprise
of, _ = Entreprise.objects.get_or_create(
    nom=OF_NAME,
    defaults={
        'type_entreprise': 'of',
        'email': 'contact@wattelse.training',
        'telephone': '+33 1 23 45 67 89',
        'adresse': '12 rue de l’Energie',
        'code_postal': '75010',
        'ville': 'Paris',
    },
)

# 2) Tenant
tenant, _ = Tenant.objects.get_or_create(
    slug=TENANT_SLUG,
    defaults={
        'organisme_formation': of,
        'nom_public': OF_NAME,
        'domaine': '',
        'couleur_primaire': '#1e2a38',
        'couleur_secondaire': '#f5a623',
        'actif': True,
    },
)

# 3) Client enterprise
client, _ = Entreprise.objects.get_or_create(
    nom=CLIENT_NAME,
    defaults={
        'type_entreprise': 'client',
        'email': 'contact@acme-industrie.fr',
        'telephone': '+33 1 88 88 88 88',
        'adresse': '1 avenue des Forges',
        'code_postal': '69000',
        'ville': 'Lyon',
        'tenant': tenant,
    },
)

# 4) Habilitation sample
hab, _ = Habilitation.objects.get_or_create(
    code='B1V',
    defaults={
        'nom': 'Exécution de travaux - Basse Tension',
        'description': 'Travaux BT courants',
        'categorie': '1',
        'niveau': 'Standard',
        'duree_validite_mois': 36,
        'savoirs': 'Normes de sécurité\nRisques électriques\nProcédures d’urgence',
        'savoirs_faire': 'Utilisation EPI\nRéalisation de câblages\nTests de sécurité',
        'actif': True,
    },
)

# 5) Helper to create users + profiles

def ensure_user(username, role, entreprise):
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password(DEFAULT_PWD)
    user.is_active = True
    user.save()

    profil, _ = ProfilUtilisateur.objects.get_or_create(user=user)
    profil.role = role
    profil.entreprise = entreprise
    profil.tenant = tenant
    profil.actif = True
    profil.save()
    return user, profil

admin_user, _ = ensure_user('wattelse_admin', 'admin_of', of)
sec_user, _ = ensure_user('wattelse_sec', 'secretariat', of)
form_user, _ = ensure_user('wattelse_formateur', 'formateur', of)
client_user, _ = ensure_user('acme_resp', 'responsable_pme', client)

print("✓ OF:", of)
print("✓ Tenant:", tenant)
print("✓ Client PME:", client)
print("✓ Users created/updated (pwd = password123):")
print("  - wattelse_admin (admin_of)")
print("  - wattelse_sec (secretariat)")
print("  - wattelse_formateur (formateur)")
print("  - acme_resp (responsable_pme)")
print("✓ Habilitation:", hab.code)
print("Done.")
