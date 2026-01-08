from django.urls import path
from . import views
from . import views_demandes, views_dashboards, views_invitations

urlpatterns = [
    path('', views.home, name='home'),
    
    # Dashboards par rôle
    path('dashboard/', views.home, name='dashboard'),  # Redirection intelligente
    path('dashboard/super-admin/', views_dashboards.dashboard_super_admin, name='dashboard_super_admin'),
    path('dashboard/admin-of/', views_dashboards.dashboard_admin_of, name='dashboard_admin_of'),
    path('dashboard/responsable-pme/', views_dashboards.dashboard_responsable_pme, name='dashboard_responsable_pme'),
    path('dashboard/stagiaire/', views_dashboards.dashboard_stagiaire, name='dashboard_stagiaire'),
    path('dashboard/formateur/', views_dashboards.dashboard_formateur, name='dashboard_formateur'),
    
    # Compatibilité anciens noms
    path('dashboard/client/', views_dashboards.dashboard_responsable_pme, name='dashboard_client'),
    path('dashboard/of/', views_dashboards.dashboard_admin_of, name='dashboard_of'),
    
    # Stagiaires
    path('stagiaires/', views.StagiaireListView.as_view(), name='stagiaire_list'),
    path('stagiaires/<int:pk>/', views.StagiaireDetailView.as_view(), name='stagiaire_detail'),
    path('stagiaires/nouveau/', views.StagiaireCreateView.as_view(), name='stagiaire_create'),
    path('stagiaires/<int:pk>/modifier/', views.StagiaireUpdateView.as_view(), name='stagiaire_update'),
    
    # Formations
    path('formations/', views.FormationListView.as_view(), name='formation_list'),
    path('formations/<int:pk>/', views.FormationDetailView.as_view(), name='formation_detail'),
    path('stagiaires/<int:stagiaire_id>/formation/nouveau/', views.FormationCreateView.as_view(), name='formation_create'),
    path('formations/<int:pk>/modifier/', views.FormationUpdateView.as_view(), name='formation_update'),
    path('formations/<int:formation_id>/competences/', views.valider_competences, name='valider_competences'),
    path('formations/<int:formation_id>/avis/', views.creer_avis_formation, name='creer_avis'),
    path('formations/<int:formation_id>/titre/', views.delivrer_titre, name='delivrer_titre'),
    
    # Titres
    path('titres/', views.TitreListView.as_view(), name='titre_list'),
    path('titres/<int:titre_id>/renouveler/', views.planifier_renouvellement, name='planifier_renouvellement'),
    
    # Renouvellements
    path('renouvellements/', views.RenouvellementListView.as_view(), name='renouvellement_list'),
    
    # Demandes de formation B2B2C (PME → OF)
    path('demandes-formation/creer/', views_demandes.creer_demande_formation, name='creer_demande_formation'),
    path('demandes-formation/', views_demandes.liste_demandes_formation, name='liste_demandes_formation'),
    path('demandes-formation/<int:pk>/', views_demandes.detail_demande_formation, name='detail_demande_formation'),
    path('demandes-formation/<int:pk>/traiter/', views_demandes.traiter_demande_formation, name='traiter_demande_formation'),
    path('demandes-formation/<int:demande_pk>/creer-session/', views_demandes.creer_session_from_demande, name='creer_session_from_demande'),
    
    # Demandes de stagiaires (entreprise cliente) - Ancien système
    path('demandes/soumettre/', views.soumettre_demande_stagiaire, name='soumettre_demande_stagiaire'),
    path('demandes/mes-demandes/', views.liste_demandes_stagiaires, name='liste_demandes_stagiaires'),
    
    # Sessions de formation (secrétaire kompetans)
    path('sessions/', views.liste_sessions_formation, name='liste_sessions_formation'),
    path('sessions/creer/', views.creer_session_formation, name='creer_session_formation'),
    path('sessions/<int:pk>/', views.detail_session_formation, name='detail_session_formation'),
    
    # Gestion des demandes (admin/secrétaire)
    path('admin/demandes/', views.liste_demandes_admin, name='liste_demandes_admin'),

    # Invitations PME (Admin OF)
    path('of/invitations/', views_invitations.liste_invitations, name='liste_invitations'),
    path('of/invitations/creer/', views_invitations.creer_entreprise_et_invitation, name='creer_entreprise_et_invitation'),
    path('invite/<str:token>/', views_invitations.accepter_invitation, name='accepter_invitation'),

    # API utilitaires
    path('api/import-csv/', views.api_import_csv, name='api_import_csv'),
    path('api/aggregats-of/', views.api_aggregats_of, name='api_aggregats_of'),
    path('api/demandes/<int:demande_id>/valider/', views.api_valider_demande, name='api_valider_demande'),
    path('api/titres/<int:titre_id>/pdf/', views.api_pdf_titre, name='api_pdf_titre'),
]
