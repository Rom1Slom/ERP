from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div
from .models import (
    Stagiaire, Formation, ValidationCompetence, Titre, 
    AvisFormation, Entreprise, Habilitation, RenouvellementHabilitation,
    DemandeStagiaire, SessionFormation, InvitationEntreprise,
    TypeFormation, Specialisation
)


class EntrepriseForm(forms.ModelForm):
    """Form pour créer/modifier une entreprise"""
    class Meta:
        model = Entreprise
        fields = ['nom', 'email', 'telephone', 'adresse', 'code_postal', 'ville']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Informations de l\'entreprise',
                Row(Column('nom', css_class='col-md-6'),
                    Column('email', css_class='col-md-6')),
                Row(Column('telephone', css_class='col-md-6'),
                    Column('code_postal', css_class='col-md-3'),
                    Column('ville', css_class='col-md-3')),
                'adresse',
            ),
            Submit('submit', 'Enregistrer', css_class='btn btn-primary mt-3')
        )


class InvitationEntrepriseForm(forms.ModelForm):
    """Form pour créer une invitation PME"""
    class Meta:
        model = InvitationEntreprise
        fields = ['email_contact']
        widgets = {
            'email_contact': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email du responsable Client'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset("Invitation",
                'email_contact',
            ),
            Submit('submit', "Envoyer l'invitation", css_class='btn btn-primary mt-3')
        )


class StagiaireForm(forms.ModelForm):
    """Form pour créer/modifier un stagiaire"""
    class Meta:
        model = Stagiaire
        fields = ['nom', 'prenom', 'email', 'telephone', 'poste', 'date_embauche', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre tous les champs facultatifs sauf nom et prenom
        self.fields['email'].required = False
        self.fields['telephone'].required = False
        self.fields['poste'].required = False
        self.fields['date_embauche'].required = False
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Informations personnelles',
                Row(Column('prenom', css_class='col-md-6'),
                    Column('nom', css_class='col-md-6')),
                Row(Column('email', css_class='col-md-6'),
                    Column('telephone', css_class='col-md-6')),
            ),
            Fieldset('Emploi',
                Row(Column('poste', css_class='col-md-8'),
                    Column('date_embauche', css_class='col-md-4')),
                'actif',
            ),
            Submit('submit', 'Enregistrer', css_class='btn btn-primary mt-3')
        )


class FormationForm(forms.ModelForm):
    """Form pour créer/modifier une formation"""
    class Meta:
        model = Formation
        fields = ['habilitation', 'organisme_formation', 'date_debut', 'date_fin_prevue', 'numero_session', 'notes']
        widgets = {
            'habilitation': forms.Select(attrs={'class': 'form-control'}),
            'organisme_formation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'OF'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'numero_session': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Détails de formation',
                'habilitation',
                'organisme_formation',
            ),
            Fieldset('Calendrier',
                Row(Column('date_debut', css_class='col-md-6'),
                    Column('date_fin_prevue', css_class='col-md-6')),
                'numero_session',
            ),
            'notes',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary mt-3')
        )


class ValidationCompetenceForm(forms.ModelForm):
    """Form pour valider les compétences"""
    class Meta:
        model = ValidationCompetence
        fields = ['type_competence', 'titre_competence', 'description', 'valide', 'commentaires_validateur']
        widgets = {
            'type_competence': forms.Select(attrs={'class': 'form-control'}),
            'titre_competence': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commentaires_validateur': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Compétence',
                'type_competence',
                'titre_competence',
                'description',
            ),
            Fieldset('Validation',
                'valide',
                'commentaires_validateur',
            ),
            Submit('submit', 'Valider', css_class='btn btn-primary mt-3')
        )


class AvisFormationForm(forms.ModelForm):
    """Form pour créer l'avis de formation"""
    class Meta:
        model = AvisFormation
        fields = ['avis', 'observations', 'points_forts', 'points_amelioration', 'recommandations', 'formateur_nom', 'signature_formateur']
        widgets = {
            'avis': forms.Select(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'points_forts': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'points_amelioration': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommandations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'formateur_nom': forms.TextInput(attrs={'class': 'form-control'}),
            'signature_formateur': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Avis de formation',
                'avis',
                'observations',
            ),
            Fieldset('Évaluation',
                'points_forts',
                'points_amelioration',
                'recommandations',
            ),
            Fieldset('Formateur',
                'formateur_nom',
                'signature_formateur',
            ),
            Submit('submit', 'Enregistrer', css_class='btn btn-primary mt-3')
        )


class TitreForm(forms.ModelForm):
    """Form pour créer/modifier un titre d'habilitation"""
    class Meta:
        model = Titre
        fields = ['numero_titre', 'date_delivrance', 'date_expiration', 'statut', 'notes_avis']
        widgets = {
            'numero_titre': forms.TextInput(attrs={'class': 'form-control'}),
            'date_delivrance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_expiration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'notes_avis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Identification du titre',
                'numero_titre',
            ),
            Fieldset('Validité',
                Row(Column('date_delivrance', css_class='col-md-6'),
                    Column('date_expiration', css_class='col-md-6')),
            ),
            Fieldset('Statut',
                'statut',
                'notes_avis',
            ),
            Submit('submit', 'Enregistrer', css_class='btn btn-primary mt-3')
        )


class RenouvellementForm(forms.ModelForm):
    """Form pour créer un renouvellement d'habilitation"""
    class Meta:
        model = RenouvellementHabilitation
        fields = ['date_renouvellement_prevue', 'notes']
        widgets = {
            'date_renouvellement_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Renouvellement',
                'date_renouvellement_prevue',
                'notes',
            ),
            Submit('submit', 'Planifier le renouvellement', css_class='btn btn-primary mt-3')
        )


class FiltreFormationForm(forms.Form):
    """Form pour filtrer les formations"""
    stagiaire = forms.ModelChoiceField(
        queryset=Stagiaire.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    habilitation = forms.ModelChoiceField(
        queryset=Habilitation.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    statut = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Formation._meta.get_field('statut').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class DemandeStagiaireForm(forms.ModelForm):
    """Form pour qu'un stagiaire indépendant soumette une demande"""
    
    # Champ pour sélectionner un stagiaire existant
    stagiaire_existant = forms.ModelChoiceField(
        queryset=Stagiaire.objects.none(),
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Sélectionner un stagiaire existant (optionnel)"
    )
    
    # Champs pour spécialisations multiples
    spécialisations_demandees = forms.ModelMultipleChoiceField(
        queryset=Specialisation.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label="Spécialisations demandées"
    )
    
    class Meta:
        model = DemandeStagiaire
        fields = ['nom', 'prenom', 'email', 'telephone', 'statut_professionnel', 'notes']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du stagiaire'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom du stagiaire'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+33 6 12 34 56 78'}),
            'poste': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fonction dans l\'entreprise'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Informations complémentaires (optionnel)'}),
        }
    
    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Charger les stagiaires de l'entreprise
        if entreprise:
            self.fields['stagiaire_existant'].queryset = Stagiaire.objects.filter(entreprise=entreprise)
        
        # Rendre les champs facultatifs pour l'entrée manuelle
        self.fields['nom'].required = False
        self.fields['prenom'].required = False
        self.fields['email'].required = False
        self.fields['telephone'].required = False
        self.fields['poste'].required = False
        self.fields['date_embauche'].required = False
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h4 class="mb-3">Sélectionnez un stagiaire</h4>'),
            Fieldset('',
                'stagiaire_existant',
            ),
            HTML('<hr><h4 class="mb-3">Ou entrez les informations manuellement</h4>'),
            Fieldset('Identité',
                Row(Column('prenom', css_class='col-md-6'),
                    Column('nom', css_class='col-md-6')),
            ),
            Fieldset('Contact',
                Row(Column('email', css_class='col-md-6'),
                    Column('telephone', css_class='col-md-6')),
            ),
            Fieldset('Emploi',
                Row(Column('poste', css_class='col-md-8'),
                    Column('date_embauche', css_class='col-md-4')),
            ),
            HTML('<hr><h4 class="mb-3">Habilitations/Certifications demandées</h4>'),
            Fieldset('',
                'habilitations_demandees',
            ),
            Fieldset('Notes',
                'notes',
            ),
            Submit('submit', 'Soumettre la demande', css_class='btn btn-success btn-lg mt-3')
        )
    
    def clean(self):
        """Valider que soit un stagiaire existant, soit des infos manuelles sont fournis"""
        cleaned_data = super().clean()
        stagiaire_existant = cleaned_data.get('stagiaire_existant')
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')
        
        if not stagiaire_existant and not (nom and prenom):
            raise forms.ValidationError(
                "Vous devez soit sélectionner un stagiaire existant, soit fournir au moins son nom et prénom."
            )
        
        return cleaned_data


class SessionFormationForm(forms.ModelForm):
    """Form pour créer/modifier une session de formation"""
    class Meta:
        model = SessionFormation
        fields = ['numero_session', 'type_formation', 'spécialisations', 
                  'date_debut', 'date_fin', 'lieu', 'formateurs',
                  'nombre_places', 'statut', 'notes']
        widgets = {
            'numero_session': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SESS-2026-001'}),
            'type_formation': forms.Select(attrs={'class': 'form-control'}),
            'spécialisations': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'formateurs': forms.SelectMultiple(attrs={
                'class': 'form-control', 
                'size': '5',
                'style': 'height: auto;'
            }),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse du lieu de formation'}),
            'nombre_places': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '50'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'type_formation': 'Type de formation',
            'spécialisations': 'Spécialisations',
            'formateurs': 'Formateurs',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les formateurs disponibles pour l'OF courant
        if user and hasattr(user, 'profil'):
            from .services import formateurs_of
            of = user.profil.entreprise
            if of:
                self.fields['formateurs'].queryset = formateurs_of(of)


class AssignerDemandeForm(forms.Form):
    """Form pour assigner des demandes de stagiaires à une session"""
    demandes = forms.ModelMultipleChoiceField(
        queryset=DemandeStagiaire.objects.filter(statut='en_attente'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Sélectionner les stagiaires"
    )
    
    def __init__(self, *args, habilitation=None, **kwargs):
        super().__init__(*args, **kwargs)
        if habilitation:
            # Filtrer les demandes qui contiennent cette habilitation dans leurs habilitations_demandees
            self.fields['demandes'].queryset = DemandeStagiaire.objects.filter(
                statut='en_attente',
                habilitations_demandees=habilitation
            )

# ==================== FORMATEURS ====================

class FormateurForm(forms.Form):
    """Formulaire pour créer/modifier un formateur"""
    # Option 1 : Sélectionner un user existant
    user_id = forms.ModelChoiceField(
        queryset=User.objects.filter(profil__role='formateur').select_related('profil'),
        required=False,
        label="Utilisateur existant formateur",
        empty_label="-- Créer un nouvel utilisateur --"
    )
    
    # Option 2 : Créer un nouvel utilisateur
    first_name = forms.CharField(max_length=150, required=False, label="Prénom")
    last_name = forms.CharField(max_length=150, required=False, label="Nom")
    email = forms.EmailField(required=False, label="Email")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone")
    
    # Statut
    actif = forms.BooleanField(required=False, initial=True, label="Actif")
    
    def clean(self):
        cleaned = super().clean()
        user_id = cleaned.get('user_id')
        first_name = cleaned.get('first_name')
        last_name = cleaned.get('last_name')
        email = cleaned.get('email')
        
        # Vérifier qu'on a soit un user existant, soit les infos pour en créer un
        if not user_id:
            if not (first_name and last_name and email):
                raise forms.ValidationError(
                    "Renseigner un utilisateur existant OU créer un nouvel utilisateur (prénom, nom, email requis)."
                )
        return cleaned


class FormateurCompetencesForm(forms.Form):
    """Formulaire pour assigner les spécialisations à un formateur"""
    spécialisations = forms.ModelMultipleChoiceField(
        queryset=Specialisation.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Spécialisations maîtrisées"
    )
    
    def __init__(self, *args, specialisations_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        if specialisations_qs:
            self.fields['spécialisations'].queryset = specialisations_qs