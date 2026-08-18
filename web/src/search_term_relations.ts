import assert from "minimalistic-assert";

import * as people from "./people.ts";
import type {NarrowCanonicalOperator, NarrowCanonicalTerm} from "./state_data.ts";
import * as stream_data from "./stream_data.ts";
import * as util from "./util.ts";

// This module decides whether a search suggestion is still worth
// offering, given the terms already in the search bar.
//
// The decision is derived from the relation between the sets of
// messages the two terms match, instead of hand-maintained tables of
// operator pairs: a suggestion is withheld exactly when adding it
// could not change the search (it repeats or is implied by the bar),
// or when the combined search can never match anything. A small
// policy function covers the few product rules that aren't about
// meaning at all.

// Relation between the sets of messages the plain forms of two terms
// match, ignoring their negated flags. "subset" means every message
// the first term matches is also matched by the second. "unknown" is
// the safe default: it never suppresses a suggestion.
export type Relation = "equal" | "subset" | "superset" | "disjoint" | "unknown";

// Operators whose different operands can never match the same
// message: a message is in exactly one channel, has one topic, one
// sender, and one id, and a direct message conversation has one
// exact set of recipients. "date" is not here: two different date
// operands can name the same day ("today" and the date itself).
const partition_operators = new Set(["channel", "topic", "sender", "dm", "id"]);

// Messages are either channel messages or direct messages, and some
// terms can only ever match one of the two kinds. Terms of different
// kinds are disjoint. The kind of each term follows its predicate in
// filter.ts: "is:resolved" and "is:followed" require a channel
// message, "is:dm" a direct message.
type MessageKind = "channel" | "direct" | "any";

function message_kind(term: NarrowCanonicalTerm): MessageKind {
    switch (term.operator) {
        case "channel":
        case "channels":
        case "topic":
            return "channel";
        case "dm":
        case "dm-including":
            return "direct";
        case "is":
            if (term.operand === "dm") {
                return "direct";
            }
            if (term.operand === "resolved" || term.operand === "followed") {
                return "channel";
            }
            return "any";
        default:
            return "any";
    }
}

// Terms arrive already canonicalized by Filter (is:private -> is:dm,
// synonym operators renamed, mentions:me from typed text ->
// is:mentioned). This adds the rewrites Filter doesn't do, so that
// the relation logic only ever sees one spelling of each filter:
// - "in:home" means "-is:muted" (see Filter.is_in_home), turning an
//   alias between complements into equality plus a polarity flip.
// - A "mentions" term naming the current user means "is:mentioned".
// - Direct message operands are sorted the same way the dm predicate
//   sorts them, so "dm:2,3" and "dm:3,2" compare equal.
function normalize(term: NarrowCanonicalTerm): NarrowCanonicalTerm {
    if (term.operator === "in" && term.operand === "home") {
        return {operator: "is", operand: "muted", negated: term.negated !== true};
    }
    if (term.operator === "mentions" && term.operand === people.my_current_user_id()) {
        return {operator: "is", operand: "mentioned", negated: term.negated === true};
    }
    if (term.operator === "dm" || term.operator === "dm-including") {
        return {...term, operand: people.sorted_other_user_ids(term.operand)};
    }
    return term;
}

// Whether a conversation with the "container" recipients includes
// everyone in "contained". Your own id is always included: you are
// part of all of your direct message conversations, even though the
// normalized operands leave you out.
function dm_group_contains(container: number[], contained: number[]): boolean {
    return contained.every((id) => container.includes(id) || people.is_my_user_id(id));
}

function relation_of_normalized(a: NarrowCanonicalTerm, b: NarrowCanonicalTerm): Relation {
    // Terms restricted to different message kinds are disjoint. This
    // also covers pairs of "is:" operands like is:dm and is:resolved.
    const a_kind = message_kind(a);
    const b_kind = message_kind(b);
    if (a_kind !== "any" && b_kind !== "any" && a_kind !== b_kind) {
        return "disjoint";
    }

    if (a.operator === b.operator) {
        switch (a.operator) {
            case "channel":
            case "sender":
            case "id":
                return a.operand === b.operand ? "equal" : "disjoint";
            case "topic":
                // Case-insensitive like the topic predicate. The resolved
                // topic prefix is not stripped: the predicate treats
                // "foo" and "✔ foo" as different topics, so we do too.
                assert(b.operator === "topic");
                return a.operand.toLowerCase() === b.operand.toLowerCase() ? "equal" : "disjoint";
            case "dm":
                assert(b.operator === "dm");
                return util.array_compare(a.operand, b.operand) ? "equal" : "disjoint";
            case "dm-including": {
                // "dm-including:A" matches conversations that include all
                // of A, so requiring a larger set matches fewer messages.
                assert(b.operator === "dm-including");
                const a_in_b = dm_group_contains(b.operand, a.operand);
                const b_in_a = dm_group_contains(a.operand, b.operand);
                if (a_in_b && b_in_a) {
                    return "equal";
                }
                if (b_in_a) {
                    return "subset";
                }
                if (a_in_b) {
                    return "superset";
                }
                return "unknown";
            }
            case "channels":
                if (a.operand === b.operand) {
                    return "equal";
                }
                // Web-public channels are a subset of public channels
                // (see the "channels" predicate). Archived channels can
                // have any privacy, so those pairs stay unknown.
                if (a.operand === "web-public" && b.operand === "public") {
                    return "subset";
                }
                if (a.operand === "public" && b.operand === "web-public") {
                    return "superset";
                }
                return "unknown";
            default:
                // Identical terms are always equal. Different operands of
                // the remaining operators can overlap: a starred message
                // can be mentioned, a message can have both a link and an
                // image, one message can mention two users, and two
                // "date" operands can name the same day ("today" and the
                // date itself).
                return a.operand === b.operand ? "equal" : "unknown";
        }
    }

    // Cross-operator facts, stated in one direction and flipped for
    // the other.
    const forward = cross_operator_relation(a, b);
    if (forward !== "unknown") {
        return forward;
    }
    const backward = cross_operator_relation(b, a);
    // cross_operator_relation only states subset and disjoint facts.
    return backward === "subset" ? "superset" : backward;
}

// Relations where P(a) ⊆ P(b) or the two are disjoint, for specific
// operator pairs.
function cross_operator_relation(a: NarrowCanonicalTerm, b: NarrowCanonicalTerm): Relation {
    if ((a.operator === "dm" || a.operator === "dm-including") && b.operator === "is") {
        return b.operand === "dm" ? "subset" : "unknown";
    }
    if (a.operator === "dm" && b.operator === "dm-including") {
        // "dm:A" is the conversation with exactly A plus yourself, so
        // it includes everyone in B only when B is part of it;
        // otherwise the two can never match the same message.
        assert(Array.isArray(a.operand) && Array.isArray(b.operand));
        return dm_group_contains(a.operand, b.operand) ? "subset" : "disjoint";
    }
    if (a.operator === "channel" && b.operator === "channels") {
        const sub = stream_data.get_sub_by_id_string(a.operand);
        if (sub === undefined) {
            return "unknown";
        }
        // Mirrors the "channels" predicate: "public" includes
        // web-public channels; a channel not in the scope can never
        // match the same message as the scope.
        switch (b.operand) {
            case "public":
                return sub.is_web_public || !sub.invite_only ? "subset" : "disjoint";
            case "web-public":
                return sub.is_web_public ? "subset" : "disjoint";
            case "archived":
                return sub.is_archived ? "subset" : "disjoint";
            default:
                return "unknown";
        }
    }
    return "unknown";
}

export function relation(a: NarrowCanonicalTerm, b: NarrowCanonicalTerm): Relation {
    return relation_of_normalized(normalize(a), normalize(b));
}

// Product rules that aren't derivable from term meaning. A candidate
// is described by its operator, operand, and polarity; the operand
// is undefined for a bare operator suggestion like "channel:". Rules
// only ever key on a plain (not negated) term in the search bar, and
// match the terms as Filter canonicalized them, before this module's
// own normalization, so a rule can name "in".
function policy_blocks(
    bar: NarrowCanonicalTerm,
    operator: NarrowCanonicalOperator,
    operand: string | number | number[] | undefined,
    negated: boolean,
): boolean {
    if (bar.negated === true) {
        return false;
    }
    switch (bar.operator) {
        case "date":
        case "near":
            // "date" and "near" are not combined, and a second "date"
            // isn't offered: with both terms present only "date"
            // takes effect, which would confuse the user. See #38486.
            return operator === "date" || (operator === "near" && bar.operator === "date");
        case "channels":
            // With a "channels:" scope in the bar, adding a second
            // scope or naming one channel from the scope isn't
            // offered: the pill combinations read confusingly, even
            // where they are meaningful. Excluding a scope or a
            // channel is derived, not decided here.
            return (operator === "channels" || operator === "channel") && !negated;
        case "channel":
            // A single channel already pins down its scopes: every
            // "channels:" suggestion next to it would be redundant or
            // could never match. Per term that is derived, but the
            // bare "channels:" operator has no operand yet to derive
            // it from.
            return operator === "channels";
        case "mentions":
            // Only one "mentions" filter at a time. Whether a message
            // can match two of them is unknown (it can mention both
            // users), so this is a choice, not a derivation.
            return operator === "mentions";
        case "in":
            // An "in:" term already scopes the search, so channel
            // scoping and "is:dm" aren't offered next to it.
            return (
                operator === "channel" ||
                operator === "channels" ||
                (operator === "is" && operand === "dm")
            );
        default:
            return false;
    }
}

// Whether to offer a candidate suggestion next to the terms already
// in the search bar. P is the set of messages the bar term's plain
// form matches, Q the candidate's; each term constrains the search
// to its set or, when negated, to the complement. The candidate is
// withheld when its constraint adds nothing to the bar term's
// (duplicate/redundant), or when the two constraints together can
// match nothing (contradiction).
//
// | relation | bar | candidate | withheld?       | example                                    |
// |----------|-----|-----------|-----------------|--------------------------------------------|
// | equal    |  +  |     +     | duplicate       | is:starred -> is:starred                   |
// | equal    |  +  |     -     | contradiction   | is:starred -> -is:starred                  |
// | equal    |  -  |     +     | contradiction   | -is:starred -> is:starred                  |
// | equal    |  -  |     -     | duplicate       | -is:starred -> -is:starred                 |
// | P ⊂ Q    |  +  |     +     | redundant       | channel:X(public) -> channels:public       |
// | P ⊂ Q    |  +  |     -     | contradiction   | channel:X(public) -> -channels:public      |
// | P ⊂ Q    |  -  |   any     | no              | -channel:X -> channels:public              |
// | P ⊃ Q    |  +  |   any     | no              | channels:public -> -channel:X              |
// | P ⊃ Q    |  -  |     +     | contradiction   | -channels:public -> channel:X(public)      |
// | P ⊃ Q    |  -  |     -     | redundant       | -channels:public -> -channel:X(public)     |
// | disjoint |  +  |     +     | contradiction   | topic:a -> topic:b; is:dm -> channel:X     |
// | disjoint |  +  |     -     | redundant       | is:dm -> -channel:X (a no-op)              |
// | disjoint |  -  |   any     | no              | -topic:a -> topic:b                        |
// | unknown  | any |   any     | no              | never suppress without proof               |
export function should_offer(
    candidate: NarrowCanonicalTerm,
    bar_terms: NarrowCanonicalTerm[],
): boolean {
    const candidate_normalized = normalize(candidate);
    const candidate_negated = candidate_normalized.negated === true;
    return !bar_terms.some((bar) => {
        const bar_normalized = normalize(bar);
        const bar_negated = bar_normalized.negated === true;
        switch (relation_of_normalized(bar_normalized, candidate_normalized)) {
            case "equal":
                return true;
            case "subset":
                if (!bar_negated) {
                    return true;
                }
                break;
            case "superset":
                if (bar_negated) {
                    return true;
                }
                break;
            case "disjoint":
                if (!bar_negated) {
                    return true;
                }
                break;
            case "unknown":
                break;
        }
        return policy_blocks(bar, candidate.operator, candidate.operand, candidate_negated);
    });
}

function operator_message_kind(operator: NarrowCanonicalOperator): MessageKind {
    switch (operator) {
        case "channel":
        case "channels":
        case "topic":
            return "channel";
        case "dm":
        case "dm-including":
            return "direct";
        default:
            return "any";
    }
}

// Whether to offer an operator the user hasn't completed with an
// operand yet, like "channel:". Offer it unless every completion
// would be withheld:
// - For a partition operator, a plain term with the same operator in
//   the bar makes every completion a duplicate or a contradiction.
// - A plain bar term restricted to the other message kind makes
//   every completion a contradiction. Only that rule applies here:
//   a specific completion could still narrow the search, so the
//   redundancy rules can't be decided at the operator level.
// - The policy rules apply as-is, with no operand.
// Negated bar terms never withhold an operator: some completion
// (of either polarity) always remains meaningful next to them.
export function should_offer_operator(
    operator: NarrowCanonicalOperator,
    negated: boolean,
    bar_terms: NarrowCanonicalTerm[],
): boolean {
    const kind = operator_message_kind(operator);
    return !bar_terms.some((bar) => {
        if (bar.negated === true) {
            return false;
        }
        if (partition_operators.has(operator) && bar.operator === operator) {
            return true;
        }
        if (kind !== "any") {
            const bar_kind = message_kind(bar);
            if (bar_kind !== "any" && bar_kind !== kind) {
                return true;
            }
        }
        return policy_blocks(bar, operator, undefined, negated);
    });
}
