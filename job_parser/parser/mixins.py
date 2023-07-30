from dataclasses import dataclass
from typing import Any, Awaitable

from django.contrib.auth.mixins import AccessMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from logger import setup_logging
from loguru import logger

from parser.forms import SearchingForm
from parser.models import UserVacancies, Vacancies
from parser.utils import Utils

# Логирование
setup_logging()

utils = Utils()


@dataclass
class RequestParams:
    """
    Класс для хранения параметров запроса.

    Класс использует декоратор `dataclass` и содержит атрибуты для хранения параметров
    запроса.

    Attributes:
        title (str | None): Строка с названием вакансии.
        city (str | None): Строка с городом.
        date_from (str | None): Строка с датой начала поиска.
        date_to (str | None): Строка с датой конца поиска.
        salary_from (int | None): Число с начальной суммой зарплаты.
        salary_to (int | None): Число с конечной суммой зарплаты.
        experience (str | None): Строка с опытом работы.
        job_board (str | None): Строка с площадкой для поиска.
        remote (bool | None): Строка с флажком удаленной работы.
        title_search (bool | None): Строка с флажком поиска в заголовках вакансий.
    """

    title: str | None
    city: str | None
    date_from: str | None
    date_to: str | None
    salary_from: int | None
    salary_to: int | None
    experience: str | None
    job_board: str | None
    remote: bool | None
    title_search: bool | None


class FormDataParser:
    """Класс для извлечения данных из формы и преобразования их в параметры запроса.

    Этот класс предназначен для извлечения данных из формы поиска вакансий и
    преобразования их в объект параметров запроса.
    """

    def get_form_data(self, form: SearchingForm) -> dict:
        """
        Метод для получения данных из формы.

        Метод принимает на вход объект класса `SearchingForm` и возвращает словарь
        с данными из формы.
        Метод проверяет, является ли форма действительной с помощью
        метода `is_valid`. Если форма действительна, то метод создает список с именами
        полей формы и проходит по всем элементам списка. Для каждого элемента списка
        метод получает значение соответствующего поля из атрибута `cleaned_data`
        объекта `form` и сохраняет его в словарь с данными из формы. В конце работы
        метода возвращается словарь с данными из формы.

        Args:
            form (SearchingForm): Объект класса `SearchingForm`.

        Returns:
            dict: Словарь с данными из формы.
        """
        form_data: dict = {}
        if form.is_valid():
            fields = [
                "city",
                "title",
                "date_from",
                "date_to",
                "salary_from",
                "salary_to",
                "title_search",
                "experience",
                "remote",
                "job_board",
            ]

            for field in fields:
                value = form.cleaned_data.get(field)
                form_data[field] = value

        return form_data

    def get_request_params(self, form_data: dict) -> RequestParams:
        """
        Метод для получения параметров запроса.

        Метод принимает на вход словарь с данными из формы и возвращает объект класса
        `RequestParams` с параметрами запроса.
        Метод создает объект класса
        `RequestParams`, передавая ему значения атрибутов, полученные с помощью методов
        `get_title`, `get_city`, `get_date_from`, `get_date_to`, `get_experience`,
        `get_job_board`, `get_remote` и `get_title_search`.
        Полученный объект возвращается как результат работы метода.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            RequestParams: Объект класса `RequestParams` с параметрами запроса.
        """
        params = RequestParams(
            title=self.get_title(form_data),
            city=self.get_city(form_data),
            date_from=self.get_date_from(form_data),
            date_to=self.get_date_to(form_data),
            salary_from=self.get_salary_from(form_data),
            salary_to=self.get_salary_to(form_data),
            experience=self.get_experience(form_data),
            job_board=self.get_job_board(form_data),
            remote=self.get_remote(form_data),
            title_search=self.get_title_search(form_data),
        )
        return params

    def get_title(self, form_data: dict) -> str | None:
        """
        Метод для получения названия вакансии из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку
        с названием вакансии или `None`.
        Метод получает значение ключа "title" из словаря с данными из формы.
        Если значение равно `None`, то метод возвращает `None`.
        В противном случае метод удаляет пробельные символы с начала и конца строки
        и возвращает полученную строку.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с названием вакансии или `None`.
        """
        title = form_data.get("title", None)
        return title.strip() if title else None

    def get_city(self, form_data: dict) -> str | None:
        """
        Метод для получения города из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку
        с городом или `None`.
        Метод получает значение ключа "city" из словаря с данными из формы.
        Если значение равно `None`, то метод возвращает `None`. В противном случае
        метод преобразует строку в нижний регистр, удаляет пробельные символы с начала
        и конца строки и возвращает полученную строку.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с городом или `None`.
        """
        city = form_data.get("city", None)
        return city.lower().strip() if city else None

    def get_date_from(self, form_data: dict) -> str | None:
        """
        Метод для получения даты начала поиска из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку с датой
        начала поиска или `None`.
        Метод получает значение ключа "date_from" из словаря с данными из формы.
        Затем метод вызывает функцию `check_date_from` модуля `utils` с передачей ему
        полученного значения и возвращает полученное значение.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с датой начала поиска или `None`.
        """
        date_from = form_data.get("date_from", None)
        date_from = utils.check_date_from(date_from)
        return date_from

    def get_date_to(self, form_data: dict) -> str | None:
        """
        Метод для получения даты конца поиска из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку с датой
        конца поиска или `None`.
        Метод получает значение ключа "date_to" из словаря с данными из формы.
        Затем метод вызывает функцию `check_date_to` модуля `utils` с передачей ему
        полученного значения и возвращает полученное значение.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с датой конца поиска или `None`.
        """
        date_to = form_data.get("date_to", None)
        date_to = utils.check_date_to(date_to)
        return date_to

    def get_salary_from(self, form_data: dict) -> int:
        """
        Метод для получения начальной суммы зарплаты из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает число
        или `None`.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с датой конца поиска или `None`.
        """
        salary_from = form_data.get("salary_from", None)
        if salary_from is not None:
            salary_from = int(salary_from) if int(salary_from) > 0 else None
        return salary_from

    def get_salary_to(self, form_data: dict) -> int:
        """
        Метод для получения конечной суммы зарплаты из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает число
        или `None`.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с датой конца поиска или `None`.
        """
        salary_to = form_data.get("salary_to", None)
        if salary_to is not None:
            salary_to = int(salary_to) if int(salary_to) != 300000 else None
        return salary_to

    def get_experience(self, form_data: dict) -> str | None:
        """
        Метод для получения опыта работы из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку с опытом
        работы или `None`.
        Метод получает значение ключа "experience" из словаря с данными из формы.
        Если значение равно списку с одним элементом "Не имеет значения", то метод
        возвращает `None`. В противном случае метод возвращает полученное значение.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с опытом работы или `None`.
        """
        experience = form_data.get("experience", None)
        if experience == ["Не имеет значения"]:
            experience = None
        return experience

    def get_remote(self, form_data: dict) -> bool | None:
        """
        Метод для получения флажка удаленной работы из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает булево значение
        флажка удаленной работы или `None`.
        Метод получает значение ключа "remote" из словаря с данными из формы.
        Если значение равно `None`, то метод возвращает `None`.
        В противном случае метод преобразует значение в булево и возвращает его.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            bool | None: Булево значение флажка удаленной работы или `None`.
        """
        remote = form_data.get("remote", None)
        return bool(remote) if remote else None

    def get_job_board(self, form_data: dict) -> str | None:
        """
        Метод для получения площадки для поиска из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку с
        площадкой для поиска или `None`.
        Метод получает значение ключа "job_board" из словаря с данными из формы.
        Если значение равно списку с одним элементом "Не имеет значения", то метод
        возвращает `None`. В противном случае метод возвращает полученное значение.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с площадкой для поиска или `None`.
        """
        job_board = form_data.get("job_board", None)
        if job_board == ["Не имеет значения"]:
            job_board = None
        return job_board

    def get_title_search(self, form_data: dict) -> bool | None:
        """
        Метод для получения флажка поиска в заголовках вакансий из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает булево значение
        флажка поиска в заголовках вакансий или `None`. Метод получает значение ключа
        "title_search" из словаря с данными из формы. Если значение равно `None`,
        то метод возвращает `None`. В противном случае метод преобразует значение
        в булево и возвращает его.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            bool | None: Булево значение флажка поиска в заголовках вакансий или `None`.
        """
        title_search = form_data.get("title_search", None)
        return bool(title_search) if title_search else None


class VacancyFetcher:
    """Класс для извлечения вакансий из базы данных.

    Этот класс предназначен для извлечения вакансий из базы данных с использованием
    различных условий фильтрации. Он содержит методы для фильтрации по названию,
    городу, дате и другим параметрам.
    """

    async def fetch(self, params: RequestParams) -> QuerySet:
        """Метод извлечения вакансий.

        Этот метод извлекает вакансии из базы данных с использованием
        условий фильтрации, указанных в параметрах запроса.

        Args:
            params (RequestParams): Объект параметров запроса.

        Returns:
            QuerySet: Набор результатов запроса, содержащий отфильтрованные вакансии.
        """
        q_objects = Q()
        vacancies = []
        if params.title:
            q_objects = await self.filter_by_title(q_objects, params)
            q_objects = await self.filter_by_city(q_objects, params)
            q_objects = await self.filter_by_date(q_objects, params)
            q_objects = await self.filter_by_salary(q_objects, params)
            q_objects = await self.filter_by_experience(q_objects, params)
            q_objects = await self.filter_by_job_board(q_objects, params)
            q_objects = await self.filter_by_remote(q_objects, params)
            vacancies = Vacancies.objects.filter(q_objects)
        return vacancies

    async def filter_by_title(self, q_objects: Q, params: RequestParams) -> Q:
        """Метод фильтрации по названию.

        Этот метод добавляет условия фильтрации по названию вакансии к объекту Q.

        Args:
            q_objects (Q): Объект Q, содержащий текущие условия фильтрации.
            params (RequestParams): Объект параметров запроса.

        Returns:
            Q: Обновленный объект Q с добавленными условиями фильтрации.
        """
        if params.title:
            if params.title_search:
                q_objects &= Q(title__icontains=params.title)
            else:
                q_objects &= Q(title__icontains=params.title) | Q(
                    description__icontains=params.title
                )
        return q_objects

    async def filter_by_city(self, q_objects: Q, params: RequestParams) -> Q:
        """Метод фильтрации по городу.

        Этот метод добавляет условия фильтрации по городу к объекту Q.

        Args:
            q_objects (Q): Объект Q, содержащий текущие условия фильтрации.
            params (RequestParams): Объект параметров запроса.

        Returns:
            Q: Обновленный объект Q с добавленными условиями фильтрации.
        """
        if params.city:
            q_objects &= Q(city__icontains=params.city)
        return q_objects

    async def filter_by_date(self, q_objects: Q, params: RequestParams) -> Q:
        """Метод фильтрации по дате.

        Этот метод добавляет условия фильтрации по дате публикации вакансии к объекту Q.

        Args:
            q_objects (Q): Объект Q, содержащий текущие условия фильтрации.
            params (RequestParams): Объект параметров запроса.

        Returns:
            Q: Обновленный объект Q с добавленными условиями фильтрации.
        """
        if params.date_from:
            q_objects &= Q(published_at__gte=params.date_from)

        if params.date_to:
            q_objects &= Q(published_at__lte=params.date_to)
        return q_objects

    async def filter_by_salary(self, q_objects: Q, params: RequestParams) -> Q:
        """Метод фильтрации по зарплате.

        Этот метод добавляет условия фильтрации по зарплате к объекту Q.

        Args:
            q_objects (Q): Объект Q, содержащий текущие условия фильтрации.
            params (RequestParams): Объект параметров запроса.

        Returns:
            Q: Обновленный объект Q с добавленными условиями фильтрации.
        """
        if params.salary_from and params.salary_to:
            q_objects &= Q(
                salary_from__gte=params.salary_from, salary_from__lte=params.salary_to
            ) & Q(salary_to__lte=params.salary_to, salary_to__gte=params.salary_from)
        elif params.salary_from and not params.salary_to:
            q_objects &= Q(salary_from__gte=params.salary_from)
        elif not params.salary_from and params.salary_to:
            q_objects &= Q(salary_to__lte=params.salary_to)
        return q_objects

    async def filter_by_experience(self, q_objects: Q, params: RequestParams) -> Q:
        """Метод фильтрации по опыту работы.

        Этот метод добавляет условия фильтрации по опыту работы к объекту Q.

        Args:
            q_objects (Q): Объект Q, содержащий текущие условия фильтрации.
            params (RequestParams): Объект параметров запроса.

        Returns:
            Q: Обновленный объект Q с добавленными условиями фильтрации.
        """
        if params.experience and params.experience[0] != "Не имеет значения":
            q_objects &= Q(experience__in=params.experience)
        return q_objects

    async def filter_by_job_board(self, q_objects: Q, params: RequestParams) -> Q:
        """Метод фильтрации по площадке поиска вакансий.

        Этот метод добавляет условия фильтрации по площадке поиска вакансий
        к объекту Q.

        Args:
            q_objects (Q): Объект Q, содержащий текущие условия фильтрации.
            params (RequestParams): Объект параметров запроса.

        Returns:
            Q: Обновленный объект Q с добавленными условиями фильтрации.
        """
        if params.job_board and params.job_board[0] != "Не имеет значения":
            q_objects &= Q(job_board__in=params.job_board)
        return q_objects

    async def filter_by_remote(self, q_objects: Q, params: RequestParams) -> Q:
        """Метод фильтрации по удаленной работе.

        Этот метод добавляет условия фильтрации по удаленной работе к объекту Q.

        Args:
            q_objects (Q): Объект Q, содержащий текущие условия фильтрации.
            params (RequestParams): Объект параметров запроса.

        Returns:
            Q: Обновленный объект Q с добавленными условиями фильтрации.
        """
        if params.remote:
            q_objects &= Q(remote=True)
        return q_objects


class AsyncLoginRequiredMixin(AccessMixin):
    """
    Асинхронная версия миксина LoginRequiredMixin Django.

    Этот миксин предназначен для использования в представлениях, доступ к которым
    должен быть разрешен только для аутентифицированных пользователей.
    Если пользователь не аутентифицирован, он будет перенаправлен на страницу входа.

    Наследуется от класса AccessMixin.
    """

    async def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Awaitable[HttpResponse]:
        """Асинхронный метод dispatch для обработки запросов.

        В этом методе выполняется проверка аутентификации пользователя.
        Если пользователь не аутентифицирован, вызывается метод handle_no_permission,
        который возвращает объект HttpResponseRedirect для перенаправления пользователя
        на страницу входа.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            Awaitable[HttpResponse]: Объект ответа.
        """
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return await super().dispatch(request, *args, **kwargs)


class VacanciesMixin:
    """
    Класс-примесь для работы с вакансиями.

    Класс содержит методы для получения списка вакансий, проверки черного и скрытого
    списков и другие вспомогательные методы.
    """

    @property
    def fetcher(self) -> VacancyFetcher:
        """
        Это свойство возвращает объект VacancyFetcher.

        Returns:
            VacancyFetcher: Объект VacancyFetcher.
        """
        return VacancyFetcher()

    @property
    def parser(self) -> FormDataParser:
        """
        Это свойство возвращает объект FormDataParser.

        Returns:
            FormDataParser: Объект FormDataParser.
        """
        return FormDataParser()

    async def get_vacancies(self, form: SearchingForm) -> QuerySet:
        """
        Метод для получения списка вакансий.

        Метод принимает на вход словарь с данными из формы и возвращает объект
        класса `QuerySet` с вакансиями.
        Метод вызывает метод `get_request_params`
        с передачей ему словаря с данными из формы и получает объект класса
        `RequestParams` с параметрами запроса. Затем метод вызывает метод `fetch`
        с передачей ему объекта `RequestParams` и возвращает полученный объект
        класса `QuerySet`.

        Args:
            form (dict): Словарь с данными из формы.

        Returns:
            QuerySet: Объект класса `QuerySet` с вакансиями.
        """
        form_data = self.parser.get_form_data(form)
        params = self.parser.get_request_params(form_data)
        vacancies = await self.fetcher.fetch(params)
        return vacancies

    def check_vacancies(
        self, vacancies: QuerySet, request: HttpRequest
    ) -> tuple[QuerySet, QuerySet]:
        """
        Метод для проверки вакансий на соответствие черному и скрытому спискам.

        Метод принимает на вход объекты класса `QuerySet` с вакансиями и объект
        класса `HttpRequest` с запросом. Метод проверяет, является ли пользователь
        анонимным. Если пользователь анонимный, то метод возвращает список вакансий
        без изменений и пустой список избранных вакансий.

        Если пользователь не анонимный, то метод получает список пользовательских
        вакансий и вызывает методы `get_blacklist_urls`, `get_favourite_urls` и
        `get_hidden_companies` для получения соответствующих списков URL-адресов и
        компаний. Затем метод вызывает методы `get_filtered_vacancies` и
        `get_favourite_vacancies` для получения соответствующих списков вакансий.
        Возвращает кортеж из двух списков: отфильтрованных вакансий и избранных
        вакансий.

        Args:
            vacancies (QuerySet): Объект класса `QuerySet` с вакансиями.
            request (HttpRequest): Объект класса `HttpRequest` с запросом.

        Returns:
            tuple[QuerySet, QuerySet]: Кортеж из двух списков: отфильтрованных
            вакансий и избранных вакансий.
        """
        try:
            user = request.user
            if user.is_anonymous:
                return vacancies, []

            user_vacancies = UserVacancies.objects.filter(user=user)

            blacklist_urls = self.get_blacklist_urls(vacancies, user_vacancies)
            favourite_urls = self.get_favourite_urls(vacancies, user_vacancies)
            hidden_companies = self.get_hidden_companies(vacancies, user_vacancies)

            filtered_vacancies = self.get_filtered_vacancies(
                vacancies, blacklist_urls, hidden_companies
            )
            favourite_vacancies = self.get_favourite_vacancies(
                vacancies, favourite_urls, hidden_companies
            )

        except Exception as exc:
            logger.exception(exc)
            filtered_vacancies = vacancies
            favourite_vacancies = []

        return filtered_vacancies, favourite_vacancies

    def get_blacklist_urls(self, vacancies: QuerySet, user_vacancies: QuerySet) -> set:
        """
        Метод для получения списка URL-адресов вакансий из черного списка.

        Метод принимает на вход объекты класса `QuerySet` с вакансиями и
        пользовательскими вакансиями и возвращает множество URL-адресов вакансий,
        которые находятся в черном списке пользователя.

        Args:
            vacancies (QuerySet): Объект класса `QuerySet` с вакансиями.
            user_vacancies (QuerySet): Объект класса `QuerySet` с пользовательскими
            вакансиями.

        Returns:
            set: Множество URL-адресов вакансий из черного списка.
        """
        blacklist_urls = set(
            user_vacancy.url
            for user_vacancy in user_vacancies
            if user_vacancy.is_blacklist
        )
        return blacklist_urls.intersection(vacancy.url for vacancy in vacancies)

    def get_favourite_urls(self, vacancies: QuerySet, user_vacancies: QuerySet) -> set:
        """
        Метод для получения списка URL-адресов избранных вакансий.

        Метод принимает на вход объекты класса `QuerySet` с вакансиями и
        пользовательскими вакансиями и возвращает множество URL-адресов избранных
        вакансий пользователя.

        Args:
            vacancies (QuerySet): Объект класса `QuerySet` с вакансиями.
            user_vacancies (QuerySet): Объект класса `QuerySet` с пользовательскими
            вакансиями.

        Returns:
            set: Множество URL-адресов избранных вакансий.
        """
        favourite_urls = set(
            user_vacancy.url
            for user_vacancy in user_vacancies
            if user_vacancy.is_favourite and not user_vacancy.is_blacklist
        )
        return favourite_urls.intersection(vacancy.url for vacancy in vacancies)

    def get_hidden_companies(
        self, vacancies: QuerySet, user_vacancies: QuerySet
    ) -> set:
        """
        Метод для получения списка скрытых компаний.

        Метод принимает на вход объекты класса `QuerySet` с вакансиями и
        пользовательскими вакансиями и возвращает множество названий компаний,
        которые пользователь скрыл.

        Args:
            vacancies (QuerySet): Объект класса `QuerySet` с вакансиями.
            user_vacancies (QuerySet): Объект класса `QuerySet` с пользовательскими
            вакансиями.

        Returns:
            set: Множество названий скрытых компаний.
        """
        hidden_companies = set()
        for vacancy in vacancies:
            for user_vacancy in user_vacancies:
                if vacancy.company == user_vacancy.hidden_company:
                    hidden_companies.add(user_vacancy.hidden_company)
        return hidden_companies

    def get_filtered_vacancies(
        self, vacancies: QuerySet, blacklist_urls: set, hidden_companies: set
    ) -> list:
        """
        Метод для получения множества отфильтрованных вакансий.

        Метод принимает на вход объект класса `QuerySet` с вакансиями,
        множество URL-адресов из черного списка и множество названий скрытых компаний.
        Метод фильтрует список вакансий и удаляет из него те, которые находятся
        в черном списке или принадлежат скрытым компаниям. Возвращает список
        отфильтрованных вакансий.

        Args:
            vacancies (QuerySet): Объект класса `QuerySet` с вакансиями.
            blacklist_urls (set): Множество URL-адресов из черного списка.
            hidden_companies (set): Множество названий скрытых компаний.

        Returns:
            list: Список отфильтрованных вакансий.
        """
        filtered_vacancies = [
            vacancy
            for vacancy in vacancies
            if vacancy.url not in blacklist_urls
            and vacancy.company not in hidden_companies
        ]
        return filtered_vacancies

    def get_favourite_vacancies(
        self, vacancies: QuerySet, favourite_urls: set, hidden_companies: set
    ) -> list:
        """
        Метод для получения множества избранных вакансий.

        Метод принимает на вход объект класса `QuerySet` с вакансиями,
        множество URL-адресов избранных вакансий и множество названий скрытых компаний.
        Метод фильтрует список вакансий и оставляет в нем только те, которые находятся
        в списке избранных и не принадлежат скрытым компаниям. Возвращает список
        избранных вакансий.

        Args:
            vacancies (QuerySet): Объект класса `QuerySet` с вакансиями.
            favourite_urls (set): Множество URL-адресов избранных вакансий.
            hidden_companies (set): Множество названий скрытых компаний.

        Returns:
            list: Список избранных вакансий.
        """
        favourite_vacancies = [
            vacancy
            for vacancy in vacancies
            if vacancy.url in favourite_urls and vacancy.company not in hidden_companies
        ]
        return favourite_vacancies
