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

function addVacancyToBlackList(index, vacancyUrl) {
    let vacancy = document.getElementById(`delete-vacancy-${index}`);
    vacancy.remove();

    fetch("/add-to-black-list/", {
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
