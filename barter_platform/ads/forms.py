from django import forms
from .models import Ad, ExchangeProposal

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image', 'category', 'condition']


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment', 'status']
        widgets = {
            'ad_sender': forms.HiddenInput(),
            'ad_receiver': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        ad_sender = self.cleaned_data.get('ad_sender')

        if not ad_sender:
            raise forms.ValidationError('Выберите объявление для обмена.')

        return cleaned_data