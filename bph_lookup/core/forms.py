from django import forms
from django.core.validators import RegexValidator
from django.db import connection
from .models import State

class MedicareRateLookupForm(forms.Form):
    zip_code = forms.CharField(
        max_length=5,
        min_length=5,
        required=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{5}$',
                message='ZIP code must be exactly 5 digits',
                code='invalid_zip'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 5-digit ZIP code',
            'pattern': '[0-9]{5}'
        })
    )
    
    procedure_code = forms.CharField(
        max_length=5,
        min_length=5,
        required=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{5}$',
                message='CPT code must be exactly 5 digits',
                code='invalid_cpt'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 5-digit CPT code',
            'pattern': '[0-9]{5}'
        })
    )

    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code']
        if not zip_code.isdigit():
            raise forms.ValidationError('ZIP code must contain only numbers')
        return zip_code

    def clean_procedure_code(self):
        procedure_code = self.cleaned_data['procedure_code']
        if not procedure_code.isdigit():
            raise forms.ValidationError('CPT code must contain only numbers')
        return procedure_code


class WorkersCompRateLookupForm(forms.Form):
    """Lookup workers' compensation fee schedule rates by state and CPT code."""

    state = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    procedure_code = forms.CharField(
        max_length=5,
        min_length=5,
        required=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{5}$',
                message='CPT code must be exactly 5 digits',
                code='invalid_cpt',
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 5-digit CPT code',
            'pattern': '[0-9]{5}'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT state FROM fee_schedule_rate ORDER BY state")
            states = cursor.fetchall()
            self.fields['state'].choices = [(state[0], state[0]) for state in states]

    def clean_procedure_code(self):
        procedure_code = self.cleaned_data['procedure_code']
        if not procedure_code.isdigit():
            raise forms.ValidationError('CPT code must contain only numbers')
        return procedure_code
