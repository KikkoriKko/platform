# ads/forms.py
from django import forms
from .models import Ad, ExchangeProposal

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']

class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment', 'status']
        widgets = {
            'ad_sender': forms.HiddenInput(),
            'ad_receiver': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        }
