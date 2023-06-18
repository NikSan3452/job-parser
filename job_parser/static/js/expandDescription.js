/**
 * Раскрывает и сворачивает текстовые блоки на странице при клике на соответствующие ссылки.
 * @param {NodeListOf<Element>} expandLinks - Список ссылок для раскрытия текста.
 * @param {NodeListOf<Element>} collapseLinks - Список ссылок для сворачивания текста.
 * @param {NodeListOf<Element>} shortTexts - Список коротких текстовых блоков, которые будут скрыты при раскрытии полного текста.
 * @param {NodeListOf<Element>} fullTexts - Список полных текстовых блоков, которые будут показаны при раскрытии текста.
 */
const expandLinks = document.querySelectorAll(".expand-link");
const collapseLinks = document.querySelectorAll(".collapse-link");
const shortTexts = document.querySelectorAll(".short-text");
const fullTexts = document.querySelectorAll(".full-text");

for (let i = 0; i < expandLinks.length; i++) {
    expandLinks[i].addEventListener("click", function () {
        shortTexts[i].style.display = "none";
        fullTexts[i].style.display = "inline";
        expandLinks[i].style.display = "none";
        collapseLinks[i].style.display = "inline";
    });

    collapseLinks[i].addEventListener("click", function () {
        shortTexts[i].style.display = "inline";
        fullTexts[i].style.display = "none";
        expandLinks[i].style.display = "inline";
        collapseLinks[i].style.display = "none";
    });
}
