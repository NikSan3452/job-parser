# job-parser
Сайт - агрегатор вакансий с различных площадок по поиску работы. На данный момент собирает данные с 6-х популярных сайтов: [Headhunter](https://hh.ru/), [SuperJob](https://superjob.ru), [Zarplata](https://zarplata.ru), [Trudvsem](https://trudvsem.ru/), [HabrCareer](https://career.habr.com/), [Geekjob](https://geekjob.ru/).

Написан при помощи: Django, PostgreSQL, Redis, Docker, Huey, Bootstrap
### Особенности:

- Парсер асинхронный
- Аутентификация пользователей через Django-allauth
- Фильтр по различным критериям
- Подписка на рассылку вакансий
- Работает, как с официальными API, так и парсит те площадки, где нет возможности взаимодействия с API
- Возможность добавить вакансию в избранное
- Возможность добавить вакансию в черный список
- Возможность скрыть вакансии компании
- Можно запустить с помощью Docker  

### Демонстрация:

**Поиск**
![home.png](/screenshots/searching.gif)

**Манипуляции с поисковой выдачей**

![list.png](/screenshots/list.gif)

