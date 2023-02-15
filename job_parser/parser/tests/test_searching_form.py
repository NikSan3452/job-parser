import pytest
from parser.forms import SearchingForm


class TestSearchingForm:
    @pytest.mark.parametrize(
        "job, city, date_from, date_to, experience, title_search, remote, validity",
        [
            ("Python", "Москва", "2023-01-01", "2023-02-02", "0", False, False, True),
            ("Python", "Москва", "2023-01-01", "2023-02-02", "1", True, True, True),
        ],
    )
    def test_valid_searching_form(
        self,
        job: str,
        city: str,
        date_from: str,
        date_to: str,
        experience: str,
        title_search: str,
        remote: str,
        validity: bool,
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
            }
        )

        assert form.is_valid() is validity
