export function utilsInit() {
    const accordBtns = document.querySelectorAll("button.collapse-btn");
    accordBtns.forEach(el => {
        el.addEventListener('click', ()=> {
            const t = el.getElementsByTagName("svg")[0];
            t.classList.toggle('rotate');
        })
    });
}
