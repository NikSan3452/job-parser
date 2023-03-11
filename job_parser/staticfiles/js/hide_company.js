// (function () {
//     // Получаем все ссылки на компании.
//     var companyLinks = document.querySelectorAll(".company-name");

//     // Добавляем обработчик событий на каждую ссылку.
//     companyLinks.forEach(function (link) {
//         link.addEventListener("click", function (e) {
//             // Отменяем переход по ссылке по умолчанию.
//             e.preventDefault();

//             // Получаем название компании из атрибута "data-company".
//             var companyName = link.dataset.company;

//             // Проверяем, существует ли уже выпадающее меню для этой компании.
//             var menu = link.parentNode.querySelector(".company-menu");
//             if (menu) {
//                 // Если да, то удаляем его и завершаем выполнение функции.
//                 menu.parentNode.removeChild(menu);
//                 return;
//             }

//             // Создаем выпадающее меню.
//             menu = document.createElement("div");
//             menu.className = "company-menu";

//             // Создаем элемент "Скрыть вакансии этой компании".
//             var hideButton = document.createElement("a");
//             hideButton.className = "company-hide-button";
//             hideButton.textContent = "Скрыть вакансии этой компании";

//             // Добавляем обработчик событий на кнопку "Скрыть вакансии этой компании".
//             hideButton.addEventListener("click", function (e) {
//                 // Получаем все вакансии, которые относятся к этой компании.
//                 var vacancies = document.querySelectorAll(".card");

//                 vacancies.forEach(function (vacancy) {
//                     var vacancyCompany =
//                         vacancy.querySelector(".company-name").dataset.company;
//                     if (vacancyCompany === companyName) {
//                         vacancy.style.display = "none";
//                     }
//                 });

//                 // Удаляем выпадающее меню.
//                 menu.parentNode.removeChild(menu);

//                 // Отправляем запрос на сервер
//                 fetch("/hide-company/", {
//                     method: "POST",
//                     credentials: "same-origin",
//                     headers: {
//                         "X-Requested-With": "XMLHttpRequest",
//                         "X-CSRFToken": getCookie("csrftoken"),
//                     },
//                     body: JSON.stringify({ company: companyName }),
//                 })
//                     .then((response) => response.json())
//                     .then((data) => {
//                         console.log(vacancyUrl);
//                     });
//             });

//             // Добавляем кнопку "Скрыть вакансии этой компании" в меню.
//             menu.appendChild(hideButton);

//             // Размещаем меню под ссылкой на компанию.
//             link.parentNode.appendChild(menu);
//         });
//     });
// })();

// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== "") {
//         const cookies = document.cookie.split(";");
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === name + "=") {
//                 cookieValue = decodeURIComponent(
//                     cookie.substring(name.length + 1)
//                 );
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }

// (function () {
//     // Получаем все ссылки на компании.
//     var companyLinks = document.querySelectorAll(".company-name");

//     // Добавляем обработчик событий на каждую ссылку.
//     companyLinks.forEach(function (link) {
//         // Объявляем переменную для popup окна, чтобы была доступна вне функции-обработчика.
//         var popup;

//         link.addEventListener("click", function (e) {
//             // Отменяем переход по ссылке по умолчанию.
//             e.preventDefault();

//             // Получаем название компании из атрибута "data-company".
//             var companyName = link.dataset.company;

//             // Проверяем, существует ли уже popup окно для этой компании.
//             popup = link.querySelector(".company-popup");
//             if (popup) {
//                 // Если да, то удаляем его и завершаем выполнение функции.
//                 link.removeChild(popup);
//                 return;
//             }

//             // Создаем popup окно.
//             popup = document.createElement("div");
//             popup.className = "col-md-2 company-popup";
//             popup.textContent = "Скрыть компанию";
//             popup.style.position = "absolute";
//             popup.style.top = link.offsetTop + link.offsetHeight + "px";
//             popup.style.left = link.offsetLeft + "px";

//             // Добавляем обработчик событий на popup окно.
//             popup.addEventListener("click", function (e) {
//                 // Получаем все вакансии, которые относятся к этой компании.
//                 var vacancies = document.querySelectorAll(".card");

//                 vacancies.forEach(function (vacancy) {
//                     var vacancyCompany =
//                         vacancy.querySelector(".company-name").dataset.company;
//                     if (vacancyCompany === companyName) {
//                         vacancy.style.display = "none";
//                     }
//                 });

//                 // Отправляем запрос на сервер
//                 fetch("/hide-company/", {
//                     method: "POST",
//                     credentials: "same-origin",
//                     headers: {
//                         "X-Requested-With": "XMLHttpRequest",
//                         "X-CSRFToken": getCookie("csrftoken"),
//                     },
//                     body: JSON.stringify({ company: companyName }),
//                 })
//                     .then((response) => response.json())
//                     .then((data) => {
//                         console.log(vacancyUrl);
//                     });

//                 // Удаляем popup окно.
//                 link.removeChild(popup);
//             });

//             // Добавляем popup окно в ссылку на компанию.
//             link.appendChild(popup);

//             // Добавляем обработчик событий на document, чтобы закрывать popup окно при клике вне его.
//             document.addEventListener("click", function (e) {
//                 // Проверяем, был ли клик вне popup окна и ссылки на компанию.
//                 if (!popup.contains(e.target) && e.target !== link) {
//                     link.removeChild(popup);
//                 }
//             });
//         });
//     });
// })();

document.addEventListener("DOMContentLoaded", function () {
    var companyLinks = document.querySelectorAll(".company-name");

    companyLinks.forEach(function (link) {
        var modal;

        link.addEventListener("click", function (e) {
            e.preventDefault();

            var companyName = link.dataset.company;

            modal = document.createElement("div");
            modal.className = "modal";
            modal.innerHTML = `
    <div class="modal-content">
        <span class="close">&times;</span>
        <p>Cкрыть компанию?</p>
        <button class="hide-company-btn">Подтвердить</button>
    </div>
`;
            var hideCompanyBtn = modal.querySelector(".hide-company-btn");
            hideCompanyBtn.addEventListener("click", function () {
                var vacancies = document.querySelectorAll(".card");

                vacancies.forEach(function (vacancy) {
                    var vacancyCompany =
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

            var closeModal = modal.querySelector(".close");
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
            var linkRect = link.getBoundingClientRect();
            var modalRect = modal.getBoundingClientRect();
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
