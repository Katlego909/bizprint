from django import forms
from .models import DesignRequest

class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = [
            'email', 'packages', 'additional_instructions', 'uploaded_files',
            'brand_colors', 'target_audience', 'design_preferences', 
            'inspiration_links', 'timeline_preference'
        ]
        widgets = {
            'packages': forms.CheckboxSelectMultiple,
            'additional_instructions': forms.Textarea(attrs={'rows': 4}),
            'target_audience': forms.Textarea(attrs={'rows': 3}),
            'design_preferences': forms.Textarea(attrs={'rows': 3}),
            'inspiration_links': forms.Textarea(attrs={'rows': 2}),
        }
