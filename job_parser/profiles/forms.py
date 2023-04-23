from django import forms


class ProfileForm(forms.Form):
    """
    Класс формы профиля.

    Этот класс наследуется от `forms.Form` и представляет собой форму профиля.
    Он содержит три поля: `city`, `job` и `subscribe`.
    Поле `city` является текстовым полем для ввода города.
    Поле `job` является текстовым полем для ввода названия вакансии.
    Поле `subscribe` является флажком для подписки на рассылку и не является
    обязательным.
    """

    city = forms.CharField(label="Город", widget=forms.TextInput())
    job = forms.CharField(label="Вакансия", widget=forms.TextInput())
    subscribe = forms.BooleanField(
        label="Подписаться на рассылку", required=False, widget=forms.CheckboxInput()
    )
