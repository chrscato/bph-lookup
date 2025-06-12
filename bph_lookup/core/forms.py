from django import forms
from django.core.validators import RegexValidator

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