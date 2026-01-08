from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Entreprise, Habilitation, Stagiaire, Formation, 
    ValidationCompetence, Titre, AvisFormation, 
    RenouvellementHabilitation, Journal,
    DemandeStagiaire, SessionFormation, ProfilUtilisateur,
    DemandeFormation
)


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_entreprise', 'email', 'telephone', 'ville', 'date_creation']
    list_filter = ['type_entreprise', 'ville', 'date_creation']
    search_fields = ['nom', 'email', 'ville']
    fieldsets = (
        ('Informations générales', {'fields': ('nom', 'type_entreprise', 'email', 'telephone')}),
        ('Adresse', {'fields': ('adresse', 'code_postal', 'ville')}),
    )


@admin.register(Habilitation)
class HabilitationAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'categorie', 'niveau', 'duree_validite_mois', 'actif']
    list_filter = ['categorie', 'actif']
    search_fields = ['code', 'nom']
    fieldsets = (
        ('Identification', {'fields': ('code', 'nom', 'description')}),
        ('Classification', {'fields': ('categorie', 'niveau')}),
        ('Validité', {'fields': ('duree_validite_mois',)}),
        ('Compétences', {'fields': ('savoirs', 'savoirs_faire')}),
        ('Statut', {'fields': ('actif',)}),
    )


@admin.register(Stagiaire)
class StagiaireAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'poste', 'organisme_formation', 'entreprise', 'email', 'actif', 'est_independant']
    list_filter = ['organisme_formation', 'entreprise', 'actif', 'date_embauche']
    search_fields = ['nom', 'prenom', 'email', 'poste']
    fieldsets = (
        ('Informations personnelles', {'fields': ('user', 'nom', 'prenom', 'email', 'telephone')}),
        ('Architecture B2B2C', {
            'fields': ('organisme_formation', 'entreprise'),
            'description': 'OF obligatoire. Entreprise optionnelle (si NULL = stagiaire indépendant)'
        }),
        ('Emploi', {'fields': ('poste', 'date_embauche')}),
        ('Statut', {'fields': ('actif',)}),
    )
    
    def est_independant(self, obj):
        return "✓" if obj.est_independant else ""
    est_independant.short_description = "Indépendant"


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ['stagiaire', 'habilitation', 'statut', 'date_debut', 'date_fin_reelle']
    list_filter = ['statut', 'habilitation', 'date_debut']
    search_fields = ['stagiaire__nom', 'stagiaire__prenom', 'habilitation__code']
    fieldsets = (
        ('Stagiaire et Habilitation', {'fields': ('stagiaire', 'habilitation')}),
        ('Informations de formation', {'fields': ('organisme_formation', 'numero_session')}),
        ('Dates', {'fields': ('date_debut', 'date_fin_prevue', 'date_fin_reelle')}),
        ('Statut', {'fields': ('statut', 'notes')}),
    )


@admin.register(ValidationCompetence)
class ValidationCompetenceAdmin(admin.ModelAdmin):
    list_display = ['formation', 'type_competence', 'titre_competence', 'valide', 'validateur']
    list_filter = ['type_competence', 'valide', 'date_validation']
    search_fields = ['formation__stagiaire__nom', 'titre_competence']
    fieldsets = (
        ('Formation', {'fields': ('formation',)}),
        ('Compétence', {'fields': ('type_competence', 'titre_competence', 'description')}),
        ('Validation', {'fields': ('valide', 'validateur', 'date_validation', 'commentaires_validateur')}),
    )


@admin.register(Titre)
class TitreAdmin(admin.ModelAdmin):
    list_display = ['numero_titre', 'stagiaire', 'habilitation', 'statut', 'date_delivrance', 'date_expiration']
    list_filter = ['statut', 'habilitation', 'date_delivrance']
    search_fields = ['numero_titre', 'stagiaire__nom', 'stagiaire__prenom']
    fieldsets = (
        ('Identification', {'fields': ('numero_titre', 'stagiaire', 'formation')}),
        ('Habilitation', {'fields': ('habilitation',)}),
        ('Dates', {'fields': ('date_delivrance', 'date_expiration')}),
        ('Statut', {'fields': ('statut', 'notes_avis', 'delivre_par')}),
    )


@admin.register(AvisFormation)
class AvisFormationAdmin(admin.ModelAdmin):
    list_display = ['formation', 'avis', 'formateur_nom', 'date_avis']
    list_filter = ['avis', 'date_avis']
    search_fields = ['formation__stagiaire__nom', 'formateur_nom']
    fieldsets = (
        ('Formation', {'fields': ('formation',)}),
        ('Avis', {'fields': ('avis', 'observations')}),
        ('Détails', {'fields': ('points_forts', 'points_amelioration', 'recommandations')}),
        ('Formateur', {'fields': ('formateur_nom', 'signature_formateur')}),
    )


@admin.register(RenouvellementHabilitation)
class RenouvellementHabilitationAdmin(admin.ModelAdmin):
    list_display = ['titre_precedent', 'statut', 'date_renouvellement_prevue', 'date_renouvellement_reelle']
    list_filter = ['statut', 'date_renouvellement_prevue']
    search_fields = ['titre_precedent__numero_titre', 'titre_precedent__stagiaire__nom']
    fieldsets = (
        ('Titre précédent', {'fields': ('titre_precedent',)}),
        ('Dates', {'fields': ('date_renouvellement_prevue', 'date_renouvellement_reelle')}),
        ('Statut', {'fields': ('statut', 'notes')}),
    )


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['action', 'utilisateur', 'entreprise', 'date_action']
    list_filter = ['action', 'entreprise', 'date_action']
    search_fields = ['description', 'objet_concerne']
    readonly_fields = ['date_action']


@admin.register(SessionFormation)
class SessionFormationAdmin(admin.ModelAdmin):
    list_display = ['numero_session', 'habilitation', 'date_debut', 'date_fin', 'statut', 'nombre_places', 'places_restantes']
    list_filter = ['statut', 'habilitation', 'date_debut']
    search_fields = ['numero_session', 'habilitation__code', 'lieu']
    fieldsets = (
        ('Identification', {'fields': ('numero_session', 'habilitation')}),
        ('Dates et lieu', {'fields': ('date_debut', 'date_fin', 'lieu')}),
        ('Organisation', {'fields': ('organisme_formation', 'formateur_nom', 'nombre_places')}),
        ('Statut', {'fields': ('statut', 'notes', 'createur')}),
    )
    readonly_fields = ['createur']


@admin.register(DemandeStagiaire)
class DemandeStagiaireAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'entreprise', 'statut', 'est_renouvellement', 'date_demande']
    list_filter = ['statut', 'est_renouvellement', 'entreprise', 'date_demande']
    search_fields = ['nom', 'prenom', 'email', 'entreprise__nom']
    fieldsets = (
        ('Stagiaire', {
            'fields': ('stagiaire_existant', 'nom', 'prenom', 'email', 'telephone'),
            'description': 'Sélectionnez un stagiaire existant ou remplissez les infos manuelles'
        }),
        ('Emploi', {'fields': ('poste', 'date_embauche')}),
        ('Entreprise', {'fields': ('entreprise',)}),
        ('Formations demandées', {'fields': ('habilitations_demandees',)}),
        ('Renouvellement', {'fields': ('est_renouvellement', 'titre_renouvelle')}),
        ('Informations', {'fields': ('notes',)}),
        ('Traitement', {'fields': ('statut', 'session_assignee', 'stagiaire_cree', 'date_traitement', 'traite_par')}),
    )
    readonly_fields = ['date_demande', 'date_traitement']
    
    def nom_complet(self, obj):
        """Affiche le nom complet du stagiaire"""
        if obj.stagiaire_existant:
            return str(obj.stagiaire_existant)
        return f"{obj.prenom} {obj.nom}" if obj.nom else "Inconnu"
    nom_complet.short_description = "Stagiaire"


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ['user', 'entreprise', 'role', 'actif', 'date_creation']
    list_filter = ['role', 'actif', 'entreprise']
    search_fields = ['user__username', 'user__email', 'entreprise__nom']
    fieldsets = (
        ('Utilisateur', {'fields': ('user',)}),
        ('Rôle B2B2C', {
            'fields': ('role', 'entreprise'),
            'description': 'Super Admin = pas d\'entreprise. Autres rôles = entreprise obligatoire.'
        }),
        ('Statut', {'fields': ('actif',)}),
    )
    readonly_fields = ['date_creation']
    
    def get_form(self, request, obj=None, **kwargs):
        """Aide pour la création de profils"""
        form = super().get_form(request, obj, **kwargs)
        if 'role' in form.base_fields:
            form.base_fields['role'].help_text = (
                '<b>Rôles:</b><br>'
                '• Super Admin: Vous (éditeur SaaS)<br>'
                '• Admin OF: Organisme de Formation (client payant)<br>'
                '• Responsable PME: Responsable d\'entreprise cliente<br>'
                '• Stagiaire: Consultation personnelle uniquement'
            )
        return form


@admin.register(DemandeFormation)
class DemandeFormationAdmin(admin.ModelAdmin):
    list_display = ['id', 'entreprise_demandeuse', 'organisme_formation', 'habilitation', 
                    'nombre_stagiaires', 'statut', 'date_demande', 'date_traitement']
    list_filter = ['statut', 'organisme_formation', 'habilitation', 'date_demande']
    search_fields = ['entreprise_demandeuse__nom', 'organisme_formation__nom', 'habilitation__code']
    filter_horizontal = ['stagiaires']
    fieldsets = (
        ('Demande', {
            'fields': ('entreprise_demandeuse', 'organisme_formation', 'habilitation'),
        }),
        ('Stagiaires concernés', {
            'fields': ('stagiaires',),
        }),
        ('Détails', {
            'fields': ('date_souhaitee', 'commentaire_demande'),
        }),
        ('Traitement', {
            'fields': ('statut', 'commentaire_reponse', 'session_creee', 'traite_par', 'date_traitement'),
        }),
        ('Métadonnées', {
            'fields': ('demandeur', 'date_demande'),
        }),
    )
    readonly_fields = ['date_demande', 'date_traitement', 'demandeur']
    
    def nombre_stagiaires(self, obj):
        return obj.nombre_stagiaires
    nombre_stagiaires.short_description = "Nb stagiaires"

