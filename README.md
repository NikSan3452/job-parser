# job-parser

Сайт - агрегатор вакансий с различных площадок по поиску работы. На данный момент собирает данные с 6-х популярных сайтов: [Headhunter](https://hh.ru/), [SuperJob](https://superjob.ru), [Zarplata](https://zarplata.ru), [Trudvsem](https://trudvsem.ru/), [HabrCareer](https://career.habr.com/), [Geekjob](https://geekjob.ru/).

Написан с использованием: Django, PostgreSQL, Redis, Docker, Huey, Bootstrap

### Особенности:

-   Асинхронный парсер
-   Аутентификация пользователей через Django-allauth
-   Фильтр по различным критериям
-   Подписка на рассылку вакансий
-   Работает, как с официальными API, так и парсит те площадки, где нет возможности взаимодействия с API
-   Возможность добавить вакансию в избранное
-   Возможность добавить вакансию в черный список
-   Возможность скрыть вакансии компании
-   Можно запустить с помощью Docker

### Демонстрация:

**Поиск**
![home.png](/screenshots/searching.gif)

**Манипуляции с поисковой выдачей**

![list.png](/screenshots/list.gif)

### Установка:

-   **Клонируйте репозиторий в свою рабочую папку:**
    `git clone https://github.com/NikSan3452/job-parser.git`<br>

-   **Перейдите в папку проекта:**
    `cd job-parser`<br>

-   **Создайте новое виртуальное окружение:**
    `python -m vevn venv` - для Windows
    `python3 -m venv venv` - для Linux<br>

-   **Активируйте виртуальное окружение:**
    `venv\Scripts\activate.bat` - для Windows
    `source venv/bin/activate` - для Linux<br>

-   **Установите необходимые библиотеки:**
    `cd job_parser`
    `pip install -r requirements.txt`<br>

-   **Создайте файл .env в текущей директории (job_parser) и укажите в нем следующие параметры:**

    _Django_
    `SECRET_KEY=1234Qwerty` - Ваш секретный ключ для приложения Django
    `DEBUG=1` - если нужен режим дебага, 0 - в противном случае
    `DJANGO_ALLOWED_HOSTS="*"` - Разрешенные хосты, можно оставить по умолчанию
    `CSRF_TRUSTED_ORIGINS="http://127.0.0.1:1337"` - Укажите список хостов, которые являются доверенными источниками для небезопасных запросов
    _Postgres_
    `POSTGRES_USER=postgresql` - Пользователь postgres
    `POSTGRES_PASSWORD= 1234Qwerty` - Пароль
    `POSTGRES_SERVER=localhost` - Адрес сервера
    `POSTGRES_PORT=5432` - Порт
    `POSTGRES_DB=postgres` - Имя базы
    `ENGINE="django.db.backends.postgresql"` (Настройка для Django, указывающая, какая именно база используется, если оставить по умолчанию, то нужно настроить и запустить postgresql на хосте, иначе можно закомментировать эту строку и тогда создастся база sqlite3)

    _Redis Cache_
    `REDIS_HOST=localhost` - Адрес сервера
    `REDIS_PORT=6379` - Порт

    _Huey_
    `GEEKJOB_PAGES_COUNT=5` - Количество страниц, которые будет парсить парсер GeekJob начиная с первой
    `HABR_PAGES_COUNT=10` - Количество страниц, которые будет парсить парсер Habr career начиная с первой
    `DOWNLOAD_DELAY=5` - Интервал в секундах между запросами на загрузку страницы
    `SCRAPING_SCHEDULE_MINUTES=200` - Интервал между запусками парсера в минутах. В данном случае, парсер будет запускаться каждые 200 минут

    `SENDING_EMAILS_HOURS=6` - Интервал между рассылкой писем в часах

    `DELETE_OLD_VACANCIES_HOURS=6` - Интервал между удалением устаревших вакансий из базы данных

    _parser Superjob_
    `SUPERJOB_SECRET_KEY1=v3.qw1e2r3ty`Секретный ключ для приложения SuperJob. Создается в личном кабинете на сайте Superjob. Чем больше приложений, тем проще обойти ограничения на количество запросов в минуту.
    `SUPERJOB_SECRET_KEY2`=Тоже что и выше (Можно не создавать, достаточно первого).
    `SUPERJOB_SECRET_KEY3`=Тоже что и выше (Можно не создавать, достаточно первого).

    _Email_
    `EMAIL_HOST=smtp.example.ru` - Хост
    `EMAIL_HOST_USER=example.example@mail.ru` - Ваш электронный адрес.
    `EMAIL_HOST_PASSWORD=1234Qwerty` - Пароль.<br>

-   **Запустите миграции:**
    `python manage.py migrate` - для Windows
    `python3 manage.py migrate` - для Linux
    `django m` - либо можно использовать сокращения<br>

-   **Запустите сбор статики:**
    `python mange.py collectstatic --noinput` - для Windows
    `python3 mange.py collectstatic --noinput` - для Linux
    `django с` - либо можно использовать сокращения<br>

-   **Запустите скрипт insert_data.py для заполнения базы данных городами:**
    `python insert_data.py` - для Windows
    `python3 insert_data.py` - для Linux<br>

-   **Запустите приложение Django:**
    `python manage.py runserver` - для Windows
    `python3 manage.py runserver` - для Linux
    `django r` - либо можно использовать сокращения<br>
