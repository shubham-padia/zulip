import {$} from "jquery";

import * as loading from "./loading.ts";

let top_of_feed_indicator_showing = false;
let loading_newer_messages_indicator_showing = false;

// The indicator at the top of the feed is shown for two reasons: the
// initial page load, until the initial message fetch completes, and a
// fetch for older messages. It stays up while either applies.
let initial_page_load_pending = false;
let fetching_older_messages = false;

function top_of_feed_in_view(): boolean {
    // The indicator rests at the bottom of the navbar, which is also
    // where it sticks, so it is only away from the top of the feed once
    // the page has scrolled. This is what message_viewport.at_rendered_top
    // checks too, but importing that module here makes an import cycle.
    return window.scrollY <= 0;
}

function update_top_of_feed_indicator(): void {
    // The initial page load is shown wherever the feed is scrolled to.
    // A fetch for older messages is only shown while the top of the
    // feed, where those messages will go, is in view; one that starts
    // while the user is reading further down should not draw attention
    // to itself.
    const should_show =
        initial_page_load_pending || (fetching_older_messages && top_of_feed_in_view());
    if (should_show && !top_of_feed_indicator_showing) {
        $("#top_of_feed_gutter").addClass("loading");
        top_of_feed_indicator_showing = true;
    } else if (!should_show && top_of_feed_indicator_showing) {
        $("#top_of_feed_gutter").removeClass("loading");
        top_of_feed_indicator_showing = false;
    }
}

export function update_for_scroll_position(): void {
    // Scrolling can bring the top of the feed into or out of view while
    // older messages are being fetched.
    if (fetching_older_messages) {
        update_top_of_feed_indicator();
    }
}

export function show_loading_initial_page(): void {
    initial_page_load_pending = true;
    update_top_of_feed_indicator();
}

export function hide_loading_initial_page(): void {
    initial_page_load_pending = false;
    update_top_of_feed_indicator();
}

export function show_loading_older(): void {
    fetching_older_messages = true;
    update_top_of_feed_indicator();
}

export function hide_loading_older(): void {
    fetching_older_messages = false;
    update_top_of_feed_indicator();
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
