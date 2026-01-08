from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import secrets


class Entreprise(models.Model):
    """Model pour les entreprises"""
    TYPES_ENTREPRISE = [
        ('client', 'Client'),
        ('of', 'Organisme de Formation'),
    ]
    
    nom = models.CharField(max_length=255, unique=True)
    type_entreprise = models.CharField(max_length=20, choices=TYPES_ENTREPRISE, default='client')
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entreprises',
        help_text="Tenant (OF) propriétaire – obligatoire pour les PME clientes"
    )
    
    class Meta:
        verbose_name_plural = "Entreprises"
        ordering = ['nom']
        indexes = [
            models.Index(fields=['type_entreprise', 'nom']),
            models.Index(fields=['tenant', 'type_entreprise']),
        ]
    
    def __str__(self):
        return self.nom


class Tenant(models.Model):
    """Tenant SaaS associé à un organisme de formation (OF)

    Sert à l'isolation des données, au branding (logo/couleurs) et au routage par sous-domaine.
    """

    organisme_formation = models.OneToOneField(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='tenant_of',
        limit_choices_to={'type_entreprise': 'of'}
    )
    nom_public = models.CharField(max_length=255)
    slug = models.SlugField(max_length=80, unique=True, help_text="Sous-domaine slug ex: of-kompetans")
    domaine = models.CharField(max_length=255, blank=True, help_text="Domaine dédié si configuré (ex: of.example.com)")
    logo = models.ImageField(upload_to='tenants/logos/', blank=True, null=True)
    couleur_primaire = models.CharField(max_length=20, default='#2c3e50')
    couleur_secondaire = models.CharField(max_length=20, default='#27ae60')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['slug']
        indexes = [
            models.Index(fields=['slug', 'actif']),
            models.Index(fields=['domaine']),
        ]

    def __str__(self):
        return f"{self.nom_public} ({self.slug})"


class Habilitation(models.Model):
    """Model pour les types d'habilitations électriques"""
    CATEGORIES = [
        ('1', 'Basse Tension (BT)'),
        ('2', 'Haute Tension (HT)'),
        ('3', 'Mixte'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    categorie = models.CharField(max_length=10, choices=CATEGORIES)
    niveau = models.CharField(max_length=10)
    duree_validite_mois = models.IntegerField(default=36)
    savoirs = models.TextField(help_text="Liste des savoirs théoriques requis")
    savoirs_faire = models.TextField(help_text="Liste des savoir-faire pratiques requis")
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


class Stagiaire(models.Model):
    """Model pour les stagiaires en formation
    
    Architecture B2B2C:
    - organisme_formation: L'OF qui gère ce stagiaire (OBLIGATOIRE)
    - entreprise: La PME employeur (OPTIONNEL)
      * Si NULL = stagiaire indépendant inscrit directement par l'OF
      * Si renseigné = stagiaire employé d'une PME cliente de l'OF
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    organisme_formation = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='stagiaires_of',
        limit_choices_to={'type_entreprise': 'of'},
        help_text="L'organisme de formation qui gère ce stagiaire"
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stagiaires',
        help_text="Tenant (OF) propriétaire"
    )
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='stagiaires',
        limit_choices_to={'type_entreprise': 'client'},
        null=True,
        blank=True,
        help_text="L'entreprise employeur (optionnel, NULL = stagiaire indépendant)"
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    poste = models.CharField(max_length=150, blank=True, null=True)
    date_embauche = models.DateField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nom', 'prenom']
        indexes = [
            models.Index(fields=['entreprise', 'actif']),
            models.Index(fields=['tenant', 'actif']),
        ]
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
    
    @property
    def est_independant(self):
        """Retourne True si le stagiaire est indépendant (pas d'entreprise)"""
        return self.entreprise is None


class Formation(models.Model):
    """Model pour les formations suivies"""
    STATUTS = [
        ('en_cours', 'En cours'),
        ('completee', 'Complétée'),
        ('abandonnee', 'Abandonnée'),
    ]
    
    stagiaire = models.ForeignKey(Stagiaire, on_delete=models.CASCADE, related_name='formations')
    habilitation = models.ForeignKey(Habilitation, on_delete=models.CASCADE, related_name='formations')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='formations',
        help_text="Tenant (OF) propriétaire"
    )
    session = models.ForeignKey(
        'SessionFormation', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='formations_session'
    )
    organisme_formation = models.CharField(max_length=255, default='Oxalis')
    date_debut = models.DateField()
    date_fin_prevue = models.DateField()
    date_fin_reelle = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    numero_session = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('stagiaire', 'habilitation')
        ordering = ['-date_debut']
        indexes = [
            models.Index(fields=['tenant', 'statut']),
            models.Index(fields=['stagiaire', 'habilitation', 'statut']),
        ]
    
    def __str__(self):
        return f"{self.stagiaire.nom_complet} - {self.habilitation.code}"
    
    @property
    def est_completee(self):
        return self.statut == 'completee'
    
    @property
    def jours_restants(self):
        if self.date_fin_reelle:
            return 0
        return (self.date_fin_prevue - timezone.now().date()).days


class ValidationCompetence(models.Model):
    """Model pour valider les compétences (savoirs et savoir-faire)"""
    COMPETENCE_TYPES = [
        ('savoir', 'Savoir théorique'),
        ('savoir_faire', 'Savoir-faire pratique'),
    ]
    
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='validations')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='validations'
    )
    type_competence = models.CharField(max_length=20, choices=COMPETENCE_TYPES)
    titre_competence = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    valide = models.BooleanField(default=False)
    commentaires_validateur = models.TextField(blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    validateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validations')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('formation', 'titre_competence')
        ordering = ['type_competence', 'titre_competence']
        indexes = [
            models.Index(fields=['tenant', 'type_competence']),
        ]
    
    def __str__(self):
        return f"{self.formation} - {self.titre_competence}"


class Titre(models.Model):
    """Model pour les titres d'habilitation"""
    STATUTS = [
        ('attente', 'En attente'),
        ('delivre', 'Délivré'),
        ('expire', 'Expiré'),
        ('renouvele', 'Renouvelé'),
    ]
    
    stagiaire = models.ForeignKey(Stagiaire, on_delete=models.CASCADE, related_name='titres')
    formation = models.OneToOneField(Formation, on_delete=models.CASCADE)
    habilitation = models.ForeignKey(Habilitation, on_delete=models.CASCADE)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='titres'
    )
    numero_titre = models.CharField(max_length=50, unique=True)
    date_delivrance = models.DateField()
    date_expiration = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUTS, default='attente')
    notes_avis = models.TextField(blank=True)
    delivre_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='titres_delivres')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_delivrance']
        indexes = [
            models.Index(fields=['date_expiration']),
            models.Index(fields=['tenant', 'statut']),
        ]
    
    def __str__(self):
        return f"{self.numero_titre} - {self.stagiaire.nom_complet}"
    
    @property
    def est_valide(self):
        return self.statut == 'delivre' and self.date_expiration >= timezone.now().date()
    
    @property
    def jours_avant_expiration(self):
        return (self.date_expiration - timezone.now().date()).days
    
    @property
    def expire_bientot(self):
        """Retourne True si le titre expire dans moins de 90 jours"""
        return 0 < self.jours_avant_expiration <= 90


class AvisFormation(models.Model):
    """Model pour l'avis après formation"""
    AVIS_CHOICES = [
        ('favorable', 'Favorable'),
        ('favorable_condition', 'Favorable avec conditions'),
        ('defavorable', 'Défavorable'),
    ]
    
    formation = models.OneToOneField(Formation, on_delete=models.CASCADE, related_name='avis')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='avis_formations'
    )
    avis = models.CharField(max_length=20, choices=AVIS_CHOICES)
    observations = models.TextField(blank=True)
    points_forts = models.TextField(blank=True)
    points_amelioration = models.TextField(blank=True)
    recommandations = models.TextField(blank=True)
    formateur_nom = models.CharField(max_length=150)
    date_avis = models.DateField(auto_now_add=True)
    signature_formateur = models.ImageField(upload_to='signatures/', blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Avis - {self.formation.stagiaire.nom_complet}"
    
    @property
    def avis_label(self):
        return dict(self.AVIS_CHOICES).get(self.avis)


class RenouvellementHabilitation(models.Model):
    """Model pour le suivi des renouvellements d'habilitations"""
    STATUTS = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('renouvele', 'Renouvelé'),
        ('expire', 'Expiré'),
    ]
    
    titre_precedent = models.ForeignKey(Titre, on_delete=models.CASCADE, related_name='renouvellements')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='renouvellements'
    )
    date_renouvellement_prevue = models.DateField()
    date_renouvellement_reelle = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='planifie')
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_renouvellement_prevue']
        indexes = [
            models.Index(fields=['tenant', 'statut']),
            models.Index(fields=['date_renouvellement_prevue']),
        ]
    
    def __str__(self):
        return f"Renouvellement {self.titre_precedent.numero_titre}"
    
    @property
    def est_en_retard(self):
        """Retourne True si le renouvellement est en retard"""
        if self.statut == 'renouvele':
            return False
        return timezone.now().date() > self.date_renouvellement_prevue
    
    @property
    def jours_avant_renouvellement(self):
        """Retourne le nombre de jours avant le renouvellement prévu"""
        return (self.date_renouvellement_prevue - timezone.now().date()).days


class SessionFormation(models.Model):
    """Model pour les sessions de formation créées par les secrétaires"""
    STATUTS = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    numero_session = models.CharField(max_length=50, unique=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sessions'
    )
    habilitation = models.ForeignKey(Habilitation, on_delete=models.CASCADE, related_name='sessions')
    date_debut = models.DateField()
    date_fin = models.DateField()
    organisme_formation = models.CharField(max_length=255, default='Kompetans.fr')
    lieu = models.CharField(max_length=255, blank=True)
    formateur_nom = models.CharField(max_length=150, blank=True)
    formateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions_assignees',
        help_text="Formateur responsable de la session"
    )
    statut = models.CharField(max_length=20, choices=STATUTS, default='planifiee')
    nombre_places = models.IntegerField(default=12)
    notes = models.TextField(blank=True)
    createur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sessions_creees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Session de formation"
        verbose_name_plural = "Sessions de formation"
        indexes = [
            models.Index(fields=['tenant', 'statut']),
            models.Index(fields=['organisme_formation', 'statut']),
        ]
    
    def __str__(self):
        return f"{self.numero_session} - {self.habilitation.code} ({self.date_debut})"
    
    @property
    def places_restantes(self):
        """Retourne le nombre de places disponibles"""
        stagiaires_inscrits = self.formations_session.count()
        return max(0, self.nombre_places - stagiaires_inscrits)
    
    @property
    def est_complete(self):
        """Retourne True si la session est complète"""
        return self.places_restantes == 0


class DemandeFormation(models.Model):
    """Demande de formation d'une PME vers un OF
    
    Workflow: Responsable PME → Admin OF
    1. Responsable PME crée une demande pour un/plusieurs stagiaires
    2. Admin OF reçoit la demande dans son tableau de bord
    3. Admin OF approuve/refuse la demande
    4. Si approuvée, Admin OF crée une session et inscrit les stagiaires
    """
    STATUTS = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('refusee', 'Refusée'),
        ('annulee', 'Annulée'),
    ]
    
    entreprise_demandeuse = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='demandes_formation_emises',
        limit_choices_to={'type_entreprise': 'client'},
        help_text="La PME qui demande la formation"
    )
    organisme_formation = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='demandes_formation_recues',
        limit_choices_to={'type_entreprise': 'of'},
        help_text="L'OF qui recevra la demande"
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='demandes_formation'
    )
    habilitation = models.ForeignKey(
        Habilitation,
        on_delete=models.CASCADE,
        help_text="Type d'habilitation demandée"
    )
    stagiaires = models.ManyToManyField(
        Stagiaire,
        related_name='demandes_formation',
        help_text="Stagiaires concernés par cette demande"
    )
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    date_souhaitee = models.DateField(null=True, blank=True, help_text="Date souhaitée pour la formation")
    commentaire_demande = models.TextField(blank=True, help_text="Commentaire de la PME")
    commentaire_reponse = models.TextField(blank=True, help_text="Réponse de l'OF")
    
    demandeur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='demandes_formation_creees',
        help_text="Utilisateur ayant créé la demande"
    )
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demandes_formation_traitees'
    )
    consentement_at = models.DateTimeField(null=True, blank=True)
    consentement_ip = models.GenericIPAddressField(null=True, blank=True)
    consentement_user_agent = models.TextField(blank=True)
    session_creee = models.ForeignKey(
        'SessionFormation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demandes_origine'
    )
    
    class Meta:
        ordering = ['-date_demande']
        verbose_name = "Demande de formation"
        verbose_name_plural = "Demandes de formation"
        indexes = [
            models.Index(fields=['tenant', 'statut']),
            models.Index(fields=['entreprise_demandeuse', 'statut']),
            models.Index(fields=['organisme_formation', 'statut']),
        ]
    
    def __str__(self):
        return f"Demande {self.entreprise_demandeuse.nom} → {self.habilitation.code} ({self.get_statut_display()})"
    
    @property
    def nombre_stagiaires(self):
        return self.stagiaires.count()


class DemandeStagiaire(models.Model):
    """Model pour les demandes de formation soumises par les entreprises clientes"""
    STATUTS = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('integree', 'Intégrée à une session'),
        ('refusee', 'Refusée'),
    ]
    
    # Lien au stagiaire existant ou infos manuelles
    stagiaire_existant = models.ForeignKey(
        Stagiaire, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='demandes_stagiaires'
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='demandes_stagiaires'
    )
    
    # Infos manuelles (si pas de stagiaire existant)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='demandes_stagiaires')
    nom = models.CharField(max_length=100, blank=True)
    prenom = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    poste = models.CharField(max_length=150, blank=True)
    date_embauche = models.DateField(null=True, blank=True)
    
    # Habilitations demandées (plusieurs possibles)
    habilitations_demandees = models.ManyToManyField(Habilitation, related_name='demandes')
    
    # Renouvellement
    est_renouvellement = models.BooleanField(default=False)
    titre_renouvelle = models.ForeignKey(
        Titre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demande_renouvellement'
    )
    
    notes = models.TextField(blank=True, help_text="Informations complémentaires")
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    session_assignee = models.ForeignKey(
        SessionFormation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='demandes'
    )
    stagiaire_cree = models.ForeignKey(
        Stagiaire, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='demande_origine'
    )
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_traitees')
    consentement_at = models.DateTimeField(null=True, blank=True)
    consentement_ip = models.GenericIPAddressField(null=True, blank=True)
    consentement_user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_demande']
        verbose_name = "Demande de stagiaire"
        verbose_name_plural = "Demandes de stagiaires"
        indexes = [
            models.Index(fields=['tenant', 'statut']),
            models.Index(fields=['entreprise', 'statut']),
        ]

    def __str__(self):
        return f"Demande de {self.nom_complet} - {self.get_statut_display()}"

    @property
    def nom_complet(self):
        if self.stagiaire_existant:
            return str(self.stagiaire_existant)
        return f"{self.prenom} {self.nom}".strip()


class ProfilUtilisateur(models.Model):
    """Profil utilisateur liant un User à une Entreprise avec rôle spécifique
    
    Rôles B2B2C:
    - super_admin: Éditeur SaaS (vous) - gère tous les OF
    - admin_of: Administrateur OF - gère ses PME clientes + stagiaires indépendants
    - secretariat: Secrétariat OF - gère sessions/demandes/imports pour l'OF
    - formateur: Formateur OF - saisit validations et avis sur ses sessions
    - responsable_pme: Responsable PME (client) - consulte ses employés, demande formations
    - stagiaire: Stagiaire - consulte son propre dossier
    """
    ROLES = [
        ('super_admin', 'Super Admin - Éditeur SaaS'),
        ('admin_of', 'Administrateur OF'),
        ('secretariat', 'Secrétariat OF'),
        ('formateur', 'Formateur OF'),
        ('responsable_pme', 'Responsable PME'),
        ('stagiaire', 'Stagiaire'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs'
    )
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='utilisateurs',
        null=True,
        blank=True,
        help_text="Entreprise rattachée (NULL pour super_admin)"
    )
    role = models.CharField(max_length=50, choices=ROLES, default='responsable_pme')
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        entreprise_nom = self.entreprise.nom if self.entreprise else "N/A"
        return f"{self.user.username} - {entreprise_nom} ({self.get_role_display()})"
    
    @property
    def est_super_admin(self):
        return self.role == 'super_admin'
    
    @property
    def est_admin_of(self):
        return self.role == 'admin_of'

    @property
    def est_secretariat(self):
        return self.role == 'secretariat'

    @property
    def est_formateur(self):
        return self.role == 'formateur'
    
    @property
    def est_responsable_pme(self):
        return self.role == 'responsable_pme'
    
    @property
    def est_stagiaire(self):
        return self.role == 'stagiaire'
    
    # Anciens noms pour compatibilité
    @property
    def est_client(self):
        return self.role in ['responsable_pme', 'client']
    
    @property
    def est_of(self):
        return self.role in ['admin_of', 'secretariat', 'formateur']


# Model Secretaire supprimé - remplacé par ProfilUtilisateur avec rôle 'of'


class Consentement(models.Model):
    """Trace du consentement recueilli (RGPD / traitement des données)"""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    demande_formation = models.ForeignKey(
        DemandeFormation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='consentements'
    )
    stagiaire = models.ForeignKey(
        Stagiaire,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='consentements'
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='consentements'
    )
    scope = models.CharField(max_length=150, default='demande_formation')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    consent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-consent_at']
        indexes = [
            models.Index(fields=['tenant', 'scope']),
        ]

    def __str__(self):
        return f"Consentement {self.scope} ({self.consent_at.date()})"


class Journal(models.Model):
    """Model pour journaliser les actions"""
    ACTIONS = [
        ('creation_stagiaire', 'Création stagiaire'),
        ('creation_formation', 'Création formation'),
        ('validation_competence', 'Validation compétence'),
        ('delivrance_titre', 'Délivrance titre'),
        ('renouvellement', 'Renouvellement'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    action = models.CharField(max_length=30, choices=ACTIONS)
    description = models.TextField()
    objet_concerne = models.CharField(max_length=100)
    date_action = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.action} - {self.date_action}"


class InvitationEntreprise(models.Model):
    """Invitation pour créer un compte Responsable PME lié à une entreprise cliente"""
    STATUTS = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('revoked', 'Révoquée'),
        ('expired', 'Expirée'),
    ]

    organisme_formation = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='invitations_emises',
        limit_choices_to={'type_entreprise': 'of'}
    )
    entreprise_client = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='invitations_recues',
        limit_choices_to={'type_entreprise': 'client'}
    )
    email_contact = models.EmailField()
    token = models.CharField(max_length=64, unique=True, editable=False)
    statut = models.CharField(max_length=20, choices=STATUTS, default='pending')
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitations_acceptees')
    date_created = models.DateTimeField(auto_now_add=True)
    date_accepted = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = "Invitation entreprise"
        verbose_name_plural = "Invitations entreprises"

    def __str__(self):
        return f"Invitation {self.entreprise_client.nom} ({self.email_contact})"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
