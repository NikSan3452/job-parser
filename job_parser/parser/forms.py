from django import forms


class SearchingForm(forms.Form):
    job = forms.CharField(
        label="Специальность", widget=forms.TextInput(attrs={"placeholder": "Поиск"})
    )
    city = forms.CharField(
        label="Город", widget=forms.TextInput(attrs={"placeholder": "Город"})
    )
