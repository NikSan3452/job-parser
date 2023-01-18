from django import forms


class SearchingForm(forms.Form):

    job = forms.CharField(
        label="Что ищем ?", widget=forms.TextInput(attrs={"placeholder": "Поиск"})
    )
    city = forms.CharField(
        label="Город", widget=forms.TextInput(attrs={"placeholder": "Город"})
    )
    date_from = forms.DateField(
        label="Дата от",
        required=False,
        widget=forms.DateInput(format="%m/%d/%Y", attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        label="Дата до",
        required=False,
        widget=forms.DateInput(format="%m/%d/%Y", attrs={"type": "date"}),
    )
    title_search = forms.BooleanField(
        label="Искать в заголовках вакансий", required=False, widget=forms.CheckboxInput()
    )
