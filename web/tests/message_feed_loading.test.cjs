"use strict";

const assert = require("node:assert/strict");

const {clock, zrequire} = require("./lib/namespace.cjs");
const {run_test} = require("./lib/test.cjs");
const {$} = require("./lib/zjquery.cjs");

const message_feed_loading = zrequire("message_feed_loading");
const {MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS} = message_feed_loading;

function is_loading() {
    return $("#loading_older_messages_indicator").hasClass("loading");
}

run_test("minimum display time", () => {
    message_feed_loading.show_loading_older();
    assert.ok(is_loading());

    // A fetch that finishes quickly leaves the line up until the
    // minimum display time has elapsed.
    clock.tick(100);
    message_feed_loading.hide_loading_older();
    assert.ok(is_loading());
    clock.tick(MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS - 100 - 1);
    assert.ok(is_loading());
    clock.tick(1);
    assert.ok(!is_loading());

    // A slow fetch hides the line right away.
    message_feed_loading.show_loading_older();
    clock.tick(MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS);
    message_feed_loading.hide_loading_older();
    assert.ok(!is_loading());
});

run_test("new fetch during pending hide", () => {
    message_feed_loading.show_loading_older();
    message_feed_loading.hide_loading_older();
    clock.tick(100);

    // Another fetch starts before the minimum time is up. The first
    // fetch's pending hide must not take the line down while this one
    // is still in flight, however long it takes.
    message_feed_loading.show_loading_older();
    clock.tick(MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS * 3);
    assert.ok(is_loading());
    message_feed_loading.hide_loading_older();
    assert.ok(!is_loading());
});

run_test("hide_indicators hides immediately", () => {
    message_feed_loading.show_loading_older();
    message_feed_loading.hide_loading_older();
    message_feed_loading.hide_indicators();
    assert.ok(!is_loading());

    // The pending hide from before the reset must not affect a fetch
    // in the new narrow.
    message_feed_loading.show_loading_older();
    clock.tick(MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS * 3);
    assert.ok(is_loading());
    message_feed_loading.hide_loading_older();
    assert.ok(!is_loading());
});

run_test("run_when_top_of_feed_indicator_hidden", () => {
    let runs = 0;
    const callback = () => {
        runs += 1;
    };

    // Nothing is showing, so the callback runs right away.
    message_feed_loading.run_when_top_of_feed_indicator_hidden(callback);
    assert.equal(runs, 1);

    // While the line is being kept on screen, the callback waits until
    // it is hidden.
    message_feed_loading.show_loading_older();
    message_feed_loading.hide_loading_older();
    message_feed_loading.run_when_top_of_feed_indicator_hidden(callback);
    clock.tick(MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS - 1);
    assert.equal(runs, 1);
    clock.tick(1);
    assert.ok(!is_loading());
    assert.equal(runs, 2);

    // Resetting for a new narrow drops callbacks from the old one.
    message_feed_loading.show_loading_older();
    message_feed_loading.hide_loading_older();
    message_feed_loading.run_when_top_of_feed_indicator_hidden(callback);
    message_feed_loading.hide_indicators();
    clock.tick(MIN_TOP_OF_FEED_INDICATOR_DISPLAY_MS);
    assert.equal(runs, 2);
});

run_test("page load line is independent", () => {
    // The page load line has no minimum display time and is not
    // affected by fetches for older messages or by narrow changes.
    message_feed_loading.show_loading_initial_page();
    assert.ok($("#page_loading_indicator").hasClass("loading"));
    message_feed_loading.show_loading_older();
    message_feed_loading.hide_loading_older();
    message_feed_loading.hide_indicators();
    assert.ok($("#page_loading_indicator").hasClass("loading"));
    assert.ok(!is_loading());
    message_feed_loading.hide_loading_initial_page();
    assert.ok(!$("#page_loading_indicator").hasClass("loading"));
});
