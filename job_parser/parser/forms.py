from django import forms


class SearchingForm(forms.Form):
    """
    Класс для формы поиска вакансий.

    Класс наследуется от класса `Form` модуля `forms` и содержит поля для ввода 
    информации для поиска вакансий. Поля включают в себя название вакансии, город, 
    даты начала и конца поиска, опыт работы, площадку для поиска, флажки для поиска 
    в заголовках вакансий и удаленной работы.

    Attributes:
        exp_values (tuple[tuple[str, str], ...]): Кортеж с кортежами из двух строк с 
        возможными значениями опыта работы.
        job_board_values (tuple[tuple[str, str], ...]): Кортеж с кортежами из двух 
        строк с возможными значениями площадок для поиска.
        title (CharField): Поле для ввода названия вакансии.
        city (CharField): Поле для ввода города.
        date_from (DateField): Поле для выбора даты начала поиска.
        date_to (DateField): Поле для выбора даты конца поиска.
        experience (MultipleChoiceField): Поле для выбора опыта работы.
        job_board (MultipleChoiceField): Поле для выбора площадки для поиска.
        title_search (BooleanField): Флажок для поиска в заголовках вакансий.
        remote (BooleanField): Флажок для поиска удаленной работы.
    """
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
        widget=forms.CheckboxSelectMultiple,
    )
    job_board = forms.MultipleChoiceField(
        label="Площадка",
        initial=job_board_values[0],
        required=False,
        choices=job_board_values,
        widget=forms.CheckboxSelectMultiple,
    )

    title_search = forms.BooleanField(
        label="Искать в заголовках вакансий",
        required=False,
        widget=forms.CheckboxInput,
    )
    remote = forms.BooleanField(
        label="Удаленная работа", required=False, widget=forms.CheckboxInput
    )