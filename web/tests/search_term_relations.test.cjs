"use strict";

const assert = require("node:assert/strict");

const {make_realm} = require("./lib/example_realm.cjs");
const {make_user} = require("./lib/example_user.cjs");
const {zrequire} = require("./lib/namespace.cjs");
const {run_test} = require("./lib/test.cjs");

const people = zrequire("people");
const stream_data = zrequire("stream_data");
const search_term_relations = zrequire("search_term_relations");
const {set_current_user, set_realm} = zrequire("state_data");

set_realm(make_realm());
set_current_user({});

const me = make_user({
    email: "me@example.com",
    user_id: 30,
    full_name: "Me Myself",
});
const joe = make_user({
    email: "joe@example.com",
    user_id: 31,
    full_name: "joe",
});
const steve = make_user({
    email: "steve@example.com",
    user_id: 32,
    full_name: "steve",
});

people.init();
people.add_active_user(me, "server_events");
people.add_active_user(joe, "server_events");
people.add_active_user(steve, "server_events");
people.initialize_current_user(me.user_id);

const public_id = 1;
const web_public_id = 2;
const private_id = 3;
const archived_id = 4;

stream_data.add_sub_for_tests({name: "devel", stream_id: public_id});
stream_data.add_sub_for_tests({name: "lounge", stream_id: web_public_id, is_web_public: true});
stream_data.add_sub_for_tests({name: "secret", stream_id: private_id, invite_only: true});
stream_data.add_sub_for_tests({name: "old", stream_id: archived_id, is_archived: true});

function term(operator, operand, negated = false) {
    return {operator, operand, negated};
}

const {relation, should_offer, should_offer_operator} = search_term_relations;

run_test("relation for one operator", () => {
    // Partition operators: a message has one channel, topic, sender,
    // and id, so different operands can never match the same message.
    assert.equal(relation(term("channel", "1"), term("channel", "1")), "equal");
    assert.equal(relation(term("channel", "1"), term("channel", "2")), "disjoint");
    assert.equal(relation(term("sender", 31), term("sender", 31)), "equal");
    assert.equal(relation(term("sender", 31), term("sender", 32)), "disjoint");
    assert.equal(relation(term("id", "17"), term("id", "17")), "equal");
    assert.equal(relation(term("id", "17"), term("id", "18")), "disjoint");

    // Topics compare case-insensitively, like the topic predicate,
    // and the resolved-topic prefix makes a different topic.
    assert.equal(relation(term("topic", "Lunch"), term("topic", "lunch")), "equal");
    assert.equal(relation(term("topic", "lunch"), term("topic", "dinner")), "disjoint");
    assert.equal(relation(term("topic", "lunch"), term("topic", "✔ lunch")), "disjoint");

    // Direct message operands are compared as sorted sets.
    assert.equal(relation(term("dm", [32, 31]), term("dm", [31, 32])), "equal");
    assert.equal(relation(term("dm", [31]), term("dm", [32])), "disjoint");

    // A conversation including all of a larger group also includes
    // the smaller group.
    assert.equal(relation(term("dm-including", [31]), term("dm-including", [31])), "equal");
    assert.equal(relation(term("dm-including", [31, 32]), term("dm-including", [31])), "subset");
    assert.equal(relation(term("dm-including", [31]), term("dm-including", [31, 32])), "superset");
    // Groups that only overlap can both include a conversation.
    assert.equal(relation(term("dm-including", [31]), term("dm-including", [32])), "unknown");

    // Web-public channels are a subset of public channels; archived
    // channels can have any privacy.
    assert.equal(relation(term("channels", "public"), term("channels", "public")), "equal");
    assert.equal(relation(term("channels", "web-public"), term("channels", "public")), "subset");
    assert.equal(relation(term("channels", "public"), term("channels", "web-public")), "superset");
    assert.equal(relation(term("channels", "archived"), term("channels", "public")), "unknown");

    // Different "is:"/"has:" operands can overlap, except the
    // message-kind cases tested separately below.
    assert.equal(relation(term("is", "starred"), term("is", "starred")), "equal");
    assert.equal(relation(term("is", "starred"), term("is", "mentioned")), "unknown");
    assert.equal(relation(term("has", "link"), term("has", "link")), "equal");
    assert.equal(relation(term("has", "link"), term("has", "image")), "unknown");
    assert.equal(relation(term("is", "resolved"), term("is", "followed")), "unknown");

    // Two different date operands can name the same day ("today"),
    // and one message can mention two users.
    assert.equal(relation(term("date", "2026-08-18"), term("date", "2026-08-18")), "equal");
    assert.equal(relation(term("date", "2026-08-18"), term("date", "today")), "unknown");
    assert.equal(relation(term("mentions", 31), term("mentions", 31)), "equal");
    assert.equal(relation(term("mentions", 31), term("mentions", 32)), "unknown");

    assert.equal(relation(term("search", "foo"), term("search", "bar")), "unknown");
});

run_test("relation across message kinds", () => {
    // Channel-message terms and direct-message terms are disjoint.
    assert.equal(relation(term("is", "dm"), term("channel", "1")), "disjoint");
    assert.equal(relation(term("topic", "lunch"), term("dm", [31])), "disjoint");
    assert.equal(relation(term("channels", "public"), term("dm-including", [31])), "disjoint");
    assert.equal(relation(term("is", "resolved"), term("is", "dm")), "disjoint");
    assert.equal(relation(term("is", "followed"), term("dm", [31])), "disjoint");
});

run_test("relation across operators", () => {
    // Every direct message conversation is a direct message.
    assert.equal(relation(term("dm", [31]), term("is", "dm")), "subset");
    assert.equal(relation(term("is", "dm"), term("dm", [31])), "superset");
    assert.equal(relation(term("dm-including", [31]), term("is", "dm")), "subset");
    assert.equal(relation(term("dm", [31]), term("is", "starred")), "unknown");

    // "dm:A" includes everyone in B only when B is part of A.
    assert.equal(relation(term("dm", [31, 32]), term("dm-including", [31])), "subset");
    assert.equal(relation(term("dm", [31]), term("dm-including", [32])), "disjoint");
    assert.equal(relation(term("dm-including", [31]), term("dm", [31, 32])), "superset");
    // You are part of all of your conversations, so including
    // yourself includes every direct message.
    assert.equal(relation(term("dm", [31]), term("dm-including", [me.user_id])), "subset");
    assert.equal(relation(term("dm-including", [me.user_id]), term("dm", [31])), "superset");
    assert.equal(
        relation(term("dm-including", [31]), term("dm-including", [me.user_id])),
        "subset",
    );

    // A channel is inside a "channels:" scope, or disjoint from it,
    // depending on its privacy; an unknown channel never blocks.
    assert.equal(relation(term("channel", "1"), term("channels", "public")), "subset");
    assert.equal(relation(term("channel", "2"), term("channels", "public")), "subset");
    assert.equal(relation(term("channel", "2"), term("channels", "web-public")), "subset");
    assert.equal(relation(term("channel", "1"), term("channels", "web-public")), "disjoint");
    assert.equal(relation(term("channel", "3"), term("channels", "public")), "disjoint");
    assert.equal(relation(term("channel", "4"), term("channels", "archived")), "subset");
    assert.equal(relation(term("channel", "1"), term("channels", "archived")), "disjoint");
    assert.equal(relation(term("channels", "public"), term("channel", "1")), "superset");
    assert.equal(relation(term("channel", "999"), term("channels", "public")), "unknown");
    assert.equal(relation(term("channel", "1"), term("channels", "bogus")), "unknown");

    // Pairs the module knows nothing about never suppress.
    assert.equal(relation(term("sender", 31), term("channel", "1")), "unknown");
    assert.equal(relation(term("near", "17"), term("id", "17")), "unknown");
});

run_test("relation sees through aliases", () => {
    // "in:home" means "-is:muted"; the polarity flip is should_offer's
    // job, so the plain sets are equal.
    assert.equal(relation(term("in", "home"), term("is", "muted")), "equal");
    // A "mentions" term naming yourself means "is:mentioned".
    assert.equal(relation(term("mentions", me.user_id), term("is", "mentioned")), "equal");
    assert.equal(relation(term("mentions", joe.user_id), term("is", "mentioned")), "unknown");
    assert.equal(relation(term("in", "all"), term("is", "muted")), "unknown");
});

run_test("equal terms are not offered again", () => {
    // Repeating the term duplicates it; flipping it contradicts it.
    assert.equal(should_offer(term("is", "starred"), [term("is", "starred")]), false);
    assert.equal(should_offer(term("is", "starred", true), [term("is", "starred")]), false);
    assert.equal(should_offer(term("is", "starred"), [term("is", "starred", true)]), false);
    assert.equal(should_offer(term("is", "starred", true), [term("is", "starred", true)]), false);
});

run_test("suggestions when the bar term is narrower", () => {
    // The bar's channel is public, so the scope adds nothing, and
    // excluding the scope excludes the bar's own channel.
    assert.equal(should_offer(term("channels", "public"), [term("channel", "1")]), false);
    assert.equal(should_offer(term("channels", "public", true), [term("channel", "1")]), false);
    // With the narrower term excluded, both scope suggestions still
    // change the search.
    assert.equal(should_offer(term("channels", "public"), [term("channel", "1", true)]), true);
    assert.equal(should_offer(term("channels", "public", true), [term("channel", "1", true)]), true);
});

run_test("suggestions when the bar term is broader", () => {
    // Excluding one channel of the scope narrows the search; the
    // plain form is withheld by policy, not derivation.
    assert.equal(should_offer(term("channel", "1", true), [term("channels", "public")]), true);
    assert.equal(should_offer(term("channel", "1"), [term("channels", "public")]), false);
    // With the whole scope excluded, a channel inside it can't match,
    // and excluding it again changes nothing.
    assert.equal(should_offer(term("channel", "1"), [term("channels", "public", true)]), false);
    assert.equal(should_offer(term("channel", "1", true), [term("channels", "public", true)]), false);
    // A private channel is outside the excluded public scope, so both
    // its suggestions still make sense.
    assert.equal(should_offer(term("channel", "3"), [term("channels", "public", true)]), true);
    assert.equal(should_offer(term("channel", "3", true), [term("channels", "public", true)]), true);
});

run_test("suggestions disjoint from a bar term", () => {
    // Another topic contradicts the bar's topic, and excluding it
    // changes nothing; after "-topic:a", both forms make sense.
    assert.equal(should_offer(term("topic", "b"), [term("topic", "a")]), false);
    assert.equal(should_offer(term("topic", "b", true), [term("topic", "a")]), false);
    assert.equal(should_offer(term("topic", "b"), [term("topic", "a", true)]), true);
    assert.equal(should_offer(term("topic", "b", true), [term("topic", "a", true)]), true);
    assert.equal(should_offer(term("channel", "1"), [term("is", "dm")]), false);
    assert.equal(should_offer(term("channel", "1", true), [term("is", "dm")]), false);
});

run_test("suggestions see through aliases", () => {
    assert.equal(should_offer(term("is", "muted"), [term("in", "home")]), false);
    assert.equal(should_offer(term("is", "muted", true), [term("in", "home")]), false);
    assert.equal(should_offer(term("is", "muted"), [term("in", "home", true)]), false);
    assert.equal(should_offer(term("is", "mentioned"), [term("mentions", me.user_id, true)]), false);
    assert.equal(should_offer(term("mentions", me.user_id), [term("is", "mentioned", true)]), false);
    assert.equal(should_offer(term("dm", [32, 31]), [term("dm", [31, 32], true)]), false);
});

run_test("suggestions withheld by policy", () => {
    assert.equal(should_offer(term("date", "today"), [term("date", "2026-08-18")]), false);
    assert.equal(should_offer(term("date", "today"), [term("near", "17")]), false);
    assert.equal(should_offer(term("near", "17"), [term("date", "today")]), false);
    assert.equal(should_offer(term("channels", "archived"), [term("channels", "public")]), false);
    assert.equal(
        should_offer(term("mentions", joe.user_id), [term("mentions", steve.user_id)]),
        false,
    );
    assert.equal(
        should_offer(term("mentions", joe.user_id, true), [term("mentions", steve.user_id)]),
        false,
    );
    assert.equal(should_offer(term("channel", "1"), [term("in", "all")]), false);
    assert.equal(should_offer(term("channels", "public"), [term("in", "all")]), false);
    assert.equal(should_offer(term("is", "dm"), [term("in", "all")]), false);
    // Rules only key on plain bar terms, and only name what they
    // name: other "is:" operands aren't blocked by "in:".
    assert.equal(should_offer(term("channel", "1"), [term("in", "all", true)]), true);
    assert.equal(should_offer(term("is", "starred"), [term("in", "all")]), true);
    assert.equal(should_offer(term("date", "today"), [term("date", "2026-08-18", true)]), true);
});

run_test("suggestions against several bar terms", () => {
    assert.equal(should_offer(term("is", "starred"), []), true);
    assert.equal(should_offer(term("is", "starred"), [term("has", "link")]), true);
    assert.equal(
        should_offer(term("is", "starred"), [term("has", "link"), term("is", "starred", true)]),
        false,
    );
});

run_test("operators after a term with the same operator", () => {
    // Every completion of a second "topic:" would duplicate or
    // contradict the topic already in the bar.
    assert.equal(should_offer_operator("topic", false, [term("topic", "a")]), false);
    assert.equal(should_offer_operator("topic", true, [term("topic", "a")]), false);
    assert.equal(should_offer_operator("channel", false, [term("channel", "1")]), false);
    assert.equal(should_offer_operator("sender", false, [term("sender", 31)]), false);
    assert.equal(should_offer_operator("dm", false, [term("dm", [31])]), false);
    // After an excluded topic, other topics are meaningful.
    assert.equal(should_offer_operator("topic", false, [term("topic", "a", true)]), true);
    assert.equal(should_offer_operator("topic", true, [term("topic", "a", true)]), true);
    // "dm-including" terms combine, so a second one is offered.
    assert.equal(should_offer_operator("dm-including", false, [term("dm-including", [31])]), true);
});

run_test("operators of the wrong message kind", () => {
    assert.equal(should_offer_operator("channel", false, [term("is", "dm")]), false);
    assert.equal(should_offer_operator("channels", false, [term("dm", [31])]), false);
    assert.equal(should_offer_operator("topic", false, [term("dm-including", [31])]), false);
    assert.equal(should_offer_operator("dm", false, [term("channel", "1")]), false);
    assert.equal(should_offer_operator("dm-including", false, [term("is", "resolved")]), false);
    assert.equal(should_offer_operator("dm", false, [term("is", "followed")]), false);
    // Negated terms never withhold an operator.
    assert.equal(should_offer_operator("channel", false, [term("is", "dm", true)]), true);
    assert.equal(should_offer_operator("dm", false, [term("channel", "1", true)]), true);
    // Operators that fit either message kind are unaffected.
    assert.equal(should_offer_operator("sender", false, [term("is", "dm")]), true);
    assert.equal(should_offer_operator("near", false, [term("channel", "1")]), true);
});

run_test("operators withheld by policy", () => {
    assert.equal(should_offer_operator("date", false, [term("date", "today")]), false);
    assert.equal(should_offer_operator("date", false, [term("near", "17")]), false);
    assert.equal(should_offer_operator("near", false, [term("date", "today")]), false);
    assert.equal(should_offer_operator("mentions", false, [term("mentions", 31)]), false);
    assert.equal(should_offer_operator("mentions", true, [term("mentions", 31)]), false);
    assert.equal(should_offer_operator("channel", false, [term("channels", "public")]), false);
    assert.equal(should_offer_operator("channels", false, [term("channels", "public")]), false);
    // Excluding a channel or a scope is offered next to a scope.
    assert.equal(should_offer_operator("channel", true, [term("channels", "public")]), true);
    assert.equal(should_offer_operator("channels", true, [term("channels", "public")]), true);
    assert.equal(should_offer_operator("channel", false, [term("in", "home")]), false);
    assert.equal(should_offer_operator("channels", false, [term("in", "all")]), false);
    // A single channel pins down its scopes, so no "channels:"
    // completion could be offered next to it.
    assert.equal(should_offer_operator("channels", false, [term("channel", "1")]), false);
    assert.equal(should_offer_operator("channels", true, [term("channel", "1")]), false);
});
