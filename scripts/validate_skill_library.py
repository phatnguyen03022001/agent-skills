#!/usr/bin/env python3
"""Validate the curated, flat Agent Skills library using only the Python stdlib."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILL_COUNT = 15
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

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
            error(
                f"{path.relative_to(ROOT)}:{line_no}: unsupported/invalid frontmatter; "
                "use simple top-level 'key: value' fields"
            )
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            error(f"{path.relative_to(ROOT)}:{line_no}: empty frontmatter key/value")
            continue
        if key in metadata:
            error(f"{path.relative_to(ROOT)}:{line_no}: duplicate frontmatter key '{key}'")
            continue
        if value[0] in "[{|>" or value.startswith("-"):
            error(
                f"{path.relative_to(ROOT)}:{line_no}: unsupported frontmatter value syntax for '{key}'"
            )
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


def validate_contracts() -> None:
    required_contract_tokens = [
        "full_name:", "branch:", "name:", "role:", "base_head:",
        "required_skills:", "recommended_skills:", "invariants:",
        "forbidden_changes:", "acceptance_criteria:", "executor_checks:",
        "authoritative_verification:", "commit:", "push:",
        "promote_to_main:", "stale_contract_behavior:", "execution_ready:",
    ]
    required_report_tokens = [
        "full_name:", "branch:", "base_head:", "pre_execution_head:",
        "final_head:", "skills_used:", "changed_files:", "commits_created:",
        "pushed:", "promoted_to_main:", "acceptance_evidence:",
        "executor_checks:", "authoritative_verification:", "result:",
    ]
    checks = [
        (ROOT / "contracts" / "IMPLEMENTATION_CONTRACT.md", required_contract_tokens),
        (ROOT / "contracts" / "IMPLEMENTATION_REPORT.md", required_report_tokens),
    ]
    for path, tokens in checks:
        if not path.is_file():
            error(f"missing required contract file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                error(f"{path.relative_to(ROOT)}: missing structural field '{token}'")
        validate_links(path, text)


def main() -> int:
    skill_files = sorted(path for path in ROOT.glob("*/SKILL.md") if path.parent.parent == ROOT)
    if len(skill_files) != EXPECTED_SKILL_COUNT:
        error(
            f"expected exactly {EXPECTED_SKILL_COUNT} discoverable top-level skills; "
            f"found {len(skill_files)}"
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
        elif not NAME_RE.fullmatch(name):
            error(f"{rel}: invalid skill name '{name}'")
        elif name != folder:
            error(f"{rel}: skill name '{name}' must match folder '{folder}'")

        if name:
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

    validate_contracts()
    readme = ROOT / "README.md"
    if not readme.is_file():
        error("missing README.md")
    else:
        validate_links(readme, readme.read_text(encoding="utf-8"))

    if warnings:
        print("\nWarnings:")
        for message in warnings:
            print(f"  WARN: {message}")
    if errors:
        print("\nErrors:", file=sys.stderr)
        for message in errors:
            print(f"  ERROR: {message}", file=sys.stderr)
        return 1

    print(f"\nOK: validated exactly {EXPECTED_SKILL_COUNT} unique skills and contract structure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
