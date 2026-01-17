from django import forms
from .models import TenantFormation, TypeFormation, Specialisation


class TenantFormationForm(forms.Form):
    """Formulaire pour ajouter/modifier une formation au catalogue de l'OF"""
    
    type_formation = forms.ModelChoiceField(
        queryset=TypeFormation.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type de formation",
        empty_label="-- Sélectionner --"
    )
    
    spécialisations = forms.ModelMultipleChoiceField(
        queryset=Specialisation.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Spécialisations proposées"
    )
    
    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        
        # Charger les spécialisations selon le TypeFormation sélectionné
        # Pour l'instant, afficher toutes les spécialisations
        # Le filtering par type se fera en JavaScript côté client
        self.fields['spécialisations'].queryset = Specialisation.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        type_formation = cleaned_data.get('type_formation')
        
        if not type_formation:
            raise forms.ValidationError("Veuillez sélectionner un type de formation")
        
        # Vérifier que la formation n'existe pas déjà pour ce tenant
        if self.tenant and TenantFormation.objects.filter(
            tenant=self.tenant,
            type_formation=type_formation
        ).exists():
            raise forms.ValidationError(
                f"La formation '{type_formation.nom}' existe déjà dans votre catalogue"
            )
        
        return cleaned_data
