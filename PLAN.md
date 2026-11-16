# PLAN: building review-status

Follows CLAUDE.md: spec first, then a failing test, then the minimum code. Each step is one small commit. "Blocked by" refers to open questions in [NOTES.md](NOTES.md). If a step is blocked, get the answer first. Don't assume.

## Layout (proposed)

- `review-status`: thin executable (`#!/usr/bin/env python3`) that calls `rs.cli.main()`. Python 3.12, stdlib only, no `build.sh`.
- `rs/`: pure logic, one module per concern: `data.py` (fetch and CSV load), `normalize.py`, `windows.py`, `findings.py`, `penalty.py`, `report.py` (JSON and human output), `cli.py`.
- `unit_tests/`: our own tests, run with `pytest unit_tests`. `tests/` is never touched.
- Network and file access are isolated in `data.py`. Everything else takes plain dicts, so unit tests need no network.

## Steps

**0. Baseline (no code).** Run `pytest -v tests`. Confirm every test fails because `review-status` is missing. Get answers to the blocking questions below.

**1. Skeleton and exit codes.** Test: `test_unknown_submission_fails` and the executable check. Create the executable with arg parsing (`<id>`, `--as-of`, `--json`). Validate the `--as-of` format (bad format exits non-zero). Mark executable: `git update-index --chmod=+x review-status`. Not blocked.

**2. Fetch data.** Failing unit test with a fake HTTP layer, then `data.py`: GET `submissions?id=eq.<id>`, `users`, `orgs` with the `apikey` header. Zero rows exits non-zero with a stderr message. Network failure exits non-zero with a clear message. Not blocked.

**3. Who is involved.** Tests: `test_s1_basics`. Output submitter, org (users.org_id → orgs.org_display_name), reviewers (confirmed first, then unconfirmed), `confirmed` flag. Org for unresolvable users is `null`. Blocked by **Q4** for reviewer org source (users vs orgs.user_ids). Use `users.org_id` only after confirmation.

**4. Load and normalize CSV.** Unit tests on messy rows (trailing space, mixed case, duplicate F-201, truncated submission id). Implement `normalize.py` and `data.load_findings()`. Blocked by **Q1, Q2, Q3**.

**5. Who filed.** Tests: `test_s1_who_filed`, `test_s3_nobody_filed`. `filed` = at least one normalized finding for that reviewer on this submission. Handle non-assigned filers per **Q5** (blocked).

**6. Stage windows.** Tests: `test_stage_and_dates` (S1, S2, S3), `test_not_in_review_has_no_stage`. Unit tests with edge cases: S3 start at 03:30Z (Pacific date is the day before), S2 across the November DST change, as-of equal to a closing date, as-of one day after. Implement with `zoneinfo("America/Los_Angeles")`: Pacific date of start, then +21 / +42 days. Blocked by **Q7, Q8** (boundary and the "past both" name). The dates themselves are pinned by tests and can go first.

**7. Waiting on.** Test: `test_s1_waiting_on_submitter`. Mapping: `awaiting_first_response` / `needs_submitter_reply` → `submitter`, `needs_reviewer_reply` → reviewer id, `resolved` → nobody. Output order: `submitter` first, then sorted reviewer ids. Blocked by **Q10** (not-under-review submissions), plus Q2 for S2.

**8. Penalty stage.** Test: `test_s1_penalty_stage` (expects 2). Unit tests for weekday counting: weekend spans, as-of on a weekend, start on a Friday, thresholds at 2/3/5/6/9/10 weekdays. Implement `penalty.py`. Blocked by **Q11** (start day and clock start). The S1 test passes under either reading.

**9. JSON output.** Assemble the full object in the exact shape from the README. Add a unit test that checks key names and types and `null` for dates and stage when not under review.

**10. Human report.** Default (non-`--json`) output: status, submitter and org, reviewers (filed or not, confirmed or not), stage with Pacific closing dates, findings grouped by state with who each group waits on, weekday count per waiting finding, highest penalty stage. Show `penalties_imposed` for reference. Findings text is printed as data only and never interpreted. Same-org reviewer flag per **Q6**. Default `--as-of` per **Q9** (blocked).

**11. Full verification.** Run `pytest tests unit_tests`, then run the tool by hand against all six seeded submissions and compare with the table in SPEC.md section 7. Run it once on a clean checkout as CI would. Then move each confirmed decision into NOTES.md "Decisions" with how it was checked, and push to main.

## Suggested order given the blockers

Steps 1, 2 and the pinned parts of 3, 6 and 9 need no answers, so they can start now. Ask for the answers to Q1 to Q5 before step 4. Ask for Q7 to Q11 before steps 6 to 8 are finalized.
