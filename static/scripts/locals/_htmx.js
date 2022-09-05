
 function htmxBeforeSwap() {
    htmx.on("htmx:beforeSwap", (evt) => {
        let domainAndProtocol = window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + "/";
        // url path (without domain and protocol) for password change
        let login_url = "/require/login/";

        let url = new URL(evt.detail.xhr.responseURL);
        if ( url.href == domainAndProtocol || url.pathname == login_url) 
        {
            evt.detail.shouldSwap = false;  // cancel htmx swap
            if (url.pathname == login_url && window.location.pathname != "/"){
                window.location.href = url.origin + login_url + "?next=" + window.location.pathname;
            }
            else {
                location.reload(true);   // reload web page with current url on browser
            }
        }
    })
}

function htmxConfigRequest() {
    htmx.on("htmx.configRequest", (evt)=> {
        let params = evt.detail.parameters;
        //TODO: add code here to configure htmx request
    })
}

export function htmxEventListenerInit() {
    htmxBeforeSwap();
    // htmxConfigRequest();
}


function htmxSpinnerAnimate() {
    const triggers = document.querySelectorAll("button.htmx-trigger, a.htmx-trigger");

    function t_onclick(t) {
        const caller = t.target;
        const targets = document.querySelectorAll(caller.getAttribute('htmx-target'));
        const spinners = document.querySelectorAll(caller.getAttribute('htmx-spinner'));
        targets.forEach(t => {
            t.classList.add('d-none');
        });
        spinners.forEach(s => {
            s.classList.remove('d-none');
        });
        console.log(triggers);
    }

    triggers.forEach(t => {
        t.addEventListener('click', t_onclick);
    });
}
