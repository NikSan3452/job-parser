from django import forms


class SearchingForm(forms.Form):
    """
    Класс формы поиска.

    Этот класс наследуется от `forms.Form` и представляет собой форму поиска.
    Он содержит несколько полей: `job`, `city`, `date_from`, `date_to`, `experience`,
    `job_board`, `title_search` и `remote`.
    Поле `job` является текстовым полем для ввода названия вакансии.
    Поле `city` является текстовым полем для ввода города и не является обязательным.
    Поля `date_from` и `date_to` являются полями для выбора даты и не являются
    обязательными.
    Поле `experience` является выпадающим списком для выбора опыта работы и
    не является обязательным.
    Поле `job_board` является выпадающим списком для выбора площадки для поиска вакансий
    и не является обязательным.
    Поле `title_search` является флажком для поиска вакансий только по названию
    и не является обязательным.
    Поле `remote` является флажком для поиска удаленных вакансий и
    не является обязательным.
    """

    exp_values = (
        (0, "Не имеет значения"),
        (1, "Без опыта"),
        (2, "от 1 до 3 лет"),
        (3, "от 3 до 6 лет"),
        (4, "от 6 лет"),
    )

    job_board_values = (
        ("Не имеет значения", "Не имеет значения"),
        ("HeadHunter", "HeadHunter"),
        ("SuperJob", "SuperJob"),
        ("Zarplata", "Zarplata"),
        ("Trudvsem", "Trudvsem"),
        ("Habr career", "Habr career"),
        ("Geekjob", "Geekjob"),
    )

    job = forms.CharField(
        label="Что ищем ?",
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
    experience = forms.ChoiceField(
        label="Опыт работы",
        initial=exp_values[0],
        required=False,
        choices=exp_values,
        widget=forms.Select(),
    )
    job_board = forms.ChoiceField(
        label="Площадка",
        initial=job_board_values[0],
        required=False,
        choices=job_board_values,
        widget=forms.Select(),
    )
    title_search = forms.BooleanField(
        label="Искать в заголовках вакансий (чувствителен к регистру)",
        required=False,
        widget=forms.CheckboxInput(),
    )
    remote = forms.BooleanField(
        label="Удаленная работа", required=False, widget=forms.CheckboxInput()
    )
