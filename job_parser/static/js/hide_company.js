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
        <p>Cкрыть компанию?</p>
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
