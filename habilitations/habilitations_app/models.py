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
        help_text="Tenant (OF) propriétaire – obligatoire pour les Clients"
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

class TypeFormation(models.Model):
    """Catégorie de formation (Habilitation, CACES, etc.)"""
    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=255)
    titre_officiel = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Titre complet avec normes/références (ex: Préparation à l'habilitation électrique - NF C18-510)"
    )
    description = models.TextField(blank=True)
    duree_validite_mois = models.IntegerField(null=True, blank=True)
    
    created_by_tenant = models.ForeignKey(
        'Tenant', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='formations_custom'
    )
    
    class Meta:
        verbose_name = "Type de formation"
        ordering = ['nom']
    
    def __str__(self):
        # Afficher le titre officiel s'il existe, sinon le nom
        return self.titre_officiel or self.nom


class Specialisation(models.Model):
    """
    Spécialisations DANS un type de formation
    Exemples :
    - Type "Habilitation" → Spécialisations [B1, B2, BC, BR, H0, H1V]
    - Type "CACES" → Spécialisations [Cat1, Cat3, Cat5]
    
    CLÉS : 
    - Chaque spécialisation = compétence indépendante
    - Formateur peut faire B1 mais PAS B2
    - Session peut avoir plusieurs spécialisations
    """
    type_formation = models.ForeignKey(TypeFormation, on_delete=models.CASCADE, related_name='specialisations')
    code = models.CharField(max_length=50)
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duree_validite_mois = models.IntegerField(null=True, blank=True, help_text="NULL = prendre le défaut du type")
    savoirs = models.TextField(blank=True, help_text="Savoirs théoriques spécifiques")
    savoirs_faire = models.TextField(blank=True, help_text="Savoir-faire pratiques spécifiques")
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('type_formation', 'code')
        ordering = ['type_formation', 'code']
        verbose_name = "Spécialisation"
    
    def __str__(self):
        return f"{self.type_formation.code} - {self.code}: {self.nom}"
    
    @property
    def duree_validite_effective(self):
        """Retourne la durée effective (spécifique ou défaut du type)"""
        return self.duree_validite_mois if self.duree_validite_mois else self.type_formation.duree_validite_mois_defaut


class TenantFormation(models.Model):
    """
    LIEN entre Tenant (OF) et formations qu'il propose
    
    Permet à chaque OF de CHOISIR :
    - Quels types de formations il propose
    - Quelles spécialisations pour chaque type
    - PLUSIEURS combinaisons différentes du même type
    
    Exemple : 
    - Kompetans propose Type "Habilitation" avec Spécialisations [B1, B2] (Pack Basique)
    - Kompetans propose Type "Habilitation" avec Spécialisations [BC, BR, H1V] (Pack Avancé)
    - Kompetans propose Type "CACES" avec Spécialisations [Cat1, Cat3]
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='formations_proposees')
    type_formation = models.ForeignKey(TypeFormation, on_delete=models.CASCADE)
    spécialisations = models.ManyToManyField(Specialisation, related_name='propositions_of')
    nom_package = models.CharField(max_length=100, blank=True, null=True, 
                                   help_text="Nom de l'offre (ex: 'Pack Basique', 'Formation Complète')")
    date_activation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Formation proposée par OF"
        ordering = ['tenant', 'type_formation', 'nom_package']
    
    def __str__(self):
        package = f" - {self.nom_package}" if self.nom_package else ""
        specs = ", ".join(self.spécialisations.values_list('code', flat=True)[:3])
        return f"{self.tenant.nom_public} → {self.type_formation.nom}{package} ({specs})"


class FormateurCompetence(models.Model):
    """
    LIEN entre Formateur et spécialisations qu'il peut enseigner
    
    Permet granularité : 
    - Formateur "Alice" peut faire [Habilitation-B1, Habilitation-B2]
    - Formateur "Alice" PEUT PAS faire [Habilitation-BC]
    - Formateur "Bob" peut faire [CACES-Cat1, CACES-Cat3]
    """
    formateur_profil = models.ForeignKey('ProfilUtilisateur', on_delete=models.CASCADE, related_name='competences')
    specialisation = models.ForeignKey(Specialisation, on_delete=models.CASCADE, related_name='formateurs')
    actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Certifications, expérience, etc.")
    
    class Meta:
        unique_together = ('formateur_profil', 'specialisation')
        verbose_name = "Compétence formateur"
    
    def __str__(self):
        return f"{self.formateur_profil.user.username} → {self.specialisation.code}"

class FormateurAffectation(models.Model):
    formateur = models.ForeignKey(
        'ProfilUtilisateur',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'formateur'},
        related_name='affectations'
    )
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        limit_choices_to={'type_entreprise': 'of'},
        related_name='formateurs_affectes'
    )
    actif = models.BooleanField(default=True)
    date_affectation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('formateur', 'entreprise')]
        indexes = [models.Index(fields=['entreprise', 'formateur', 'actif'])]

    def __str__(self):
        return f"{self.formateur} @ {self.entreprise}"


class Habilitation(models.Model):
    """
    ⚠️ MODÈLE LEGACY - DÉPRÉCIÉ
    Gardé pour compatibilité avec les anciennes données
    
    MIGRATION EN COURS vers : TypeFormation + Specialisation
    """
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
    # LIEN VERS NOUVEAU MODÈLE (pour migration)
    specialisation_liee = models.OneToOneField(
        Specialisation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='habilitation_legacy',
        help_text="Spécialisation moderne correspondante"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = "Habilitation (LEGACY)"
    
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
    """
    Model pour valider les compétences par spécialisation
    
    NOUVEAU : Validation directe par Specialisation
    - Permet validation indépendante de chaque spécialisation
    - Exemple : Stagiaire valide "Habilitation-B1" mais pas "Habilitation-B2"
    
    LEGACY : Anciens champs (type_competence, titre_competence) gardés pour compat
    """
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
    # ⭐ NOUVEAU CHAMP : Lien direct à la spécialisation
    specialisation = models.ForeignKey(
        Specialisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='validations',
        help_text="Spécialisation validée (remplace l'ancien système)"
    )
    
    # LEGACY : Rendre optionnels pour migration progressive
    type_competence = models.CharField(max_length=20, choices=COMPETENCE_TYPES, blank=True)
    titre_competence = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    valide = models.BooleanField(default=False)
    commentaires_validateur = models.TextField(blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    validateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validations')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['specialisation', 'type_competence', 'titre_competence']
        indexes = [
            models.Index(fields=['tenant', 'type_competence']),
            models.Index(fields=['specialisation', 'valide']),  # ⭐ Index nouvelle logique
        ]
    
    def __str__(self):
        if self.specialisation:
            return f"{self.formation} - {self.specialisation.code}"
        return f"{self.formation} - {self.titre_competence}"
    
    class Meta:
        unique_together = ('formation', 'titre_competence')
        ordering = ['type_competence', 'titre_competence']
        indexes = [
            models.Index(fields=['tenant', 'type_competence']),
        ]
    
    def __str__(self):
        return f"{self.formation} - {self.titre_competence}"


class Titre(models.Model):
    """
    Model pour les titres/certifications
    
    NOUVEAU : Un titre certifie UNE spécialisation unique
    - Exemple : Titre certifie "Habilitation-B1" (pas "Habilitation" en entier)
    - Un stagiaire peut avoir plusieurs titres pour plusieurs spécialisations
    
    LEGACY : Champ habilitation gardé pour compat avec anciennes données
    """
    STATUTS = [
        ('attente', 'En attente'),
        ('delivre', 'Délivré'),
        ('expire', 'Expiré'),
        ('renouvele', 'Renouvelé'),
    ]
    
    stagiaire = models.ForeignKey(Stagiaire, on_delete=models.CASCADE, related_name='titres')
    formation = models.OneToOneField(Formation, on_delete=models.CASCADE)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='titres'
    )
    
    # ⭐ NOUVEAU CHAMP : Spécialisation certifiée (OBLIGATOIRE pour nouveau)
    specialisation = models.ForeignKey(
        Specialisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='titres',
        help_text="Spécialisation certifiée par ce titre"
    )
    
    # LEGACY : Habilitation ancienne (remplacée par specialisation)
    habilitation = models.ForeignKey(
        Habilitation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='titres_legacy'
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
            models.Index(fields=['specialisation', 'statut']),  # ⭐ Index nouvelle logique
        ]
    
    def __str__(self):
        if self.specialisation:
            return f"{self.numero_titre} - {self.stagiaire.nom_complet} ({self.specialisation.code})"
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
    """
    Model pour les sessions de formation créées par les secrétaires
    
    NOUVEAU : Support multi-spécialisation
    - Une session "Formation Électrique Complète" = Type "Habilitation" + Spécialisations [B1, B2, BR]
    - Une session "CACES Cat1" = Type "CACES" + Spécialisation [Cat1]
    
    VALIDATION : Le formateur assigné doit avoir les compétences pour TOUTES les spécialisations
    """
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
    
    # ⭐ NOUVEAU : Type de formation (remplace habilitation)
    type_formation = models.ForeignKey(
        TypeFormation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sessions',
        help_text="Type de formation dispensée"
    )
    
    # ⭐ NOUVEAU : Spécialisations dispensées dans cette session (M2M)
    spécialisations = models.ManyToManyField(
        Specialisation,
        blank=True,
        related_name='sessions',
        help_text="Spécialisations enseignées dans cette session"
    )
    
    # ⭐ NOUVEAU : Plusieurs formateurs par session (M2M)
    formateurs = models.ManyToManyField(
        'ProfilUtilisateur',
        blank=True,
        related_name='sessions_formateur',
        limit_choices_to={'role': 'formateur'},
        help_text="Formateurs responsables de la session - doivent maîtriser TOUTES les spécialisations"
    )
    
    # LEGACY : Habilitation pour compat (garder provisoire)
    habilitation = models.ForeignKey(
        Habilitation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions_legacy',
        help_text="LEGACY - Voir type_formation et spécialisations"
    )

    # LEGACY : Formateur unique (User) - garder pour compat, utiliser formateurs M2M en priorité
    formateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions_assignees',
        help_text="Formateur responsable de la session - doit maîtriser TOUTES les spécialisations"
    )
    
    date_debut = models.DateField()
    date_fin = models.DateField()
    lieu = models.CharField(max_length=255, blank=True)
    
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
            models.Index(fields=['type_formation', 'statut']),  # ⭐ Index nouvelle logique
        ]
    
    def __str__(self):
        if self.type_formation:
            spec_codes = ", ".join([s.code for s in self.spécialisations.all()])
            return f"{self.numero_session} - {self.type_formation.nom} ({spec_codes}) - {self.date_debut}"
        return f"{self.numero_session} - {self.habilitation.code if self.habilitation else 'N/A'} ({self.date_debut})"
    
    @property
    def places_restantes(self):
        """Retourne le nombre de places disponibles"""
        stagiaires_inscrits = self.formations_session.count()
        return max(0, self.nombre_places - stagiaires_inscrits)
    
    @property
    def est_complete(self):
        """Retourne True si la session est complète"""
        return self.places_restantes == 0
    
    def formateur_has_competences(self):
        """
        Vérifie que tous les formateurs affectés maîtrisent TOUTES les spécialisations de la session.
        Legacy : si aucun formateur M2M, on tolère (True).
        """
        specs = list(self.spécialisations.all())
        if not specs:
            return True
        formateurs = list(self.formateurs.all())
        if not formateurs:
            return True  # tolérance legacy, à durcir si besoin
        for f in formateurs:
            ok = FormateurCompetence.objects.filter(
                formateur_profil=f,
                specialisation__in=specs,
                actif=True
            ).count() == len(specs)
            if not ok:
                return False
        return True

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
    
    TYPE_FORMATION_CHOICES = [
        ('intra', 'Intra-entreprise (sur votre site)'),
        ('inter', 'Inter-entreprise (chez l\'OF)'),
    ]
    
    LIEU_FORMATION_CHOICES = [
        ('sur_site', 'Sur le site du client'),
        ('chez_of', 'Au siège de l\'organisme de formation'),
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
    type_formation = models.CharField(
        max_length=10,
        choices=TYPE_FORMATION_CHOICES,
        default='intra',
        help_text="Type de formation : intra-entreprise ou inter-entreprise"
    )
    lieu_formation = models.CharField(
        max_length=20,
        choices=LIEU_FORMATION_CHOICES,
        default='sur_site',
        help_text="Lieu de déroulement de la formation"
    )
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
    """
    Demandes pour stagiaires INDÉPENDANTS uniquement
    
    CAS D'USAGE :
    - Auto-entrepreneur contacte l'OF directement
    - Freelance veut une formation
    - Particulier sans lien entreprise
    
    ⚠️ Pour les salariés d'entreprise : utiliser DemandeFormation
    """
    STATUTS = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('integree', 'Intégrée à une session'),
        ('refusee', 'Refusée'),
    ]
    
    # Lien au stagiaire existant OU infos manuelles
    stagiaire_existant = models.ForeignKey(
        Stagiaire, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='demandes_stagiaires',
        help_text="Si stagiaire déjà dans la base"
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='demandes_stagiaires'
    )
    
    # ⚠️ PLUS DE CHAMP entreprise (toujours NULL pour indépendants)
    # Infos du stagiaire indépendant (si pas dans la base)
    nom = models.CharField(max_length=100, blank=True)
    prenom = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    statut_professionnel = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Auto-entrepreneur, Freelance, Particulier, etc."
    )
    
    # ⭐ NOUVEAU : Type de formation (optionnel, pour filtrage rapide)
    type_formation = models.ForeignKey(
        TypeFormation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demandes_independants',
        help_text="Type de formation demandée"
    )
    
    # ⭐ NOUVEAU : Spécialisations demandées
    spécialisations_demandees = models.ManyToManyField(
        Specialisation,
        blank=True,
        related_name='demandes_independants',
        help_text="Spécialisations précises demandées"
    )
    
    # LEGACY : Habilitations (garder provisoire pour compat)
    habilitations_demandees = models.ManyToManyField(
        Habilitation,
        blank=True,
        related_name='demandes_independants_legacy'
    )
    
    # Renouvellement (un indépendant peut renouveler)
    est_renouvellement = models.BooleanField(default=False)
    titre_renouvelle = models.ForeignKey(
        Titre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demande_renouvellement_independant'
    )
    
    notes = models.TextField(blank=True, help_text="Informations complémentaires")
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    session_assignee = models.ForeignKey(
        SessionFormation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='demandes_independants'
    )
    stagiaire_cree = models.ForeignKey(
        Stagiaire, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='demande_origine_independant',
        help_text="Stagiaire créé à partir de cette demande (entreprise=NULL)"
    )
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    traite_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_independants_traitees')
    consentement_at = models.DateTimeField(null=True, blank=True)
    consentement_ip = models.GenericIPAddressField(null=True, blank=True)
    consentement_user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_demande']
        verbose_name = "Demande stagiaire indépendant"
        verbose_name_plural = "Demandes stagiaires indépendants"
        indexes = [
            models.Index(fields=['tenant', 'statut']),
            models.Index(fields=['type_formation', 'statut']),
        ]

    def __str__(self):
        spec_list = ", ".join([s.code for s in self.spécialisations_demandees.all()])
        if spec_list:
            return f"Demande indépendant {self.nom_complet} - {spec_list} - {self.get_statut_display()}"
        return f"Demande indépendant {self.nom_complet} - {self.get_statut_display()}"

    @property
    def nom_complet(self):
        if self.stagiaire_existant:
            return str(self.stagiaire_existant)
        return f"{self.prenom} {self.nom}".strip()

class ProfilUtilisateur(models.Model):
    """Profil utilisateur liant un User à une Entreprise avec rôle spécifique
    
    Rôles B2B2C:
    - super_admin: Éditeur SaaS (vous) - gère tous les OF
    - admin_of: Administrateur OF - gère ses Clients + stagiaires indépendants
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


# Signals pour créer automatiquement un ProfilUtilisateur
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un ProfilUtilisateur pour chaque nouvel utilisateur"""
    if created:
        ProfilUtilisateur.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil quand l'utilisateur est sauvegardé"""
    if hasattr(instance, 'profil'):
        instance.profil.save()

@receiver(post_save, sender='habilitations_app.ProfilUtilisateur')
def create_of_entreprise_tenant(sender, instance, created, **kwargs):
    """Créer automatiquement Entreprise et Tenant pour les admin_of"""
    # Ne traiter que si le rôle est admin_of et qu'il n'y a pas d'entreprise
    if instance.role == 'admin_of' and not instance.entreprise:
        username = instance.user.username
        
        # Créer l'entreprise si elle n'existe pas
        entreprise, _ = Entreprise.objects.get_or_create(
            nom=username,
            defaults={
                'type_entreprise': 'of',
                'adresse': f'À configurer',
                'code_postal': '00000',
                'ville': 'À configurer',
                'telephone': '0000000000',
                'email': instance.user.email or f'{username.lower()}@example.com'
            }
        )
        
        # Créer le tenant si il n'existe pas
        tenant, _ = Tenant.objects.get_or_create(
            organisme_formation=entreprise,
            defaults={
                'nom_public': f'{username} Formation',
                'slug': slugify(username),
                'actif': True
            }
        )
        
        # Associer au profil
        instance.entreprise = entreprise
        instance.tenant = tenant
        # Utiliser update pour éviter une boucle de signals
        ProfilUtilisateur.objects.filter(pk=instance.pk).update(
            entreprise=entreprise,
            tenant=tenant
        )
