from django import forms

from dashboard.models import UnSubscribe


class UnSubscribeForm(forms.ModelForm):

    class Meta:
        model = UnSubscribe
        fields = ['email']
