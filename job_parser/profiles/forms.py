from django import forms


class ProfileForm(forms.Form):
    city = forms.CharField(label="Город", widget=forms.TextInput())
    job = forms.CharField(label="Вакансия", widget=forms.TextInput())
    subscribe = forms.BooleanField(
        label="Подписаться на рассылку", widget=forms.CheckboxInput()
    )
