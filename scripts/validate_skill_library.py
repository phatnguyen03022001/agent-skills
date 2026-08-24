#!/usr/bin/env python3
"""Validate the curated Agent Skills library and reusable task protocol."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = frozenset({
    "architect",
    "executor",
    "research",
    "reuse-first",
    "simplicity",
    "design-review",
    "gap-analysis",
    "adversarial-audit",
    "security-review",
    "verification",
    "debugging",
    "reliability",
    "optimization",
    "github-dev-main-workflow",
    "cloud-run-basics",
})
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CATALOG_ROW_RE = re.compile(r"^\| `([a-z0-9-]+)` \|", re.MULTILINE)
CATALOG_START = "<!-- SKILL_CATALOG_START -->"
CATALOG_END = "<!-- SKILL_CATALOG_END -->"

errors: list[str] = []
warnings: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def warning(message: str) -> None:
    warnings.append(message)


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        error(f"{path.relative_to(ROOT)}: missing opening YAML frontmatter delimiter")
        return {}, text
    try:
        closing = lines.index("---", 1)
    except ValueError:
        error(f"{path.relative_to(ROOT)}: missing closing YAML frontmatter delimiter")
        return {}, text

    metadata: dict[str, str] = {}
    for line_no, raw in enumerate(lines[1:closing], start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1].isspace() or ":" not in raw:
            error(f"{path.relative_to(ROOT)}:{line_no}: unsupported/invalid frontmatter")
            continue
        key, value = raw.split(":", 1)
        key, value = key.strip(), value.strip()
        if not key or not value:
            error(f"{path.relative_to(ROOT)}:{line_no}: empty frontmatter key/value")
            continue
        if key in metadata:
            error(f"{path.relative_to(ROOT)}:{line_no}: duplicate frontmatter key '{key}'")
            continue
        if value[0] in "[{|>" or value.startswith("-"):
            error(f"{path.relative_to(ROOT)}:{line_no}: unsupported frontmatter value syntax for '{key}'")
            continue
        metadata[key] = value.strip("\"'")
    return metadata, text


def validate_links(path: Path, text: str) -> None:
    for target in LINK_RE.findall(text):
        target = target.strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            error(f"{path.relative_to(ROOT)}: internal link escapes repository: {target}")
            continue
        if not resolved.exists():
            error(f"{path.relative_to(ROOT)}: broken internal link: {target}")


def require_tokens(path: Path, tokens: list[str]) -> None:
    if not path.is_file():
        error(f"missing required protocol file: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            error(f"{path.relative_to(ROOT)}: missing required field/token '{token}'")
    validate_links(path, text)


def validate_readme_catalog() -> None:
    path = ROOT / "README.md"
    if not path.is_file():
        error("missing README.md")
        return
    text = path.read_text(encoding="utf-8")
    if text.count(CATALOG_START) != 1 or text.count(CATALOG_END) != 1:
        error("README.md: skill catalog markers must each appear exactly once")
        validate_links(path, text)
        return
    section = text.split(CATALOG_START, 1)[1].split(CATALOG_END, 1)[0]
    names = CATALOG_ROW_RE.findall(section)
    if len(names) != len(set(names)):
        error("README.md: duplicate skill in catalog")
    if set(names) != EXPECTED_SKILLS:
        error(
            "README.md: catalog does not match curated skill set; "
            f"missing={sorted(EXPECTED_SKILLS - set(names))} "
            f"unexpected={sorted(set(names) - EXPECTED_SKILLS)}"
        )
    validate_links(path, text)


def validate_protocol_files() -> None:
    require_tokens(ROOT / "templates" / "task.yaml", [
        "protocol_version:", "task_id:", "task_revision:", "state:",
        "architect_binding:", "target_repository:", "target:", "task_path:",
        "execution_base:", "mode: handoff_snapshot", "skill_library:", "revision:",
        "architect_analysis_skills:", "execution_skills:", "required:", "recommended:",
        "external_skills:", "authority_sources:", "structure_authority:", "objective:",
        "scope:", "invariants:", "forbidden_changes:", "gap_policy:",
        "local_auto_fix:", "dependency_change: revised_contract_required",
        "public_contract_change: revised_contract_required", "blocking_gap_behavior: BLOCKED",
        "structure_policy:", "expected_new_files:", "unlisted_new_files:",
        "allow_new_top_level_directories:", "allow_new_shared_modules:",
        "acceptance_criteria:", "verification:", "pre_execution_checks:",
        "git_authority:", "promote_to_main:", "blocking_decisions:", "execution_ready:",
    ])
    require_tokens(ROOT / "templates" / "report.yaml", [
        "task_id:", "task_revision:", "report_revision:", "state: REPORTED",
        "task_locator:", "authorized_base_head:", "final_execution_head:",
        "authorized_revision:", "observed_revision:", "execution_skills_used:",
        "changed_files:", "structure_authorized:", "acceptance_evidence:",
        "executor_checks:", "authoritative_verification:", "discovered_gaps:",
        "classification:", "blocks_current_task:", "structural_observations:",
        "deviations_from_task:", "blockers:", "result:",
    ])
    require_tokens(ROOT / "templates" / "review.yaml", [
        "task_id:", "task_revision:", "review_revision:", "reviewed_report:",
        "commit:", "contract_compliance:", "execution_base:", "skill_rules:",
        "scope:", "structure_policy:", "git_authority:", "acceptance_criteria:",
        "gap_disposition:", "follow_up_tasks:", "promotion_readiness:",
    ])
    require_tokens(ROOT / "protocols" / "TASK_PROTOCOL.md", [
        "NEW_ARCHITECT_SESSION_REQUIRED", "One Executor session", ".agent/tasks/",
        "DRAFT", "READY", "EXECUTING", "REPORTED", "ACCEPTED", "BLOCKED",
        "REVISION_REQUIRED", "handoff_snapshot", "EXECUTOR_HANDOFF", "LOCAL",
        "FOLLOW_UP", "No orphan source files", "No speculative scale structure",
    ])
    for path in [
        ROOT / "contracts" / "IMPLEMENTATION_CONTRACT.md",
        ROOT / "contracts" / "IMPLEMENTATION_REPORT.md",
        ROOT / "contracts" / "ARCHITECT_REVIEW.md",
    ]:
        require_tokens(path, ["template"])


def main() -> int:
    skill_files = sorted(path for path in ROOT.glob("*/SKILL.md") if path.parent.parent == ROOT)
    actual_folders = {path.parent.name for path in skill_files}
    if actual_folders != EXPECTED_SKILLS:
        error(
            "curated skill set mismatch; "
            f"missing={sorted(EXPECTED_SKILLS - actual_folders)} "
            f"unexpected={sorted(actual_folders - EXPECTED_SKILLS)}"
        )

    seen_names: dict[str, Path] = {}
    print("Skill word counts:")
    for path in skill_files:
        metadata, text = parse_frontmatter(path)
        rel = path.relative_to(ROOT)
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        folder = path.parent.name

        if not name:
            error(f"{rel}: missing frontmatter name")
        else:
            if len(name) > 64:
                error(f"{rel}: skill name exceeds 64 characters")
            if not NAME_RE.fullmatch(name):
                error(f"{rel}: invalid skill name '{name}'")
            if name != folder:
                error(f"{rel}: skill name '{name}' must match folder '{folder}'")
            if name in seen_names:
                error(f"duplicate skill name '{name}': {seen_names[name]} and {rel}")
            else:
                seen_names[name] = rel

        if not description:
            error(f"{rel}: missing frontmatter description")
        elif not description.startswith("Use when"):
            error(f"{rel}: description must begin with 'Use when'")
        if len(description) > 1024:
            error(f"{rel}: description exceeds 1024 characters")

        body = text.split("---", 2)[-1] if text.startswith("---") else text
        word_count = len(re.findall(r"\b[\w'-]+\b", body, flags=re.UNICODE))
        line_count = len(text.splitlines())
        print(f"  {folder}: {word_count} words, {line_count} lines")
        if word_count > 800:
            warning(f"{rel}: {word_count} words; consider moving heavy detail to references/")
        if line_count > 500:
            warning(f"{rel}: {line_count} lines; Agent Skills recommends keeping SKILL.md under 500 lines")
        validate_links(path, text)

    if set(seen_names) != EXPECTED_SKILLS:
        error("frontmatter names do not match curated skill set")

    validate_readme_catalog()
    validate_protocol_files()

    for path in ROOT.rglob("*.md"):
        validate_links(path, path.read_text(encoding="utf-8"))

    if warnings:
        print("\nWarnings:")
        for message in warnings:
            print(f"  WARN: {message}")
    if errors:
        print("\nErrors:", file=sys.stderr)
        for message in errors:
            print(f"  ERROR: {message}", file=sys.stderr)
        return 1

    print("\nOK: validated curated 15-skill taxonomy and task protocol")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
