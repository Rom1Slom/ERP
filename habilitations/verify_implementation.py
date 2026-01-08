#!/usr/bin/env python
"""
Vérification complète de l'implémentation des rôles Client & OF
Exécuter avec: python verify_implementation.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from habilitations_app.models import Entreprise, ProfilUtilisateur


def print_header(title):
    """Afficher un titre formaté"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def verify_models():
    """Vérifier les modèles"""
    print_header("1. VÉRIFICATION DES MODÈLES")
    
    # Vérifier Entreprise.type_entreprise
    print("✓ Entreprise.type_entreprise")
    entreprise = Entreprise.objects.first()
    if entreprise:
        print(f"  Exemple: {entreprise.nom} ({entreprise.get_type_entreprise_display()})")
    else:
        print("  ⚠ Aucune entreprise créée")
    
    # Vérifier ProfilUtilisateur.role
    print("\n✓ ProfilUtilisateur.role")
    profil = ProfilUtilisateur.objects.first()
    if profil:
        print(f"  Exemple: {profil.user.username} ({profil.get_role_display()})")
        print(f"  est_client: {profil.est_client}")
        print(f"  est_of: {profil.est_of}")
    else:
        print("  ⚠ Aucun profil créé")
    
    # Vérifier suppression Secretaire
    print("\n✓ Modèle Secretaire supprimé")
    try:
        from habilitations_app.models import Secretaire
        print("  ❌ ERREUR: Secretaire existe toujours!")
        return False
    except ImportError:
        print("  ✓ Secretaire bien supprimé")
    
    return True


def verify_urls():
    """Vérifier les URLs"""
    print_header("2. VÉRIFICATION DES URLs")
    
    from django.urls import get_resolver
    from django.urls.exceptions import Resolver404
    
    urls_to_check = [
        ('/', 'home'),
        ('/dashboard/client/', 'dashboard_client'),
        ('/dashboard/of/', 'dashboard_of'),
        ('/accounts/login/', 'login'),
    ]
    
    resolver = get_resolver()
    
    for path, name in urls_to_check:
        try:
            match = resolver.resolve(path)
            print(f"✓ {name}: {path}")
        except Resolver404:
            print(f"❌ {name}: {path} - NON TROUVÉ")
            return False
    
    return True


def verify_views():
    """Vérifier les vues"""
    print_header("3. VÉRIFICATION DES VUES")
    
    views_to_check = [
        ('habilitations_app.views', 'CustomLoginView'),
        ('habilitations_app.views', 'home'),
        ('habilitations_app.views', 'dashboard_client'),
        ('habilitations_app.views', 'dashboard_of'),
    ]
    
    for module_name, view_name in views_to_check:
        try:
            module = __import__(module_name, fromlist=[view_name])
            view = getattr(module, view_name)
            print(f"✓ {view_name}")
        except (ImportError, AttributeError) as e:
            print(f"❌ {view_name} - ERREUR: {e}")
            return False
    
    return True


def verify_decorators():
    """Vérifier les décorateurs"""
    print_header("4. VÉRIFICATION DES DÉCORATEURS")
    
    decorators_to_check = [
        'role_required',
        'client_required',
        'of_required',
        'RoleRequiredMixin',
        'ClientRequiredMixin',
        'OFRequiredMixin',
    ]
    
    try:
        from habilitations_app.decorators import (
            role_required, client_required, of_required,
            RoleRequiredMixin, ClientRequiredMixin, OFRequiredMixin
        )
        for decorator in decorators_to_check:
            print(f"✓ {decorator}")
        return True
    except ImportError as e:
        print(f"❌ ERREUR: {e}")
        return False


def verify_templates():
    """Vérifier les templates"""
    print_header("5. VÉRIFICATION DES TEMPLATES")
    
    from django.template.loader import get_template
    from django.template.exceptions import TemplateDoesNotExist
    
    templates_to_check = [
        'habilitations_app/base.html',
        'habilitations_app/dashboard_client.html',
        'habilitations_app/dashboard_of.html',
    ]
    
    for template_name in templates_to_check:
        try:
            get_template(template_name)
            print(f"✓ {template_name}")
        except TemplateDoesNotExist:
            print(f"❌ {template_name} - NON TROUVÉ")
            return False
    
    return True


def verify_test_users():
    """Vérifier les utilisateurs de test"""
    print_header("6. VÉRIFICATION DES UTILISATEURS DE TEST")
    
    test_users = {
        'client_user': 'client',
        'of_user': 'of',
    }
    
    all_ok = True
    for username, expected_role in test_users.items():
        try:
            user = User.objects.get(username=username)
            profil = user.profil
            if profil.role == expected_role:
                print(f"✓ {username}")
                print(f"  ├─ Entreprise: {profil.entreprise.nom}")
                print(f"  ├─ Rôle: {profil.get_role_display()}")
                print(f"  └─ Email: {user.email}")
            else:
                print(f"❌ {username} - Rôle incorrect: {profil.role}")
                all_ok = False
        except User.DoesNotExist:
            print(f"❌ {username} - UTILISATEUR NON TROUVÉ")
            all_ok = False
        except ProfilUtilisateur.DoesNotExist:
            print(f"❌ {username} - PROFIL NON TROUVÉ")
            all_ok = False
    
    return all_ok


def verify_documentation():
    """Vérifier la documentation"""
    print_header("7. VÉRIFICATION DE LA DOCUMENTATION")
    
    docs_to_check = [
        'ROLES_GUIDE.md',
        'ROLES_SUMMARY.md',
        'ARCHITECTURE_ROLES.md',
        'FICHIERS_MODIFIES.md',
        'QUICKSTART_ROLES.md',
    ]
    
    for doc in docs_to_check:
        if os.path.exists(doc):
            size = os.path.getsize(doc)
            print(f"✓ {doc} ({size} bytes)")
        else:
            print(f"❌ {doc} - NON TROUVÉ")
            return False
    
    return True


def print_summary(results):
    """Afficher le résumé"""
    print_header("RÉSUMÉ DE LA VÉRIFICATION")
    
    checks = [
        ("Modèles", results['models']),
        ("URLs", results['urls']),
        ("Vues", results['views']),
        ("Décorateurs", results['decorators']),
        ("Templates", results['templates']),
        ("Utilisateurs de test", results['test_users']),
        ("Documentation", results['documentation']),
    ]
    
    all_ok = True
    for name, ok in checks:
        status = "✓ PASS" if ok else "❌ FAIL"
        print(f"{status:8} {name}")
        if not ok:
            all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("  ✓ TOUS LES TESTS RÉUSSIS!")
        print("  L'implémentation est complète et fonctionnelle.")
    else:
        print("  ❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("  Veuillez vérifier les erreurs ci-dessus.")
    print("=" * 60 + "\n")
    
    return all_ok


def main():
    """Exécuter toutes les vérifications"""
    print("\n" + "🔍 VÉRIFICATION DE L'IMPLÉMENTATION DES RÔLES CLIENT & OF\n".center(60))
    
    results = {
        'models': verify_models(),
        'urls': verify_urls(),
        'views': verify_views(),
        'decorators': verify_decorators(),
        'templates': verify_templates(),
        'test_users': verify_test_users(),
        'documentation': verify_documentation(),
    }
    
    all_ok = print_summary(results)
    
    # Recommandations
    if not all_ok:
        print("\n⚠️  RECOMMANDATIONS:")
        print("  1. Consulter les erreurs ci-dessus")
        print("  2. Vérifier les fichiers modifiés")
        print("  3. Réexécuter les migrations si nécessaire")
        print("  4. Créer les utilisateurs de test:")
        print("     python create_test_users.py\n")
    else:
        print("\n✅ PROCHAINES ÉTAPES:")
        print("  1. Tester en local:")
        print("     python manage.py runserver")
        print("  2. Accéder à:")
        print("     http://localhost:8000/accounts/login/")
        print("  3. Identifier avec: client_user / password123")
        print("  4. Consulter la documentation:\n")
        for doc in ['QUICKSTART_ROLES.md', 'ROLES_GUIDE.md', 'ROLES_SUMMARY.md']:
            print(f"     - {doc}")
        print()
    
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
