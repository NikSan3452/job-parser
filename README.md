# job-parser
Сайт - агрегатор вакансий с различных площадок по поиску работы. На данный момент собирает данные с 3-х популярных сайтов: [Headhunter](https://hh.ru/), [SuperJob](https://superjob.ru) и [Zarplata](https://zarplata.ru).
Написан при помощи: Django, PostgreSQL, Redis, Docker, Celery, Bootstrap
### Особенности:

- Парсер асинхронный
- Аутентификация пользователей через Django-allauth
- Подписка на рассылку вакансий
- Работает с официальными API
- Возможность добавить вакансию в избранное
- Возможность добавить вакансию в черный список
- Фильтр по критериям
- Можно запустить с помощью Docker  

Главная страница

![home.png](/screenshots/home.png)

Список вакансий

![list.png](/screenshots/list.png)

Профиль

![profile.png](/screenshots/profile.png)
