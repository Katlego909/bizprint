from django import forms
from .models import DesignRequest

class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['packages', 'additional_instructions', 'uploaded_files']
        widgets = {
            'packages': forms.CheckboxSelectMultiple,
            'additional_instructions': forms.Textarea(attrs={'rows': 4}),
        }
