/**
 * Добавляет или удаляет вакансию из избранного при клике на соответствующую кнопку.
 * @param {number} index - Индекс кнопки на странице.
 * @param {string} pk - primary key вакансии.
 */
function addToFavourite(index, pk) {
    let checkbox = document.getElementById(`btn-check-outlined-${index}`);

    if (checkbox.checked == true) {
        fetch("/favourite/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ pk: pk }),
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
            body: JSON.stringify({ pk: pk }),
            
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
            });
    }
}

/**
 * Удаляет вакансию из списка на странице и добавляет ее в черный список при клике на соответствующую кнопку.
 * @param {number} index - Индекс кнопки на странице.
 * @param {string} pk - primary key вакансии.
 */
function addVacancyToBlackList(index, pk) {
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
        body: JSON.stringify({ pk: pk }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
        });
}

/**
 * Удаляет вакансию из черного списка при клике на соответствующую кнопку.
 * @param {number} index - Индекс кнопки на странице.
 * @param {string} pk - primary key вакансии.
 */
function removeVacancyFromBlackList(index, pk) {
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
        body: JSON.stringify({ pk: pk }),
    }).then((response) => response.json());
}

/**
 * Удаляет компанию из списка скрытых компаний при клике на соответствующую кнопку.
 * @param {number} index - Индекс кнопки на странице.
 * @param {string} company - Название компании.
 */
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

/**
 * Удаляет вакансию из избранного на странице профиля пользователя при клике на соответствующую кнопку.
 * @param {number} index - Индекс блока вакансии на странице.
 * @param {string} pk - primary key вакансии.
 */
function removeFavouriteFromProfile(index, pk) {
    const vacancy = document.getElementById(`favourite-block-${index}`);
    vacancy.remove();
    console.log(pk)
    fetch("/delete-favourite/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ pk: pk }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
        });
}

/**
 * Очищает список избранных вакансий на странице профиля пользователя.
 */
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

/**
 * Очищает черный список на странице профиля пользователя.
 */
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

/**
 * Очищает список скрытых компаний на странице профиля пользователя.
 */
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

/**
 * Получает значение cookie по имени.
 * @param {string} name - Имя cookie.
 * @returns {string|null} - Значение cookie или null, если cookie не найден.
 */
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

/**
 * Добавляет обработчик события "DOMContentLoaded" для элементов с классом "company-name".
 * При клике на элемент с классом "company-name" создает модальное окно с вопросом "Скрыть компанию?".
 * При подтверждении скрытия компании скрывает все вакансии этой компании на странице и отправляет запрос на сервер для скрытия компании.
 * @function
 */
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
