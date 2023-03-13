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
