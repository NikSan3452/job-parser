from django import forms


class SearchingForm(forms.Form):
    # TODO Добавить доки

    exp_values = (
        ("Не имеет значения", "Не имеет значения"),
        ("Нет опыта", "Нет опыта"),
        ("От 1 до 3 лет", "От 1 до 3 лет"),
        ("От 3 до 6 лет", "От 3 до 6 лет"),
        ("От 6 лет", "От 6 лет"),
    )

    job_board_values = (
        ("Не имеет значения", "Не имеет значения"),
        ("HeadHunter", "HeadHunter"),
        ("SuperJob", "SuperJob"),
        ("Zarplata", "Zarplata"),
        ("Trudvsem", "Trudvsem"),
        ("Habr", "Habr"),
        ("Geekjob", "Geekjob"),
    )

    title = forms.CharField(
        label="Что ищем ?",
        required=False,
        max_length=250,
        widget=forms.TextInput(attrs={"placeholder": "Поиск"}),
    )
    city = forms.CharField(
        label="Город",
        required=False,
        max_length=250,
        widget=forms.TextInput(attrs={"placeholder": "Город"}),
    )
    date_from = forms.DateField(
        label="Дата от",
        required=False,
        widget=forms.DateInput(format="%d/%m/%Y", attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        label="Дата до",
        required=False,
        widget=forms.DateInput(format="%d/%m/%Y", attrs={"type": "date"}),
    )
    experience = forms.MultipleChoiceField(
        label="Опыт работы",
        initial=exp_values[0],
        required=False,
        choices=exp_values,
        widget=forms.CheckboxSelectMultiple(),
    )
    job_board = forms.MultipleChoiceField(
        label="Площадка",
        initial=job_board_values[0],
        required=False,
        choices=job_board_values,
        widget=forms.CheckboxSelectMultiple(),
    )

    title_search = forms.BooleanField(
        label="Искать в заголовках вакансий",
        required=False,
        widget=forms.CheckboxInput(),
    )
    remote = forms.BooleanField(
        label="Удаленная работа", required=False, widget=forms.CheckboxInput()
    )