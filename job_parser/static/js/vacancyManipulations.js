function addToFavourite(index, vacancyUrl, vacancyTitle) {
    let checkbox = document.getElementById(`btn-check-outlined-${index}`);

    if (checkbox.checked == true) {
        fetch("/favourite/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ url: vacancyUrl, title: vacancyTitle }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
            });
    } else {
        fetch("/delete-favourite/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ url: vacancyUrl }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
            });
    }
}

function addVacancyToBlackList(index, vacancyUrl, vacancyTitle) {
    let vacancy = document.getElementById(`delete-vacancy-${index}`);
    vacancy.remove();
    // Получить текущее значение total_vacancies
    let totalVacanciesElement = document.getElementById("total-vacancies");
    let currentTotalVacancies = parseInt(
        totalVacanciesElement.textContent.split(": ")[1]
    );
    // Обновить значение total_vacancies и обновить элемент DOM
    totalVacanciesElement.textContent = `Найдено вакансий: ${
        currentTotalVacancies - 1
    }`;
    fetch("/add-to-black-list/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ url: vacancyUrl, title: vacancyTitle }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
        });
}

function removeVacancyFromBlackList(index, vacancyUrl) {
    const vacancy = document.getElementById(
        `btn-delete-from-black-list-${index}`
    );
    console.log(vacancy);
    vacancy.remove();
    fetch("/delete-from-blacklist/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ url: vacancyUrl }),
    }).then((response) => response.json());
}

function removeCompanyFromHiddenList(index, company) {
    const vacancy = document.getElementById(
        `btn-delete-from-hidden-companies-${index}`
    );
    console.log(vacancy);
    vacancy.remove();
    fetch("/delete-from-hidden-companies/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ name: company }),
    }).then((response) => response.json());
}

function removeFavouriteFromProfile(index, vacancyUrl) {
    const vacancy = document.getElementById(`favourite-block-${index}`);
    vacancy.remove();
    fetch("/delete-favourite/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ url: vacancyUrl }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(vacancyUrl);
        });
}

function clearProfileFavouriteList() {
    const vacancy = document.getElementById(`wrap-favourite`);
    vacancy.remove();
    fetch("/clear-favourite-list/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
    });
}

function clearProfileBlackList() {
    const vacancy = document.getElementById(`wrap-blacklist`);
    vacancy.remove();
    fetch("/clear-blacklist-list/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
    });
}

function clearProfileHiddenCompaniesList() {
    const vacancy = document.getElementById(`wrap-hidden-companies`);
    vacancy.remove();
    fetch("/clear-hidden-companies-list/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
    let companyLinks = document.querySelectorAll(".company-name");

    companyLinks.forEach(function (link) {
        let modal;

        link.addEventListener("click", function (e) {
            e.preventDefault();

            let companyName = link.dataset.company;

            modal = document.createElement("div");
            modal.className = "modal";
            modal.innerHTML = `
    <div class="modal-content">
        <span class="close">&times;</span>
        <p>Скрыть компанию?</p>
        <button class="hide-company-btn">Подтвердить</button>
    </div>
`;
            let hideCompanyBtn = modal.querySelector(".hide-company-btn");
            hideCompanyBtn.addEventListener("click", function () {
                let vacancies = document.querySelectorAll(".card");

                vacancies.forEach(function (vacancy) {
                    let vacancyCompany =
                        vacancy.querySelector(".company-name").dataset.company;
                    if (vacancyCompany === companyName) {
                        vacancy.style.display = "none";
                    }
                });

                fetch("/hide-company/", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: JSON.stringify({ company: companyName }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        console.log(vacancyUrl);
                    });

                modal.style.display = "none";
            });

            let closeModal = modal.querySelector(".close");
            closeModal.addEventListener("click", function () {
                modal.style.display = "none";
            });

            document.addEventListener("click", function (event) {
                if (
                    event.target !== modal &&
                    !modal.contains(event.target) &&
                    event.target !== link &&
                    !link.contains(event.target)
                ) {
                    modal.style.display = "none";
                    modal.remove();
                }
            });

            link.parentNode.insertBefore(modal, link.nextSibling);

            // Установка позиции окна при открытии
            let linkRect = link.getBoundingClientRect();
            let modalRect = modal.getBoundingClientRect();
            modal.style.left =
                linkRect.left + linkRect.width / 2 - modalRect.width / 2 + "px";
            modal.style.top =
                linkRect.top +
                linkRect.height / 2 -
                modalRect.height / 2 +
                "px";

            // Обработчик события resize для пересчета позиции окна при изменении размеров экрана
            window.addEventListener("resize", function () {
                linkRect = link.getBoundingClientRect();
                modalRect = modal.getBoundingClientRect();
                modal.style.left =
                    linkRect.left +
                    linkRect.width / 2 -
                    modalRect.width / 2 +
                    "px";
                modal.style.top =
                    linkRect.top +
                    linkRect.height / 2 -
                    modalRect.height / 2 +
                    "px";
            });

            modal.style.opacity = 0;
            modal.style.display = "block";
            setTimeout(function () {
                modal.style.opacity = 1;
            }, 10);
        });
    });
});
