---
name: github-dev-main-workflow
description: Use when a repository follows a dev/main branch model and a task may read or write GitHub state, commit, push, promote changes, create refs, or trigger GitHub Actions.
---

# GitHub Dev/Main Workflow

`dev` is the normal integration/mutation branch. `main` is stable source of truth. Do not add long-lived branches or PRs, implement on `main`, force-push, or rewrite history unless explicitly required.

Before any write, refresh and confirm exact `owner/repo`, target branch, remote HEAD, expected base HEAD, scope/write authority, and possible Actions/paid-infrastructure triggers. A new chat must not mutate without exact repo + branch + base HEAD. If remote state moved, stop and reassess.

Read current file/blob before replacement. Keep commits atomic and scoped. Commit/push only when authorized.

Promotion `dev -> main` requires refreshed heads, required project verification on the intended SHA, explicit promotion authority, and no unexpected divergence. Delegated workers default to `dev` mutation only.

Before push/merge/rerun/dispatch, inspect workflow triggers, runner/matrix fan-out, caches/artifacts, and cost risk when available. Do not create/broaden/rerun Actions or enable paid/unknown-cost features for convenience. Verify current billing rules when cost matters. Prefer allowed repository-native/local verification when sufficient.

Git success, CI success, contract compliance, and authoritative project PASS are separate.
