import { navbarToggle } from "./locals/_header.js";
import { htmxEventListenerInit} from "./locals/_htmx.js";
import { scrollChangeNavBg } from "./locals/_scroll.js";
import { utilsInit } from "./locals/_utils.js";


export function scriptsInit() {
    htmxEventListenerInit();
}

scriptsInit();
// navbarToggle();
// scrollChangeNavBg();
// utilsInit();
