const expandLink = document.querySelector(".expand-link");
const collapseLink = document.querySelector(".collapse-link");
const shortText = document.querySelector(".short-text");
const fullText = document.querySelector(".full-text");

expandLink.addEventListener("click", function () {
    shortText.style.display = "none";
    fullText.style.display = "inline";
    expandLink.style.display = "none";
    collapseLink.style.display = "inline";
});

collapseLink.addEventListener("click", function () {
    shortText.style.display = "inline";
    fullText.style.display = "none";
    expandLink.style.display = "inline";
    collapseLink.style.display = "none";
});
