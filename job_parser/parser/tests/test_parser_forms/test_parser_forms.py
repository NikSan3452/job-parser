from parser.forms import SearchingForm

import pytest


class TestSearchingForm:
    case_1 = (
        "Python",
        "Москва",
        "2023-01-01",
        "2023-02-02",
        "0",
        False,
        False,
        "Не имеет значения",
        True,
    )
    case_2 = (
        "Python",
        "Москва",
        "2023-01-01",
        "2023-02-02",
        "1",
        True,
        True,
        "HeadHunter",
        True,
    )
    case_3 = (
        "Python",
        None,
        "2023-01-01",
        "2023-02-02",
        "2",
        False,
        False,
        "SuperJob",
        True,
    )
    case_4 = ("Python", None, None, None, "3", False, False, "Zarplata", True)
    case_5 = (None, None, None, None, "4", False, False, "Zarplata", False)

    @pytest.mark.parametrize(
        "job, city, date_from, date_to, experience, title_search, remote, job_board, validity",
        [case_1, case_2, case_3, case_4, case_5],
    )
    def test_valid_searching_form(
        self,
        job: str,
        city: str | None,
        date_from: str | None,
        date_to: str | None,
        experience: str | None,
        title_search: str | None,
        remote: str | None,
        job_board: str | None,
        validity: bool | None,
    ) -> None:
        form = SearchingForm(
            data={
                "job": job,
                "city": city,
                "date_from": date_from,
                "date_to": date_to,
                "experience": experience,
                "title_search": title_search,
                "remote": remote,
                "job_board": job_board,
            }
        )

        assert form.is_valid() is validity
        assert form.is_valid() is validity
