from django import forms

from .models import Poll, PollOption

class PollCreationForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = [
            'cover',
            'title',
            'description',
            'category',
            'is_public',
            'is_anonymous',
            'results_visible',
            'e'
        ]