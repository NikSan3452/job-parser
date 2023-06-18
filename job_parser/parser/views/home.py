from parser.forms import SearchingForm

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormView


class HomePageView(FormView):
    """Класс представления домашней страницы.

    Этот класс наследуется от `FormView` и используется для отображения домашней
    страницы приложения.

    Args:
        FormView (FormView): Представление для отображения формы и рендеринга 
        ответа шаблона.

    Attributes:
        template_name (str): Имя шаблона для отображения страницы.
        form_class (type): Класс формы для обработки данных.
        success_url (str): URL-адрес для перенаправления после успешной отправки формы.
    """

    template_name: str = "parser/home.html"
    form_class = SearchingForm
    success_url: str = "/list/"

    def get(self, request: HttpRequest) -> HttpResponse:
        """Метод обработки GET-запроса.

        Этот метод принимает объект запроса `request` и обрабатывает его.
        Если в сессии пользователя нет ключа сессии, то он сохраняется.
        Затем получается контекст и отображается страница с использованием этого контекста.

        Args:
            request (HttpRequest): Объект запроса

        Returns:
            HttpResponse: Ответ с отображением страницы
        """
        super().get(request)
        context = self.get_context_data()
        return self.render_to_response(context)

    def form_valid(self, form) -> HttpResponseRedirect:
        """Метод обработки валидной формы.

        Этот метод вызывается, когда форма прошла валидацию.
        Он перенаправляет пользователя на URL-адрес, указанный в атрибуте `success_url`.

        Args:
            form (Form): Объект формы

        Returns:
            HttpResponseRedirect: Ответ с перенаправлением на другую страницу
        """
        return super().form_valid(form)
