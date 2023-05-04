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

-   **Клонируйте репозиторий в свою рабочую папку:**<br>
    ```rs
    git clone https://github.com/NikSan3452/job-parser.git
    ```<br>

-   **Перейдите в папку проекта:**<br>
    `cd job-parser`<br>

-   **Создайте новое виртуальное окружение:**<br>
    `python -m vevn venv` - для Windows<br>
    `python3 -m venv venv` - для Linux<br>

-   **Активируйте виртуальное окружение:**<br>
    `venv\Scripts\activate.bat` - для Windows<br>
    `source venv/bin/activate` - для Linux<br>

-   **Установите необходимые библиотеки:**<br>
    `cd job_parser`<br>
    `pip install -r requirements.txt`<br>

-   **Создайте файл .env в текущей директории (job_parser) и укажите в нем следующие параметры:**<br>

    _Django_<br>
    `SECRET_KEY=1234Qwerty` - Ваш секретный ключ для приложения Django<br>
    `DEBUG=1` - если нужен режим дебага, 0 - в противном случае<br>
    `DJANGO_ALLOWED_HOSTS="*"` - Разрешенные хосты, можно оставить по умолчанию<br>
    `CSRF_TRUSTED_ORIGINS="http://127.0.0.1:1337"` - Укажите список хостов, которые являются доверенными источниками для небезопасных запросов<br>
    _Postgres_<br>
    `POSTGRES_USER=postgresql` - Пользователь postgres<br>
    `POSTGRES_PASSWORD= 1234Qwerty` - Пароль<br>
    `POSTGRES_SERVER=localhost` - Адрес сервера<br>
    `POSTGRES_PORT=5432` - Порт<br>
    `POSTGRES_DB=postgres` - Имя базы<br>
    `ENGINE="django.db.backends.postgresql"` (Настройка для Django, указывающая, какая именно база используется, если оставить по умолчанию, то нужно настроить и запустить postgresql на хосте, иначе можно закомментировать эту строку и тогда создастся база sqlite3)<br>

    _Redis Cache_<br>
    `REDIS_HOST=localhost` - Адрес сервера<br>
    `REDIS_PORT=6379` - Порт<br>

    _Huey_<br>
    `GEEKJOB_PAGES_COUNT=5` - Количество страниц, которые будет парсить парсер GeekJob начиная с первой<br>
    `HABR_PAGES_COUNT=10` - Количество страниц, которые будет парсить парсер Habr career начиная с первой<br>
    `DOWNLOAD_DELAY=5` - Интервал в секундах между запросами на загрузку страницы<br>
    `SCRAPING_SCHEDULE_MINUTES=200` - Интервал между запусками парсера в минутах. В данном случае, парсер будет запускаться каждые 200 минут<br>

    `SENDING_EMAILS_HOURS=6` - Интервал между рассылкой писем в часах<br>

    `DELETE_OLD_VACANCIES_HOURS=6` - Интервал между удалением устаревших вакансий из базы данных<br>

    _parser Superjob_<br>
    `SUPERJOB_SECRET_KEY1=v3.qw1e2r3ty`Секретный ключ для приложения SuperJob. Создается в личном кабинете на сайте Superjob. Чем больше приложений, тем проще обойти ограничения на количество запросов в минуту<br>
    `SUPERJOB_SECRET_KEY2`=Тоже что и выше (Можно не создавать, достаточно первого)<br>
    `SUPERJOB_SECRET_KEY3`=Тоже что и выше (Можно не создавать, достаточно первого)<br>

    _Email_<br>
    `EMAIL_HOST=smtp.example.ru` - Хост<br>
    `EMAIL_HOST_USER=example.example@mail.ru` - Ваш электронный адрес<br>
    `EMAIL_HOST_PASSWORD=1234Qwerty` - Пароль.<br>

-   **Запустите миграции:**<br>
    `python manage.py migrate` - для Windows<br>
    `python3 manage.py migrate` - для Linux<br>
    `django m` - Либо можно использовать сокращения<br>

-   **Запустите сбор статики:**<br>
    `python mange.py collectstatic --noinput` - для Windows<br>
    `python3 mange.py collectstatic --noinput` - для Linux<br>
    `django с` - Либо можно использовать сокращения<br>

-   **Запустите скрипт insert_data.py для заполнения базы данных городами:**<br>
    `python insert_data.py` - для Windows<br>
    `python3 insert_data.py` - для Linux<br>

-   **Запустите приложение Django:**<br>
    `python manage.py runserver` - для Windows<br>
    `python3 manage.py runserver` - для Linux<br>
    `django r` - Либо можно использовать сокращения<br>
-   **В браузере перейдите по адресу `http://127.0.0.1:8000`**
    <br>

    #### Docker

      <br>

-   **Создайте файл `.env.prod`**.<br>

-   **Скопируйте содержимое файла `.env` в `.env.prod`.**<br>

-   **Измените следующие параметры в `.env.prod`:**<br>

    `POSTGRES_SERVER=172.16.238.12`<br>
    `REDIS_HOST=172.16.238.11`<br>

-   **В корневой папке job-parser запустите команду:**<br>
    `docker compose up --build`<br>

-   **В браузере перейдите по адресу `http://127.0.0.1:1337`**<br>

### Запуск скрапера с помощью Huey

-   **В папке job_parser запустите команду:**<br>
    `python manage.py run_huey` - Для Windows<br>
    `python3 manage.py run_huey` - Для Linux<br>
    `django run_huey` - Либо можно использовать сокращения<br>
    Эта команда запустит переодические задачи для скрапинга вакансий, а также рассылку писем и удаление устаревших вакансий из базы данных.
    Варианты запуска Huey с дополнительными опциями смотрите в [документации](https://huey.readthedocs.io/en/latest/django.html).