import {$} from "jquery";

import * as loading from "./loading.ts";

let loading_newer_messages_indicator_showing = false;

// The two lines at the top of the feed are separate elements with
// separate owners. The page load line is shown by setup.ts until the
// initial fetch completes. The older messages line follows the fetches
// for older messages in the current narrow, and is reset with it.
export function show_loading_initial_page(): void {
    $("#page_loading_indicator").addClass("loading");
}

export function hide_loading_initial_page(): void {
    $("#page_loading_indicator").removeClass("loading");
}

export function show_loading_older(): void {
    $("#loading_older_messages_indicator").addClass("loading");
}

export function hide_loading_older(): void {
    $("#loading_older_messages_indicator").removeClass("loading");
}

export function show_loading_newer(): void {
    if (!loading_newer_messages_indicator_showing) {
        $(".bottom-messages-logo").show();
        $(".bottom-messages-logo").toggleClass("loading", true);
        loading.make_indicator($("#loading_more_indicator"), {abs_positioned: true});
        loading_newer_messages_indicator_showing = true;
    }
}

export function hide_loading_newer(): void {
    if (loading_newer_messages_indicator_showing) {
        $(".bottom-messages-logo").hide();
        $(".bottom-messages-logo").toggleClass("loading", false);
        loading.destroy_indicator($("#loading_more_indicator"));
        loading_newer_messages_indicator_showing = false;
    }
}

export function hide_indicators(): void {
    hide_loading_older();
    hide_loading_newer();
}
