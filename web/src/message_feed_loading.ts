import {$} from "jquery";

import * as loading from "./loading.ts";
import * as util from "./util.ts";

// Keep the older messages line visible for at least this long, so
// that a fast fetch doesn't make it flash briefly on screen. This
// matches the sweep duration of the line's animation in zulip.css, so
// the line always gets to go end to end at least once.
export const MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS = 750;
// How long the line takes to fade out, matching the opacity
// transition in zulip.css.
export const TOP_OF_FEED_INDICATOR_FADE_OUT_MS = 200;

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

let older_line_showing = false;
let older_line_shown_at = 0;
let pending_hide_older_line_timer: ReturnType<typeof setTimeout> | undefined;
let older_line_fade_out_timer: ReturnType<typeof setTimeout> | undefined;
let run_when_older_line_hidden_callbacks: (() => void)[] = [];

function cancel_pending_hide_older_line(): void {
    if (pending_hide_older_line_timer !== undefined) {
        clearTimeout(pending_hide_older_line_timer);
        pending_hide_older_line_timer = undefined;
    }
}

function hide_older_line_now(): void {
    cancel_pending_hide_older_line();
    if (older_line_showing) {
        // The pulse keeps moving while the line fades out; the class
        // that keeps it drawn comes off once the fade ends.
        $("#loading_older_messages_indicator").removeClass("loading").addClass("fade-out");
        older_line_fade_out_timer = setTimeout(() => {
            $("#loading_older_messages_indicator").removeClass("fade-out");
            older_line_fade_out_timer = undefined;
        }, TOP_OF_FEED_INDICATOR_FADE_OUT_MS);
        older_line_showing = false;
    }
    const callbacks = run_when_older_line_hidden_callbacks;
    run_when_older_line_hidden_callbacks = [];
    for (const callback of callbacks) {
        callback();
    }
}

export function run_when_top_of_feed_indicator_hidden(callback: () => void): void {
    // Notices that say there is nothing more to load should not appear
    // while the line is still being kept on screen; they wait until it
    // goes away.
    if (!older_line_showing) {
        callback();
        return;
    }
    run_when_older_line_hidden_callbacks.push(callback);
}

export function cancel_run_when_top_of_feed_indicator_hidden(): void {
    run_when_older_line_hidden_callbacks = [];
}

export function show_loading_older(): void {
    // Each fetch restarts the minimum display time, including one that
    // starts while we're waiting to hide the line; the pending hide
    // belongs to the previous fetch, so drop it.
    cancel_pending_hide_older_line();
    older_line_shown_at = Date.now();
    if (!older_line_showing) {
        if (older_line_fade_out_timer !== undefined) {
            clearTimeout(older_line_fade_out_timer);
            older_line_fade_out_timer = undefined;
        }
        $("#loading_older_messages_indicator").removeClass("fade-out").addClass("loading");
        older_line_showing = true;
    }
}

export function hide_loading_older(): void {
    if (!older_line_showing) {
        return;
    }
    const remaining_ms = util.get_remaining_time(
        older_line_shown_at,
        MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS,
    );
    if (remaining_ms > 0) {
        cancel_pending_hide_older_line();
        pending_hide_older_line_timer = setTimeout(hide_older_line_now, remaining_ms);
        return;
    }
    hide_older_line_now();
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
    // Called when resetting the UI for a new narrow, so hide right away.
    // Anything waiting on the old narrow's line is stale.
    cancel_run_when_top_of_feed_indicator_hidden();
    hide_older_line_now();
    hide_loading_newer();
}
