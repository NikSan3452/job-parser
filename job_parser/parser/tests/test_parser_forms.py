import pytest
from parser.forms import SearchingForm


class TestSearchingForm:
    @pytest.mark.parametrize(
        "job, city, date_from, date_to, experience, title_search, remote, job_board, validity",
        [
            (
                "Python",
                "Москва",
                "2023-01-01",
                "2023-02-02",
                "0",
                False,
                False,
                "Не имеет значения",
                True,
            ),
            (
                "Python",
                "Москва",
                "2023-01-01",
                "2023-02-02",
                "1",
                True,
                True,
                "HeadHunter",
                True,
            ),
            (
                "Python",
                None,
                "2023-01-01",
                "2023-02-02",
                "2",
                False,
                False,
                "SuperJob",
                True,
            ),
            ("Python", None, None, None, "1", False, False, "Zarplata", True),
        ],
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
