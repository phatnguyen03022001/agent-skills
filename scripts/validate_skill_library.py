#!/usr/bin/env python3
"""Validate the curated Agent Skills library and reusable task protocol."""

from __future__ import annotations

from dataclasses import dataclass
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_PROTOCOL_VERSION = 3
EXPECTED_SKILLS = frozenset({
    "architect", "executor", "research", "reuse-first", "simplicity",
    "design-review", "gap-analysis", "adversarial-audit", "security-review",
    "verification", "debugging", "reliability", "optimization",
    "github-dev-main-workflow", "cloud-run-basics",
})
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CATALOG_ROW_RE = re.compile(r"^\| `([a-z0-9-]+)` \|", re.MULTILINE)
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$")
INT_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
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


@dataclass(frozen=True)
class YamlLine:
    number: int
    indent: int
    text: str


class ProtocolYamlError(ValueError):
    pass


def strip_yaml_comment(raw: str) -> str:
    single = double = escaped = False
    for index, char in enumerate(raw):
        if escaped:
            escaped = False
        elif char == "\\" and double:
            escaped = True
        elif char == "'" and not double:
            single = not single
        elif char == '"' and not single:
            double = not double
        elif char == "#" and not single and not double:
            return raw[:index]
    return raw


def preprocess_yaml(path: Path) -> list[YamlLine]:
    lines: list[YamlLine] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "\t" in raw:
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: tabs are not supported")
        raw = strip_yaml_comment(raw).rstrip()
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ProtocolYamlError(
                f"{path.relative_to(ROOT)}:{number}: indentation must use two-space steps"
            )
        lines.append(YamlLine(number, indent, raw[indent:]))
    if not lines:
        raise ProtocolYamlError(f"{path.relative_to(ROOT)}: empty YAML document")
    if lines[0].indent:
        raise ProtocolYamlError(
            f"{path.relative_to(ROOT)}:{lines[0].number}: top-level content must start at column 1"
        )
    return lines


def scalar_value(raw: str, path: Path, number: int) -> Any:
    raw = raw.strip()
    if raw == "[]":
        return []
    if raw == "{}":
        return {}
    if raw in ("true", "false"):
        return raw == "true"
    if raw in ("null", "~"):
        return None
    if INT_RE.fullmatch(raw):
        return int(raw)
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    if raw.startswith(("[", "{", "|", ">")):
        raise ProtocolYamlError(
            f"{path.relative_to(ROOT)}:{number}: unsupported YAML value syntax"
        )
    return raw


def split_mapping(line: YamlLine, path: Path) -> tuple[str, str]:
    match = KEY_RE.match(line.text)
    if not match:
        raise ProtocolYamlError(
            f"{path.relative_to(ROOT)}:{line.number}: expected mapping key"
        )
    return match.group(1), match.group(2).strip()


def skip_sequence(
    lines: list[YamlLine], index: int, indent: int, path: Path
) -> int:
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            return index
        if line.indent == indent and not line.text.startswith("-"):
            return index
        if line.indent == indent and line.text == "-":
            raise ProtocolYamlError(
                f"{path.relative_to(ROOT)}:{line.number}: empty sequence item is unsupported"
            )
        index += 1
    return index


def scan_mapping(
    lines: list[YamlLine],
    index: int,
    indent: int,
    prefix: str,
    path: Path,
    fields: dict[str, Any],
) -> int:
    keys: set[str] = set()
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            return index
        if line.indent > indent:
            raise ProtocolYamlError(
                f"{path.relative_to(ROOT)}:{line.number}: unexpected indentation"
            )
        if line.text.startswith("-"):
            return index

        key, raw_value = split_mapping(line, path)
        if key in keys:
            raise ProtocolYamlError(
                f"{path.relative_to(ROOT)}:{line.number}: duplicate mapping key '{key}'"
            )
        keys.add(key)
        dotted = f"{prefix}.{key}" if prefix else key
        index += 1

        if raw_value:
            fields[dotted] = scalar_value(raw_value, path, line.number)
            if index < len(lines) and lines[index].indent > indent:
                raise ProtocolYamlError(
                    f"{path.relative_to(ROOT)}:{lines[index].number}: "
                    f"scalar '{dotted}' cannot have nested content"
                )
            continue

        if index >= len(lines) or lines[index].indent <= indent:
            fields[dotted] = None
            continue
        if lines[index].indent != indent + 2:
            raise ProtocolYamlError(
                f"{path.relative_to(ROOT)}:{lines[index].number}: "
                f"nested content for '{dotted}' must indent by two spaces"
            )
        if lines[index].text.startswith("-"):
            fields[dotted] = []
            index = skip_sequence(lines, index, indent + 2, path)
        else:
            fields[dotted] = {}
            index = scan_mapping(lines, index, indent + 2, dotted, path, fields)
    return index


def load_protocol_fields(relative_path: str) -> dict[str, Any] | None:
    path = ROOT / relative_path
    if not path.is_file():
        error(f"missing required protocol template: {relative_path}")
        return None
    try:
        lines = preprocess_yaml(path)
        if lines[0].text.startswith("-"):
            raise ProtocolYamlError(
                f"{relative_path}:{lines[0].number}: top-level document must be a mapping"
            )
        fields: dict[str, Any] = {}
        index = scan_mapping(lines, 0, 0, "", path, fields)
        if index != len(lines):
            line = lines[index]
            raise ProtocolYamlError(
                f"{relative_path}:{line.number}: unexpected content or indentation"
            )
    except ProtocolYamlError as exc:
        error(str(exc))
        return None
    return fields


_MISSING = object()


def require_field(
    label: str,
    fields: dict[str, Any],
    dotted: str,
    expected_type: type,
    expected_value: Any = _MISSING,
) -> None:
    if dotted not in fields:
        error(f"{label}: missing required path '{dotted}'")
        return
    value = fields[dotted]
    if type(value) is not expected_type:
        error(
            f"{label}: path '{dotted}' must be {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )
        return
    if expected_value is not _MISSING and value != expected_value:
        error(f"{label}: path '{dotted}' must equal {expected_value!r}, got {value!r}")


def validate_version(label: str, fields: dict[str, Any]) -> None:
    require_field(
        label, fields, "protocol_version", int, SUPPORTED_PROTOCOL_VERSION
    )


def validate_task_template() -> None:
    label = "templates/task.yaml"
    fields = load_protocol_fields(label)
    if fields is None:
        return
    validate_version(label, fields)
    required = [
        ("task_id", str), ("task_revision", int),
        ("architect_binding.target_repository", str), ("target.repository", str),
        ("target.branch.name", str),
        ("skill_library.repository", str), ("skill_library.revision", str),
        ("execution_skills.required", list), ("execution_skills.recommended", list),
        ("structure_authority.status", str), ("structure_authority.source", str),
        ("structure_authority.rationale", str), ("gap_policy.local_auto_fix", bool),
        ("structure_policy.expected_new_files", list),
        ("git_authority.promote_to_main", bool), ("execution_ready", bool),
    ]
    for dotted, expected_type in required:
        require_field(label, fields, dotted, expected_type)
    require_field(label, fields, "execution_base.mode", str, "handoff_snapshot")
    require_field(label, fields, "gap_policy.blocking_gap_behavior", str, "BLOCKED")

    bound = fields.get("architect_binding.target_repository", _MISSING)
    target = fields.get("target.repository", _MISSING)
    if bound is not _MISSING and target is not _MISSING and bound != target:
        error(f"{label}: architect binding must equal target repository")

    status = fields.get("structure_authority.status", _MISSING)
    source = fields.get("structure_authority.source", _MISSING)
    rationale = fields.get("structure_authority.rationale", _MISSING)
    ready = fields.get("execution_ready", _MISSING)
    if status is not _MISSING and status not in {"RESOLVED", "NOT_APPLICABLE", "UNRESOLVED"}:
        error(f"{label}: unsupported structure_authority.status {status!r}")
    if status == "RESOLVED" and not source:
        error(f"{label}: RESOLVED structure authority requires non-empty source")
    if status == "NOT_APPLICABLE" and not rationale:
        error(f"{label}: NOT_APPLICABLE structure authority requires non-empty rationale")
    if status == "UNRESOLVED" and ready is True:
        error(f"{label}: UNRESOLVED structure authority cannot be execution-ready")


def validate_handoff_template() -> None:
    label = "templates/handoff.yaml"
    fields = load_protocol_fields(label)
    if fields is None:
        return
    validate_version(label, fields)
    for dotted, expected_type in [
        ("handoff_type", str), ("task.id", str), ("task.revision", int),
        ("task.path", str), ("target.repository", str), ("target.branch", str),
        ("target.base_head", str),
    ]:
        require_field(label, fields, dotted, expected_type)
    require_field(label, fields, "handoff_type", str, "EXECUTOR")


def validate_report_template() -> None:
    label = "templates/report.yaml"
    fields = load_protocol_fields(label)
    if fields is None:
        return
    validate_version(label, fields)
    for dotted, expected_type in [
        ("task_id", str), ("task_revision", int), ("report_revision", int),
        ("state", str), ("task_source.path", str), ("execution.repository", str),
        ("execution.branch.name", str), ("execution.authorized_base_head", str),
        ("execution.pre_execution_head", str), ("execution.final_execution_head", str),
        ("skill_library.authorized_revision", str),
        ("skill_library.observed_revision", str),
        ("execution_skills_used.required", list),
        ("pre_execution_checks.protocol_version_supported", bool),
        ("pre_execution_checks.task_at_base_confirmed", bool),
        ("changed_files", list), ("acceptance_evidence", list),
        ("executor_checks", list), ("authoritative_verification", dict),
        ("discovered_gaps", list), ("structural_observations", list),
        ("result", str),
    ]:
        require_field(label, fields, dotted, expected_type)
    require_field(label, fields, "state", str, "REPORTED")


def validate_review_template() -> None:
    label = "templates/review.yaml"
    fields = load_protocol_fields(label)
    if fields is None:
        return
    validate_version(label, fields)
    for dotted, expected_type in [
        ("task_id", str), ("task_revision", int), ("review_revision", int),
        ("state", str), ("reviewed_report.repository", str),
        ("reviewed_report.path", str), ("reviewed_report.commit", str),
        ("reviewed_report.report_revision", int),
        ("contract_compliance.protocol_version", str),
        ("contract_compliance.execution_base", str),
        ("contract_compliance.skill_rules", str),
        ("contract_compliance.scope", str),
        ("contract_compliance.structure_policy", str),
        ("contract_compliance.git_authority", str),
        ("contract_compliance.acceptance_criteria", str),
        ("gap_disposition", list), ("follow_up_tasks", list),
        ("promotion_readiness.eligible_for_candidate_capture", bool),
    ]:
        require_field(label, fields, dotted, expected_type)


def require_tokens(path: Path, tokens: list[str]) -> None:
    if not path.is_file():
        error(f"missing required protocol file: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            error(f"{path.relative_to(ROOT)}: missing required protocol term '{token}'")
    validate_links(path, text)


def validate_protocol_docs() -> None:
    require_tokens(ROOT / "protocols" / "TASK_PROTOCOL.md", [
        "Supported protocol version", "NEW_ARCHITECT_SESSION_REQUIRED",
        "templates/handoff.yaml", "handoff_snapshot", "RESOLVED",
        "NOT_APPLICABLE", "UNRESOLVED", "promotion_candidate_head",
        "REVERIFY / REVIEW_REQUIRED", "LOCAL", "FOLLOW_UP",
        "No orphan source files", "No speculative scale structure",
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
    validate_task_template()
    validate_handoff_template()
    validate_report_template()
    validate_review_template()
    validate_protocol_docs()

    if warnings:
        print("\nWarnings:")
        for message in warnings:
            print(f"  WARN: {message}")
    if errors:
        print("\nErrors:", file=sys.stderr)
        for message in errors:
            print(f"  ERROR: {message}", file=sys.stderr)
        return 1

    print(f"\nOK: validated curated 15-skill taxonomy and protocol v{SUPPORTED_PROTOCOL_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
