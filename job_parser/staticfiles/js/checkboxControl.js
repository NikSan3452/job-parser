// Получаем элементы формы с типом "checkbox" для опыта работы и площадки
let expCheckboxes = document.querySelectorAll('input[type="checkbox"][name="experience"]');
let jobCheckboxes = document.querySelectorAll('input[type="checkbox"][name="job_board"]');
// Получаем элемент "Не имеет значения" для опыта работы
let expNoValue = document.querySelector('input[value="Не имеет значения"][name="experience"]');
// Получаем элемент "Не имеет значения" для площадки
let jobNoValue = document.querySelector('input[value="Не имеет значения"][name="job_board"]');

// Функция для проверки, выбрано ли хотя бы одно поле
function isAnyChecked(checkboxes) {
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            return true;
        }
    }
    return false;
}

// Добавляем обработчик события "change" для каждого флажка опыта работы
expCheckboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        // Если выбрано поле "Не имеет значения" для опыта работы
        if (expNoValue.checked && checkbox.value !== 'Не имеет значения') {
            // Снимаем флажок с поля "Не имеет значения" для опыта работы
            expNoValue.checked = false;
        }
        // Если ни одно поле не выбрано
        if (!isAnyChecked(expCheckboxes)) {
            // Выбираем поле "Не имеет значения" для опыта работы
            expNoValue.checked = true;
        }
    });
});

// Добавляем обработчик события "change" для каждого флажка площадки
jobCheckboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        // Если выбрано поле "Не имеет значения" для площадки
        if (jobNoValue.checked && checkbox.value !== 'Не имеет значения') {
            // Снимаем флажок с поля "Не имеет значения" для площадки
            jobNoValue.checked = false;
        }
        // Если ни одно поле не выбрано
        if (!isAnyChecked(jobCheckboxes)) {
            // Выбираем поле "Не имеет значения" для площадки
            jobNoValue.checked = true;
        }
    });
});

// Добавляем обработчик события "click" для поля "Не имеет значения" опыта работы
expNoValue.addEventListener('click', function(event) {
    // Снимаем флажки со всех других полей опыта работы
    expCheckboxes.forEach(function(checkbox) {
        if (checkbox.value !== 'Не имеет значения') {
            checkbox.checked = false;
        }
    });
});

// Добавляем обработчик события "click" для поля "Не имеет значения" площадки
jobNoValue.addEventListener('click', function(event) {
    // Снимаем флажки со всех других полей площадки
    jobCheckboxes.forEach(function(checkbox) {
        if (checkbox.value !== 'Не имеет значения') {
            checkbox.checked = false;
        }
    });
});