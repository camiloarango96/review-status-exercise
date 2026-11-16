# Notes

For each call you make: what you decided, why, and how you checked it.

## Open questions

Unanswered. Each becomes a decision (what, why, how checked) once confirmed. Q-numbers are referenced from [SPEC.md](SPEC.md).

1. **CSV normalization.** Is trimming and lowercasing user ids acceptable, or should dirty values be reported as data errors?
2. **Duplicate finding F-201** (submission 8d42e6b1): two rows with different states. One is `needs_submitter_reply` (last reply 10-28), the other `needs_reviewer_reply` (last reply 11-13). Proposal: the row with the latest reply wins, so it waits on the reviewer. Alternative: treat the stale row as authoritative, which makes it a stage 3 penalty. Also: should the tool warn about duplicates?
3. **Submission id and submitter mismatches in CSV.** (a) Rows for 8d42e6b1 use a truncated id; proposal: match unique prefixes. Alternative: exact match only, in which case S2 findings are lost. (b) F-501 on e6a3c8f2 lists `sub_jammy`, but the database says `sub_jammy_2`. Proposal: database wins, CSV `submitter_id` is ignored.
4. **rev_noble_2's org.** `users.org_id` says Noble Compute, but `orgs.user_ids` lists them under Lunar Silicon and omits them from Noble. Proposal: `users.org_id` is the source of truth. Alternative: `orgs.user_ids`.
5. **Non-assigned filers** (`chair_ada` with no org, `rev_old_7` who is not a user at all): list separately and exclude from `reviewers`, or add to `reviewers`? Should a `needs_reviewer_reply` finding from such a filer appear in `waiting_on`? Proposal: yes, it is still waiting on that id.
6. **Same-org reviewer** (`rev_jammy_1` on a Jammy submission): flag as a possible conflict only in the human report, or not at all?
7. **Close-day boundary.** Is `--as-of` equal to the closing date still inside that window? Proposal: yes.
8. **Third stage name** for "past both" in JSON. Proposal: `closed`. The README leaves it open.
9. **Default `--as-of`.** Proposal: today's date in Pacific time, not the machine's local or UTC date.
10. **`waiting_on` for not-under-review submissions** (e.g. withdrawn with open findings). Proposal: `[]`, consistent with `penalty_stage` 0.
11. **Weekday counting start.** Proposal as in section 5: start from `last_reply_at`, fall back to `opened_at`, exclude the start day, include the as-of day, Pacific dates, no holidays. Also: should a reply by the submitter reset the clock? (Not relevant when state says waiting on the submitter, since the last reply is then from the reviewer.)

## Decisions

_None confirmed yet._
