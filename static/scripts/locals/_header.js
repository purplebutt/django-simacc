'use strict';


export function navbarToggle() {
    const navOpenBtn = document.querySelector("button.nav-open-btn");
    const navCloseBtn = document.querySelector("button.nav-close-btn");
    const overlayDiv = document.querySelector("div.overlay");
    const navbarLinks = document.querySelectorAll("ul.navbar-nav li");
    const navbarDiv = document.querySelector("nav.navbarCover");

    navOpenBtn.addEventListener('click', headerToggler)
    navCloseBtn.addEventListener('click', headerToggler)
    overlayDiv.addEventListener('click', headerToggler)
    navbarLinks.forEach(e => {
        e.addEventListener('click', headerToggler)
    })

    function headerToggler() {
        navbarDiv.classList.toggle("active");
    }
}