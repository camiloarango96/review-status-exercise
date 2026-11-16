# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A take-home exercise: build a `review-status <submission_id> [--as-of YYYY-MM-DD] [--json]` CLI that reports where one benchmark submission stands in peer review. [README.md](README.md) is the full spec (data model, stage rules, penalty thresholds, JSON shape). The tool does not exist yet. The root `review-status` executable is still to be written, and the Actions run on `main` fails until it is.

## Commands

- Run all checks: `pytest -v tests` (CI installs pytest on Python 3.12 and runs this on every push)
- Run one check: `pytest -v tests/test_review_status.py::test_s1_penalty_stage`
- CI runs `bash build.sh` first if the file exists. Only add one if the chosen language needs a build.
- Checks need network access, because the tool reads the live Supabase REST API (`/rest/v1/{submissions,users,orgs}`, `apikey` header). The URL and publishable key are in README.md.

## Rule: don't assume, raise it

If something is unclear (the spec, the data, or an edge case), stop and raise the issue with the user, stating your proposed assumption and why. Don't silently pick an interpretation. Only record a decision in [NOTES.md](NOTES.md) and the spec after the user has confirmed it.

## Workflow: spec-driven, then test-driven

Work spec-first. [README.md](README.md) is the source requirement. Before coding, write a `SPEC.md` that turns it into precise, testable rules: inputs, outputs, stage and window computation, waiting-on mapping, penalty thresholds, error behavior and exit codes. Resolve each ambiguity in the spec and mirror the decision, its reason and how it was checked in [NOTES.md](NOTES.md). Every test and every piece of code should trace back to a spec rule. If behavior needs to change, update `SPEC.md` first, then the tests, then the code. Don't let the code drift ahead of the spec.

### Test-driven

Work test-first. Before writing or changing any code, run the relevant failing check in `tests/` and confirm it fails for the expected reason. Then write the minimum code to make it pass, re-run, and build on that. For behavior the provided checks don't cover (CSV quirks, weekday counting, edge dates), add a failing test of your own first, outside `tests/`, for example in a separate `unit_tests/` directory.

## Constraints

- Do not edit `tests/` or `.github/`.
- `review-status` must be executable at the repo root (`git update-index --chmod=+x review-status`). It must run on ubuntu-latest. A stdlib-only script avoids a build step.
- The tests call `./review-status <id> --as-of 2026-11-16 --json` and check these JSON keys: `submission_id`, `status`, `submitter`, `org`, `reviewers[{user_id, org, confirmed, filed}]`, `stage`, `peer_review_closes`, `objection_resolution_closes`, `waiting_on`, `penalty_stage`. An unknown submission id must exit non-zero.
- The tests pin specific submission UUIDs (S1, S2, S3, S6) to expected stages, dates and penalty stages. Check these against live data when changing date logic.

## Architecture

Two data sources must be joined per submission:
- **Supabase** (read-only): `submissions` (status, `peer_review_started_at`, confirmed and unconfirmed reviewer id arrays, submitter `user_id`), `users` (maps a user to an org), `orgs` (display names).
- **`reviews.csv`** in the repo: one row per finding, kept by hand, so expect messy data. Findings are keyed by `submission_id`. `review_state` decides who a finding is waiting on: `awaiting_first_response` and `needs_submitter_reply` mean the submitter, `needs_reviewer_reply` means the reviewer in `reviewed_by`, and `resolved` means nobody.

Derived logic:
- Stage windows are computed from `peer_review_started_at`: peer review closes at +21 days and objection resolution at +42 days, each at 11:59 PM US Pacific. Output is the Pacific calendar date. Use real `America/Los_Angeles` handling, because DST changes in early November.
- Stage and dates are `null` unless `status == REVIEW_PENDING`.
- Penalty stage comes from weekdays that findings have been waiting on the submitter, relative to `--as-of`: 3 gives stage 1, 6 gives stage 2, 10 gives stage 3. Report the highest, or 0.

## NOTES.md

The README requires each ambiguous decision (timezone edges, CSV data quirks, weekday counting, "filed" semantics) to be recorded in [NOTES.md](NOTES.md). Record what was decided, why, and how it was checked.
