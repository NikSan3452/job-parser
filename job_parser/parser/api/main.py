import asyncio
import datetime

from parser.api.config import RequestConfig
from parser.api.parsers import Headhunter, SuperJob, Zarplata, Trudvsem
from parser.api.utils import Utils
from parser.api.base_parser import Parser


utils = Utils()


async def run(
    form_params: dict = {},
) -> list[dict]:
    """Отвечает за запуск парсера.

    Args:
        form_params (dict) Словарь с параметрами поиска.
    Returns:
        list[dict]: Список словарей с вакансиями.
    """
    city: str | None = form_params.get("city")
    city_from_db: int | None = form_params.get("city_from_db")
    job: str = form_params.get("job", "Python")
    date_to: str | datetime.date | None = form_params.get("date_to")
    date_from: str | datetime.date | None = form_params.get("date_from")
    title_search: bool = form_params.get("title_search", False)
    experience: int = form_params.get("experience", 0)
    remote: bool = form_params.get("remote", False)
    job_board: str = form_params.get("job_board", "Не имеет значения")

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
    tv = Trudvsem(params)

    # Очищаем список вакансий
    Parser.general_job_list.clear()

    if job_board != "Не имеет значения":
        # Поиск только по определенной площадке
        match job_board:
            case "HeadHunter":
                await hh.get_vacancy_from_headhunter()
            case "SuperJob":
                await sj.get_vacancy_from_superjob()
            case "Zarplata":
                await zp.get_vacancy_from_zarplata()
            case "Trudvsem":
                await tv.get_vacancy_from_trudvsem()
    else:
        # Оборачиваем сопрограммы в задачи
        task1 = asyncio.create_task(hh.get_vacancy_from_headhunter())
        task2 = asyncio.create_task(sj.get_vacancy_from_superjob())
        task3 = asyncio.create_task(zp.get_vacancy_from_zarplata())
        task4 = asyncio.create_task(tv.get_vacancy_from_trudvsem())

        # Запускаем задачи
        await asyncio.gather(task1, task2, task3, task4)

    # Сортируем получемнный список вакансий
    sorted_job_list = await utils.sort_by_date(Parser.general_job_list)
    if title_search:
        sorted_job_list = await utils.sort_by_title(sorted_job_list, job)
    if remote:
        sorted_job_list = await utils.sort_by_remote_work(remote, sorted_job_list)
    if remote and title_search:
        sorted_job_list_title = await utils.sort_by_title(sorted_job_list, job)
        sorted_job_list = await utils.sort_by_remote_work(
            remote, sorted_job_list_title
        )

    print(f"Количество вакансий: {len(sorted_job_list)}")
    return sorted_job_list


if __name__ == "__main__":
    asyncio.run(run())
