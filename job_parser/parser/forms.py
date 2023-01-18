from django import forms


class SearchingForm(forms.Form):

    exp_values = (
        (0, "Не имеет значения"),
        (1, "Без опыта"),
        (2, "от 1 до 3 лет"),
        (3, "от 3 до 6 лет"),
        (4, "от 6 лет"),
    )

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
    experience = forms.ChoiceField(
        label="Опыт работы",
        initial=exp_values[0],
        required=False,
        choices=exp_values,
        widget=forms.Select(),
    )
