import pytest
from parser.forms import SearchingForm


class TestProfileForm:
    @pytest.mark.parametrize(
        "job, city, subscribe, validity",
        [
            ("Python", "Москва", False, True),
            ("Python", "Москва", True, True),
        ],
    )
    def test_valid_searching_form(
        self,
        job: str,
        city: str,
        subscribe: str,
        validity: bool,
    ) -> None:
        form = SearchingForm(
            data={
                "job": job,
                "city": city,
                "subscribe": subscribe,
            }
        )

        assert form.is_valid() is validity
