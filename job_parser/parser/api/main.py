import asyncio
import datetime
from typing import Optional

from parser.api.config import RequestConfig
from parser.api.parsers import Headhunter, SuperJob, Zarplata
from parser.api.utils import Utils
from parser.api.base_parser import Parser


utils = Utils()


async def run(
    city: Optional[str] = None,
    city_from_db: Optional[int] = None,
    job: Optional[str] = "Python",
    date_to: Optional[str | datetime.date] = None,
    date_from: Optional[str | datetime.date] = None,
    title_search: Optional[bool] = False,
    experience: int = 0,
    remote: Optional[bool] = False,
    job_board: Optional[str] = "Не имеет значения"
) -> list[dict]:
    """Отвечает за запуск парсера.

    Args:
        city (Optional[str], optional): Город. По умолчанию "Москва".
        city_from_db (Optional[int], optional): Код города из базы данных.
        Необходим для поиска в API HeadHUnter. По-умолчанию 1.
        job (Optional[str], optional): Специальность. По-умолчанию "Python".
        date_to (Optional[datetime.date], optional): Дата до. По-умолчанию сегодня.
        date_from (Optional[datetime.date], optional): Дата от.
        По-умолчанию высчитывается по формуле: 'Сегодня - 10 дней'.
        title_search (Optional[bool]): Если True, то поиск идет по заголовкам вакансий.
        experience (int): Опыт работы. По-умолчанию False.
        remote (Optional[bool]): Если True, то поиск идет по удаленной работе.
    Returns:
        list[dict]: Список словарей с вакансиями.
    """

    params = RequestConfig(
        city=city,
        city_from_db=city_from_db,
        job=job,
        date_from=date_from,
        date_to=date_to,
        experience=experience,
    )

    hh = Headhunter(params)
    sj = SuperJob(params)
    zp = Zarplata(params)

    # Очищаем список вакансий
    Parser.general_job_list.clear()

    # Оборачиваем сопрограммы в задачи
    task1 = asyncio.create_task(hh.get_vacancy_from_headhunter())
    task2 = asyncio.create_task(sj.get_vacancy_from_superjob())
    task3 = asyncio.create_task(zp.get_vacancy_from_zarplata())

    # Запускаем задачи
    await asyncio.gather(task1, task2, task3)

    # Сортируем получемнный список вакансий
    sorted_job_list = utils.sort_by_date(Parser.general_job_list, "published_at")
    if job_board != "Не имеет значения":
        sorted_job_list = utils.sorted_by_job_board(job_board, sorted_job_list)
    if title_search:
        sorted_job_list = utils.sort_by_title(sorted_job_list, job)
    if remote:
        sorted_job_list = utils.sorted_by_remote_work(remote, sorted_job_list)
    if remote and title_search:
        sorted_job_list_title = utils.sort_by_title(sorted_job_list, job)
        sorted_job_list = utils.sorted_by_remote_work(remote, sorted_job_list_title)

    # print(f"Количество вакансий: {len(sorted_job_list)}", sorted_job_list)
    return sorted_job_list


if __name__ == "__main__":
    asyncio.run(run())
