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
    ```

-   **Перейдите в папку проекта:**<br>

    ```rs
    cd job-parser
    ```

-   **Создайте новое виртуальное окружение:**<br>
    Для Windows:

    ```rs
    python -m vevn venv
    ```

    Для Linux:

    ```rs
    python3 -m venv venv
    ```

-   **Активируйте виртуальное окружение:**<br>
    Для Windows:

    ```rs
    venv\Scripts\activate.bat
    ```

    Для Linux:

    ```rs
    source venv/bin/activate
    ```

-   **Установите необходимые библиотеки:**<br>

    ```rs
    cd job_parser
    ```

    ```rs
    pip install -r requirements.txt
    ```

-   **Создайте файл .env в текущей директории (job_parser) и укажите в нем следующие параметры:**<br>

    _Django_<br>

    ```rs
    SECRET_KEY=1234Qwerty                        # Ваш секретный ключ для приложения Django<br>
    DEBUG=1                                      # 1 если нужен режим дебага, 0 - в противном случае<br>
    DJANGO_ALLOWED_HOSTS="*"                     # Разрешенные хосты, можно оставить по умолчанию<br>
    CSRF_TRUSTED_ORIGINS="http://127.0.0.1:1337" # Укажите список хостов, которые являются доверенными источниками для небезопасных запросов.


    _Postgres_

    POSTGRES_USER=postgresql                     # Пользователь postgres
    POSTGRES_PASSWORD= 1234Qwerty                # Пароль
    POSTGRES_SERVER=localhost                    # Адрес сервера
    POSTGRES_PORT=5432                           # Порт
    POSTGRES_DB=postgres`                        # Имя базы
    ENGINE="django.db.backends.postgresql"`      # Настройка для Django, указывающая, какая именно база используется, 
                                                 # если оставить по умолчанию, то нужно настроить и запустить postgresql
                                                 # на хосте, иначе можно закомментировать эту строку и тогда создастся 
                                                 # база sqlite3

    _Redis Cache_

    REDIS_HOST=localhost                         # Адрес сервера
    REDIS_PORT=6379                              # Порт

    _Huey_

    GEEKJOB_PAGES_COUNT=5                        # Количество страниц, которые будет парсить парсер GeekJob начиная с первой
    HABR_PAGES_COUNT=10                          # Количество страниц, которые будет парсить парсер Habr career начиная с первой
    DOWNLOAD_DELAY=5                             # Интервал в секундах между запросами на загрузку страницы
    SCRAPING_SCHEDULE_MINUTES=200                # Интервал между запусками парсера в минутах. В данном случае, 
                                                 # парсер будет запускаться каждые 200 минут

    SENDING_EMAILS_HOURS=6                       # Интервал между рассылкой писем в часах

    DELETE_OLD_VACANCIES_HOURS=6                 # Интервал между удалением устаревших вакансий из базы данных

    _parser Superjob_

    SUPERJOB_SECRET_KEY1=v3.qw1e2r3ty            # Секретный ключ для приложения SuperJob. 
                                                 # Создается в личном кабинете на сайте Superjob. Чем больше приложений, 
                                                 # тем проще обойти ограничения на количество запросов в минуту
    SUPERJOB_SECRET_KEY2=v3.qw1e2r3ty            # Тоже что и выше (Можно не создавать, достаточно первого)
    SUPERJOB_SECRET_KEY3=v3.qw1e2r3ty            # Тоже что и выше (Можно не создавать, достаточно первого)

    _Email_

    EMAIL_HOST=smtp.example.ru                   # Сервер исходящей почты
    EMAIL_HOST_USER=example.example@mail.ru      # Ваш адрес электронной почты
    EMAIL_HOST_PASSWORD=1234Qwerty               # Пароль электронной почты
    EMAIL_PORT=2525                              # Порт
    EMAIL_USE_TLS=True                           # Использовать TLS шифрование
    EMAIL_USE_SSL=False                          # Использовать SSL шифрование                              
    ```

-   **Запустите миграции:**<br>
    Для Windows:

    ```rs
    python manage.py migrate
    ```

    Для Linux:

    ```rs
    python3 manage.py migrate
    ```

    Либо можно использовать сокращения:

    ```rs
    django m
    ```

-   **Запустите сбор статики:**<br>
    Для Windows:

    ```rs
    python mange.py collectstatic --noinput
    ```

    Для Linux:

    ```rs
    python3 mange.py collectstatic --noinput
    ```

    Либо можно использовать сокращения:

    ```rs
    django с
    ```

-   **Запустите скрипт insert_data.py для заполнения базы данных городами:**<br>
    Для Windows:

    ```rs
    python insert_data.py
    ```

    Для Linux:

    ```rs
    python3 insert_data.py
    ```

-   **Запустите приложение Django:**<br>
    Для Windows:
    ```rs
    python manage.py runserver
    ```
    Для Linux:
    ```rs
    python3 manage.py runserver
    ```
    Либо можно использовать сокращения:
    ```rs
    django r
    ```
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

    ```rs
    docker compose up --build
    ```

-   **В браузере перейдите по адресу `http://127.0.0.1:1337`**<br>

### Запуск скрапера с помощью Huey

-   **В папке job_parser запустите команду:**<br>
    Для Windows:
    ```rs
    python manage.py run_huey
    ```
    Для Linux:
    ```rs
    python3 manage.py run_huey
    ```
    Либо можно использовать сокращения:
    ```rs
    django run_huey
    ```
    Эта команда запустит переодические задачи для скрапинга вакансий, а также рассылку писем и удаление устаревших вакансий из базы данных.
    Варианты запуска Huey с дополнительными опциями смотрите в [документации](https://huey.readthedocs.io/en/latest/django.html).
