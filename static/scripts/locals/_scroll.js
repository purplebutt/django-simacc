export function scrollChangeNavBg() {
    const totop = document.querySelector("a.oc-scroll-up");
    // const header = document.querySelector("header");
    // const navbarEls = document.querySelectorAll(
    //     "header h1.logo,header>div.container>button,header>div.container>a.logo");
    // const navbarlink = document.querySelectorAll("a.navbar-link");
    const observer = new IntersectionObserver(function(entries){
        if(entries[0].isIntersecting==true) {
            // header.style.backgroundImage="none";
            // header.style.color="var(--space-cadet-1)";
            // header.style.opacity="1";
            // navbarlink.forEach(el=> {
            //     el.style.color="var(--space-cadet-1)"
            // })
            // navbarEls.forEach(el=> {
            //     el.style.color="var(--space-cadet-1)"
            // });
            totop.classList.remove('active'); //hide to-top
        }
        else {
            // header.style.backgroundImage="var(--gradient-1)";
            // header.style.opacity=".9";
            // header.style.color="var(--white)";
            // if (window.innerWidth>=992) {
            //     navbarlink.forEach(el=> {
            //         el.style.color="var(--white)"
            //     })
            // }
            // navbarEls.forEach(el=> {
            //     el.style.color="var(--white)"
            // });
            totop.classList.add('active'); //show to-top
        }
    }, {threshold: [.07]});

    observer.observe(document.querySelector("section#welcome"));
}