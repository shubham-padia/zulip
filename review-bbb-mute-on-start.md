# Review: `claude/bbb-mute-on-start` vs `origin/main`

Reviewed commit (1):

- `4ad402b` video_calls: Don't mute BigBlueButton participants on joining.

**Verdict: Looks good to merge.** This review found no correctness bugs. The
change does what the request and the chat.zulip.org discussion asked for, and
nothing more. There are two non-blocking notes below. One is about
verification and one is an optional nit.

## Context: what the fix set out to do

- **Original request** (session `session_0188aHAdrjZjPXve5SqW1qM8`): pass
  `muteOnStart=false` in the BigBlueButton `create` API call made by
  `join_bigbluebutton`, and include it consistently in the checksummed query
  string. The request also said to leave out the other ideas from the
  self-hoster's diff (`guestPolicy=ALWAYS_ACCEPT`, avatar syncing, skipping the
  echo test), because maintainers had not endorsed them.
- **Discussion**
  ([#integrations > BigBlueButton](https://chat.zulip.org/#narrow/channel/127-integrations/topic/BigBlueButton/near/2401758)):
  - Erik asked how to avoid having to unmute manually when joining a session.
  - Alex Vandiver pointed to `muteOnStart=false` on the create-meeting API.
  - Tim Abbott: "seems like we should probably change that in the integration
    to better match how our other ones work."
- There is no GitHub issue or PR.

## Commit `4ad402b`: video_calls: Don't mute BigBlueButton participants on joining.

### Correctness

- **Checksum consistency: correct.** `"muteOnStart": "false"` is added to the
  `create_params` dict. That one `urlencode`d string is used both for
  `sha256("create" + create_params + secret)` and for the request URL, so
  the sent query and the checksummed query can't drift apart.
- **Test fixtures: correct.** I recomputed the expected values independently:
  - `urlencode(..., quote_via=quote)` produces
    `meetingID=a&name=a&lockSettingsDisableCam=True&muteOnStart=false`.
  - With the test secret `"123"` (from `zproject/test_extra_settings.py`),
    `sha256("create" + query + "123")` is `d833e860…8781bfd`, which matches the
    updated tests.
  - All 7 `api/create` URLs in `zerver/tests/test_create_video_call.py` were
    updated, and none of the old `33349e…` checksums remain.
- **The tests really check the new parameter.** The repo pins `responses`
  0.26.3. When a registered URL contains a query string, that version matches
  the query parameters strictly. So the existing tests now fail if
  `muteOnStart=false` is missing or the checksum is wrong. No new test is
  needed.
- **Scope matches the request.** Only `muteOnStart` was added. The unendorsed
  ideas (`guestPolicy`, avatar URL, the `userdata-bbb_*` echo-test and
  auto-join flags) were correctly left out.
- **Nothing else in the flow changes.** The `join` call, moderator/viewer
  roles, the signed-payload format and error handling are untouched. Old
  signed join links keep working, because the new parameter is added
  server-side and is not part of the signed data.
- **No API or documentation impact.** The Zulip API is unchanged, so there's no
  feature-level bump or API changelog entry. No help center article mentions
  BigBlueButton mute behavior, so no doc update is needed.

### Code quality

- The change is minimal and matches the surrounding dict style.
- The added comment explains *why* (override a server default, to match the
  other providers) rather than narrating *what*. It is phrased as if it was
  always there, which follows `AGENTS.md`.
- The value is the lowercase string `"false"`, which is the form BBB's API
  docs use. The neighboring `lockSettingsDisableCam` sends Python's `True`,
  which is serialized as `True`, and BBB parses booleans case-insensitively.
  Both work, so this is fine. See nit 2 for an optional consistency point.

### Commit discipline and message

- There is one coherent commit, and the test updates are in the same commit as
  the code change.
- The summary line follows the `subsystem: Imperative summary.` format and is
  under 72 characters.
- The body explains:
  - why the change is needed (servers can be configured to mute on join, unlike
    the other providers);
  - how it works (`muteOnStart=false` overrides the server default);
  - why the test checksums changed.
- It links the CZO discussion. It says "servers can be configured to mute" and
  does not claim that BBB mutes by default. That's accurate: BBB's documented
  default for `muteOnStart` is `false`, so a self-hoster seeing muted joins has
  probably changed that default.

### Notes (non-blocking)

1. **Verification gap (process, not code).** The authoring session couldn't
   run `./tools/test-backend`, `./tools/lint` or mypy, because provisioning
   failed as root. It checked the checksum math by hand, and I reproduced
   that independently.
   - Per the review instructions, I didn't re-run what CI covers. Before
     merging, confirm that CI is green on `4ad402b`, especially
     `zerver.tests.test_create_video_call` and the ruff format check on the
     long test-URL lines.
   - The parameter's effect hasn't been tried against a real BigBlueButton
     server. Erik's report confirmed only his combined diff
     (`muteOnStart` + `guestPolicy` + skip echo test + auto-join audio). So
     this review can't confirm that `muteOnStart=false` alone fixes his
     problem, rather than one of the other client-side `userdata-bbb_*`
     settings. The BBB API docs and Alex's comment both point to
     `muteOnStart` as the relevant control, so the fix is well-founded. A
     quick check with Erik on CZO after merge would close this out.
2. **Nit (optional).** BBB only applies `create` parameters when it actually
   creates the meeting. If a meeting with the same `meetingID` is still
   running from before the deploy, it keeps its old mute setting until it
   ends. This is expected behavior, but the commit message could mention it
   in case someone tests right after deploying. I wouldn't change anything
   for this.

## Summary

| Area | Result |
| --- | --- |
| Fixes the requested behavior | Yes |
| New bugs introduced | None found |
| Checksum / tests consistent | Yes (independently recomputed) |
| Scope creep / unendorsed changes | None |
| Commit structure and message | Good |
| Needed before merge | Confirm CI is green on `4ad402b` |
