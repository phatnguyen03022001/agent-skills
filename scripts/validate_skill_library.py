#!/usr/bin/env python3
"""Validate the curated Agent Skills library and reusable task protocol."""

from __future__ import annotations

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
    "github-workflow", "cloud-run-basics",
})
FRONTMATTER_KEYS = frozenset({"name", "description"})
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CAPABILITY_RE = re.compile(r"^[a-z][a-z0-9_]*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CATALOG_ROW_RE = re.compile(r"^\| `([a-z0-9-]+)` \|", re.MULTILINE)
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(.*)$")
INT_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
CATALOG_START = "<!-- SKILL_CATALOG_START -->"
CATALOG_END = "<!-- SKILL_CATALOG_END -->"

CONTINUATION_MODES = frozenset({"MANUAL", "AUTO_UNTIL_STOP"})
CONTINUATION_STOP_CONDITIONS = frozenset({
    "BLOCKED", "STALE_STATE", "AUTHORITY_REQUIRED",
    "CURRENT_PHASE_CAPABILITY_UNAVAILABLE", "REVIEW_REQUIRED",
    "REVERIFY_REQUIRED", "USER_STOP",
})
CAPABILITY_PHASES = frozenset({"EXECUTION", "REVIEW", "VERIFICATION", "PROMOTION", "RELEASE"})
CONTINUATION_PHASES = frozenset({"REVIEW", "VERIFICATION", "PROMOTION", "RELEASE"})
CONTINUATION_ACTIONS = frozenset({
    "REQUEST_ARCHITECT_REVIEW", "RUN_AUTHORITATIVE_VERIFICATION", "PROMOTE_TO_MAIN",
    "CREATE_VERSION_TAG", "MUTATE_REPOSITORY_METADATA", "PUBLISH_RELEASE", "FINAL_VERIFY", "STOP",
})
LIFECYCLE_STATES = frozenset({
    "PLANNED", "REPORTED", "ACCEPTED", "VERIFIED", "PROMOTED_NOT_RELEASED", "RELEASED",
})

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
        if key not in FRONTMATTER_KEYS:
            error(f"{path.relative_to(ROOT)}:{line_no}: unexpected frontmatter key '{key}'")
            continue
        if not value:
            error(f"{path.relative_to(ROOT)}:{line_no}: empty frontmatter value for '{key}'")
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


def preprocess_yaml(path: Path) -> list[tuple[int, int, str]]:
    lines: list[tuple[int, int, str]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "\t" in raw:
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: tabs are not supported")
        raw = strip_yaml_comment(raw).rstrip()
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: indentation must use two-space steps")
        lines.append((number, indent, raw[indent:]))
    if not lines:
        raise ProtocolYamlError(f"{path.relative_to(ROOT)}: empty YAML document")
    if lines[0][1] != 0:
        raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{lines[0][0]}: top-level content must start at column 1")
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
    if raw[:1] in ("'", '"'):
        quote = raw[0]
        if len(raw) < 2 or raw[-1] != quote:
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: unterminated quoted scalar")
        inner = raw[1:-1]
        escaped = False
        for char in inner:
            if quote == '"' and char == "\\" and not escaped:
                escaped = True
                continue
            if char == quote and not escaped:
                raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: unexpected quote inside quoted scalar")
            escaped = False
        if escaped:
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: unterminated escape in quoted scalar")
        return inner
    if raw.startswith(("[", "{", "|", ">")):
        raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: unsupported YAML value syntax")
    return raw


def split_mapping(text: str, path: Path, number: int) -> tuple[str, str]:
    match = KEY_RE.match(text)
    if not match:
        raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: expected mapping key")
    return match.group(1), match.group(2).strip()


def parse_mapping(
    lines: list[tuple[int, int, str]], index: int, indent: int, path: Path
) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        number, current_indent, text = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: unexpected indentation")
        if text.startswith("-"):
            break
        key, raw_value = split_mapping(text, path, number)
        if key in result:
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: duplicate mapping key '{key}'")
        index += 1
        if raw_value:
            result[key] = scalar_value(raw_value, path, number)
            if index < len(lines) and lines[index][1] > indent:
                raise ProtocolYamlError(
                    f"{path.relative_to(ROOT)}:{lines[index][0]}: scalar '{key}' cannot have nested content"
                )
            continue
        if index >= len(lines) or lines[index][1] <= indent:
            result[key] = None
            continue
        if lines[index][1] != indent + 2:
            raise ProtocolYamlError(
                f"{path.relative_to(ROOT)}:{lines[index][0]}: nested content for '{key}' must indent by two spaces"
            )
        if lines[index][2].startswith("-"):
            result[key], index = parse_sequence(lines, index, indent + 2, path)
        else:
            result[key], index = parse_mapping(lines, index, indent + 2, path)
    return result, index


def parse_sequence(
    lines: list[tuple[int, int, str]], index: int, indent: int, path: Path
) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        number, current_indent, text = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: unexpected indentation in sequence")
        if not text.startswith("-"):
            break
        if text == "-" or not text.startswith("- "):
            raise ProtocolYamlError(f"{path.relative_to(ROOT)}:{number}: malformed sequence item")

        item_text = text[2:].strip()
        index += 1
        mapping_match = KEY_RE.match(item_text)
        if not mapping_match:
            value = scalar_value(item_text, path, number)
            if index < len(lines) and lines[index][1] > indent:
                raise ProtocolYamlError(
                    f"{path.relative_to(ROOT)}:{lines[index][0]}: scalar sequence item cannot have nested content"
                )
            result.append(value)
            continue

        key, raw_value = mapping_match.group(1), mapping_match.group(2).strip()
        item: dict[str, Any] = {}
        if raw_value:
            item[key] = scalar_value(raw_value, path, number)
        else:
            if index >= len(lines) or lines[index][1] <= indent:
                item[key] = None
            else:
                if lines[index][1] != indent + 2:
                    raise ProtocolYamlError(
                        f"{path.relative_to(ROOT)}:{lines[index][0]}: nested sequence mapping must indent by two spaces"
                    )
                if lines[index][2].startswith("-"):
                    item[key], index = parse_sequence(lines, index, indent + 2, path)
                else:
                    item[key], index = parse_mapping(lines, index, indent + 2, path)

        if index < len(lines) and lines[index][1] > indent:
            if lines[index][1] != indent + 2 or lines[index][2].startswith("-"):
                raise ProtocolYamlError(
                    f"{path.relative_to(ROOT)}:{lines[index][0]}: malformed sequence mapping item"
                )
            tail, index = parse_mapping(lines, index, indent + 2, path)
            overlap = set(item) & set(tail)
            if overlap:
                duplicate = sorted(overlap)[0]
                raise ProtocolYamlError(
                    f"{path.relative_to(ROOT)}:{number}: duplicate mapping key '{duplicate}' inside sequence item"
                )
            item.update(tail)
        result.append(item)
    return result, index


def load_protocol_document(relative_path: str) -> dict[str, Any] | None:
    path = ROOT / relative_path
    if not path.is_file():
        error(f"missing required protocol template: {relative_path}")
        return None
    try:
        lines = preprocess_yaml(path)
        if lines[0][2].startswith("-"):
            raise ProtocolYamlError(f"{relative_path}:{lines[0][0]}: top-level document must be a mapping")
        document, index = parse_mapping(lines, 0, 0, path)
        if index != len(lines):
            number, _, _ = lines[index]
            raise ProtocolYamlError(f"{relative_path}:{number}: unexpected content or indentation")
    except ProtocolYamlError as exc:
        error(str(exc))
        return None
    return document


_MISSING = object()

TASK_SEQUENCE_SCHEMAS: dict[str, dict[str, type]] = {
    "authority_sources": {"source": str, "role": str, "precedence": int},
    "acceptance_criteria": {"id": str, "requirement": str, "evidence_required": str},
    "verification.executor_checks": {"id": str, "command_or_check": str, "required": bool},
}
REPORT_SEQUENCE_SCHEMAS: dict[str, dict[str, type]] = {
    "changed_files": {
        "path": str, "summary": str, "new_file": bool,
        "in_scope": bool, "structure_authorized": bool,
    },
    "commits_created": {"sha": str, "message": str},
    "acceptance_evidence": {"criterion_id": str, "status": str, "evidence": str},
    "executor_checks": {"check_id": str, "result": str, "evidence": str},
    "discovered_gaps": {
        "gap_id": str, "classification": str, "type": str, "severity": str,
        "description": str, "evidence": str, "impact": str,
        "blocks_current_task": bool, "action_taken": str, "suggested_next_step": str,
    },
    "structural_observations": {
        "type": str, "path": str, "evidence": str,
        "recommendation": str, "action_taken": str,
    },
}
REVIEW_SEQUENCE_SCHEMAS: dict[str, dict[str, type]] = {
    "gap_disposition": {"gap_id": str, "decision": str, "rationale": str},
    "follow_up_tasks": {"task_id": str, "origin": dict},
}
FOLLOW_UP_ORIGIN_SCHEMA: dict[str, type] = {"type": str, "task_id": str, "gap_id": str}
GAP_CLASSIFICATIONS = frozenset({"LOCAL", "FOLLOW_UP", "BLOCKING"})
REVIEW_STATES = frozenset({"ACCEPTED", "REVISION_REQUIRED", "BLOCKED"})
LOCAL_HYGIENE_RESULTS = frozenset({"PASS", "RETAINED_FOR_EVIDENCE", "BLOCKED"})
LOCAL_HYGIENE_RETAINED_SCHEMA: dict[str, type] = {"identity": str, "reason": str}


def get_path(document: dict[str, Any], dotted: str) -> Any:
    value: Any = document
    for key in dotted.split("."):
        if not isinstance(value, dict) or key not in value:
            return _MISSING
        value = value[key]
    return value


def require_field(
    label: str,
    document: dict[str, Any],
    dotted: str,
    expected_type: type,
    expected_value: Any = _MISSING,
) -> None:
    value = get_path(document, dotted)
    if value is _MISSING:
        error(f"{label}: missing required path '{dotted}'")
        return
    if type(value) is not expected_type:
        error(f"{label}: path '{dotted}' must be {expected_type.__name__}, got {type(value).__name__}")
        return
    if expected_value is not _MISSING and value != expected_value:
        error(f"{label}: path '{dotted}' must equal {expected_value!r}, got {value!r}")


def require_mapping_schema(
    label: str,
    value: Any,
    item_path: str,
    required_fields: dict[str, type],
    closed_values: dict[str, frozenset[Any]] | None = None,
) -> bool:
    if type(value) is not dict:
        error(f"{label}: path '{item_path}' must be mapping")
        return False

    expected_keys = set(required_fields)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    unexpected = sorted(actual_keys - expected_keys)
    if missing:
        error(f"{label}: path '{item_path}' missing required fields {missing}")
    if unexpected:
        error(f"{label}: path '{item_path}' has unexpected fields {unexpected}")

    valid = not missing and not unexpected
    for field, expected_type in required_fields.items():
        if field not in value:
            continue
        field_value = value[field]
        if type(field_value) is not expected_type:
            error(
                f"{label}: path '{item_path}.{field}' must be {expected_type.__name__}, "
                f"got {type(field_value).__name__}"
            )
            valid = False
            continue
        if closed_values and field in closed_values and field_value not in closed_values[field]:
            error(f"{label}: path '{item_path}.{field}' has unsupported value {field_value!r}")
            valid = False
    return valid


def require_mapping_sequence_schema(
    label: str,
    document: dict[str, Any],
    dotted: str,
    required_fields: dict[str, type],
    closed_values: dict[str, frozenset[Any]] | None = None,
) -> list[tuple[int, dict[str, Any]]]:
    value = get_path(document, dotted)
    if value is _MISSING:
        error(f"{label}: missing required path '{dotted}'")
        return []
    if type(value) is not list:
        error(f"{label}: path '{dotted}' must be list")
        return []

    valid_items: list[tuple[int, dict[str, Any]]] = []
    for index, item in enumerate(value):
        item_path = f"{dotted}[{index}]"
        if require_mapping_schema(label, item, item_path, required_fields, closed_values):
            valid_items.append((index, item))
    return valid_items


def validate_version(label: str, document: dict[str, Any]) -> None:
    require_field(label, document, "protocol_version", int, SUPPORTED_PROTOCOL_VERSION)


def validate_continuation_policy(label: str, doc: dict[str, Any]) -> None:
    value = get_path(doc, "continuation_policy")
    if value is _MISSING:
        return
    valid = require_mapping_schema(
        label,
        value,
        "continuation_policy",
        {"mode": str, "stop_conditions": list},
    )
    if not valid:
        return
    mode = value["mode"]
    if mode not in CONTINUATION_MODES:
        error(f"{label}: unsupported continuation mode {mode!r}")
    stops = value["stop_conditions"]
    if any(type(item) is not str for item in stops):
        error(f"{label}: path 'continuation_policy.stop_conditions' must contain strings")
        return
    stop_set = set(stops)
    unsupported = sorted(stop_set - CONTINUATION_STOP_CONDITIONS)
    if unsupported:
        error(f"{label}: unsupported continuation stop conditions {unsupported}")
    missing = sorted(CONTINUATION_STOP_CONDITIONS - stop_set)
    if missing:
        error(f"{label}: missing non-waivable continuation stop conditions {missing}")
    if len(stops) != len(stop_set):
        error(f"{label}: continuation_policy.stop_conditions must not contain duplicates")


def validate_capability_requirements(label: str, doc: dict[str, Any]) -> None:
    value = get_path(doc, "capability_requirements")
    if value is _MISSING:
        return
    if type(value) is not dict:
        error(f"{label}: path 'capability_requirements' must be mapping")
        return
    for phase, requirements in value.items():
        if phase not in CAPABILITY_PHASES:
            error(f"{label}: unsupported capability phase {phase!r}")
            continue
        dotted = f"capability_requirements.{phase}"
        if type(requirements) is not list:
            error(f"{label}: path '{dotted}' must be list")
            continue
        if len(requirements) != len(set(map(str, requirements))):
            error(f"{label}: path '{dotted}' must not contain duplicates")
        for item in requirements:
            if type(item) is not str or not CAPABILITY_RE.fullmatch(item):
                error(f"{label}: path '{dotted}' contains invalid semantic capability {item!r}")


def validate_release_authority(label: str, doc: dict[str, Any]) -> None:
    value = get_path(doc, "release_authority")
    if value is _MISSING:
        return
    require_mapping_schema(
        label,
        value,
        "release_authority",
        {
            "create_version_tag": bool,
            "mutate_repository_metadata": bool,
            "publish_release": bool,
        },
    )


def validate_task_template() -> None:
    label = "templates/task.yaml"
    doc = load_protocol_document(label)
    if doc is None:
        return
    validate_version(label, doc)
    for dotted, expected_type in [
        ("task_id", str), ("task_revision", int), ("state", str),
        ("origin.type", str), ("origin.task_id", str), ("origin.gap_id", str),
        ("architect_binding.target_repository", str), ("target.repository", str),
        ("target.branch.name", str), ("target.branch.role", str),
        ("execution_base.mode", str), ("execution_base.capture", str),
        ("execution_base.require_exact_match", bool),
        ("skill_library.repository", str), ("skill_library.revision", str),
        ("architect_analysis_skills", list),
        ("execution_skills.required", list), ("execution_skills.recommended", list),
        ("external_skills.architect_analysis", list),
        ("external_skills.execution_required", list),
        ("external_skills.execution_recommended", list),
        ("structure_authority.status", str), ("structure_authority.source", str),
        ("structure_authority.rationale", str), ("objective", str),
        ("scope.required_changes", list),
        ("scope.allowed_existing_files_or_components", list),
        ("scope.expected_files_are_restrictive", bool),
        ("invariants", list), ("forbidden_changes", list),
        ("gap_policy.local_auto_fix", bool),
        ("gap_policy.scope_expansion", str), ("gap_policy.architecture_change", str),
        ("gap_policy.spec_change", str), ("gap_policy.dependency_change", str),
        ("gap_policy.public_contract_change", str),
        ("gap_policy.blocking_gap_behavior", str),
        ("structure_policy.expected_new_files", list),
        ("structure_policy.unlisted_new_files.allowed", bool),
        ("structure_policy.unlisted_new_files.max", int),
        ("structure_policy.unlisted_new_files.within", list),
        ("structure_policy.unlisted_new_files.purpose", str),
        ("structure_policy.allow_new_top_level_directories", bool),
        ("structure_policy.allow_new_shared_modules", bool),
        ("verification.authoritative_verification", dict),
        ("verification.authoritative_verification.required", bool),
        ("verification.authoritative_verification.mechanism", str),
        ("verification.authoritative_verification.expected_signal", str),
        ("git_authority.create_branch", bool), ("git_authority.commit", bool),
        ("git_authority.push", bool), ("git_authority.promote_to_main", bool),
        ("blocking_decisions", list), ("execution_ready", bool),
    ]:
        require_field(label, doc, dotted, expected_type)
    for dotted, schema in TASK_SEQUENCE_SCHEMAS.items():
        require_mapping_sequence_schema(label, doc, dotted, schema)
    require_field(label, doc, "execution_base.mode", str, "handoff_snapshot")
    require_field(label, doc, "execution_base.require_exact_match", bool, True)
    require_field(label, doc, "gap_policy.blocking_gap_behavior", str, "BLOCKED")

    validate_continuation_policy(label, doc)
    validate_capability_requirements(label, doc)
    validate_release_authority(label, doc)

    bound = get_path(doc, "architect_binding.target_repository")
    target = get_path(doc, "target.repository")
    if bound is not _MISSING and target is not _MISSING and bound != target:
        error(f"{label}: architect binding must equal target repository")

    status = get_path(doc, "structure_authority.status")
    source = get_path(doc, "structure_authority.source")
    rationale = get_path(doc, "structure_authority.rationale")
    ready = get_path(doc, "execution_ready")
    if status is not _MISSING and status not in {"RESOLVED", "NOT_APPLICABLE", "UNRESOLVED"}:
        error(f"{label}: unsupported structure_authority.status {status!r}")
    if status == "RESOLVED" and not source:
        error(f"{label}: RESOLVED structure authority requires non-empty source")
    if status == "NOT_APPLICABLE" and not rationale:
        error(f"{label}: NOT_APPLICABLE structure authority requires non-empty rationale")
    if status == "UNRESOLVED" and ready is True:
        error(f"{label}: UNRESOLVED structure authority cannot be execution-ready")
    if ready is True and get_path(doc, "git_authority.commit") is not True:
        error(f"{label}: execution-ready task requires Executor git_authority.commit for canonical report evidence")


def validate_handoff_template() -> None:
    label = "templates/handoff.yaml"
    doc = load_protocol_document(label)
    if doc is None:
        return
    validate_version(label, doc)
    for dotted, expected_type in [
        ("handoff_type", str), ("task.id", str), ("task.revision", int),
        ("task.path", str), ("target.repository", str), ("target.branch", str),
        ("target.base_head", str),
    ]:
        require_field(label, doc, dotted, expected_type)
    require_field(label, doc, "handoff_type", str, "EXECUTOR")


def validate_report_template() -> None:
    label = "templates/report.yaml"
    doc = load_protocol_document(label)
    if doc is None:
        return
    validate_version(label, doc)
    for dotted, expected_type in [
        ("task_id", str), ("task_revision", int), ("report_revision", int),
        ("state", str), ("task_source.path", str), ("execution.repository", str),
        ("execution.branch.name", str), ("execution.branch.role", str),
        ("execution.authorized_base_head", str),
        ("execution.pre_execution_head", str), ("execution.final_execution_head", str),
        ("skill_library.repository", str),
        ("skill_library.authorized_revision", str), ("skill_library.observed_revision", str),
        ("execution_skills_used.required", list),
        ("execution_skills_used.recommended", list),
        ("execution_skills_used.external", list),
        ("pre_execution_checks.protocol_version_supported", bool),
        ("pre_execution_checks.handoff_type_confirmed", bool),
        ("pre_execution_checks.task_at_base_confirmed", bool),
        ("pre_execution_checks.task_identity_confirmed", bool),
        ("pre_execution_checks.architect_binding_confirmed", bool),
        ("pre_execution_checks.repository_confirmed", bool),
        ("pre_execution_checks.branch_confirmed", bool),
        ("pre_execution_checks.base_head_confirmed", bool),
        ("pre_execution_checks.skill_revision_confirmed", bool),
        ("pre_execution_checks.required_execution_skills_available", bool),
        ("pre_execution_checks.structure_authority_confirmed", bool),
        ("pre_execution_checks.working_tree_clean", bool),
        ("pushed", bool), ("promoted_to_main", bool),
        ("authoritative_verification", dict),
        ("authoritative_verification.required", bool),
        ("authoritative_verification.performed", bool),
        ("authoritative_verification.result", str),
        ("authoritative_verification.evidence", str),
        ("working_tree_after.clean", bool), ("working_tree_after.summary", str),
        ("result", str),
    ]:
        require_field(label, doc, dotted, expected_type)
    for dotted, schema in REPORT_SEQUENCE_SCHEMAS.items():
        closed_values = {"classification": GAP_CLASSIFICATIONS} if dotted == "discovered_gaps" else None
        require_mapping_sequence_schema(label, doc, dotted, schema, closed_values)
    require_field(label, doc, "deviations_from_task", list)
    require_field(label, doc, "blockers", list)
    require_field(label, doc, "state", str, "REPORTED")

    preflight = get_path(doc, "capability_preflight")
    if preflight is not _MISSING:
        valid = require_mapping_schema(
            label,
            preflight,
            "capability_preflight",
            {"phase": str, "required": list, "available": list, "missing": list, "passed": bool},
        )
        if valid and preflight["phase"] not in CAPABILITY_PHASES:
            error(f"{label}: unsupported capability phase {preflight['phase']!r}")

    hygiene = get_path(doc, "local_hygiene")
    if hygiene is not _MISSING:
        valid = require_mapping_schema(
            label,
            hygiene,
            "local_hygiene",
            {
                "result": str,
                "run_root": str,
                "cleanup_performed": bool,
                "retained": list,
                "evidence": str,
            },
        )
        if valid:
            result = hygiene["result"]
            if result not in LOCAL_HYGIENE_RESULTS:
                error(f"{label}: unsupported local hygiene result {result!r}")
            retained = hygiene["retained"]
            for index, item in enumerate(retained):
                item_valid = require_mapping_schema(
                    label,
                    item,
                    f"local_hygiene.retained[{index}]",
                    LOCAL_HYGIENE_RETAINED_SCHEMA,
                )
                if item_valid and (not item["identity"] or not item["reason"]):
                    error(f"{label}: retained local hygiene artifact requires non-empty identity and reason")
            if result == "PASS" and retained:
                error(f"{label}: PASS local hygiene cannot retain artifacts")
            if result == "RETAINED_FOR_EVIDENCE" and not retained:
                error(f"{label}: RETAINED_FOR_EVIDENCE requires retained artifact identity and reason")


def validate_review_template() -> None:
    label = "templates/review.yaml"
    doc = load_protocol_document(label)
    if doc is None:
        return
    validate_version(label, doc)
    for dotted, expected_type in [
        ("task_id", str), ("task_revision", int), ("review_revision", int),
        ("state", str), ("reviewed_report.repository", str),
        ("reviewed_report.path", str), ("reviewed_report.commit", str),
        ("reviewed_report.report_revision", int),
        ("contract_compliance.protocol_version", str),
        ("contract_compliance.identity", str),
        ("contract_compliance.execution_base", str),
        ("contract_compliance.skill_rules", str),
        ("contract_compliance.scope", str),
        ("contract_compliance.structure_policy", str),
        ("contract_compliance.git_authority", str),
        ("contract_compliance.acceptance_criteria", str),
        ("contract_compliance.verifier_evidence", str),
        ("promotion_readiness.eligible_for_candidate_capture", bool),
        ("promotion_readiness.reason", str),
        ("notes", list),
    ]:
        require_field(label, doc, dotted, expected_type)
    for dotted, schema in REVIEW_SEQUENCE_SCHEMAS.items():
        items = require_mapping_sequence_schema(label, doc, dotted, schema)
        if dotted == "follow_up_tasks":
            for index, item in items:
                require_mapping_schema(
                    label, item["origin"], f"follow_up_tasks[{index}].origin", FOLLOW_UP_ORIGIN_SCHEMA
                )

    independence = get_path(doc, "independence")
    if independence is not _MISSING:
        valid = require_mapping_schema(
            label,
            independence,
            "independence",
            {
                "reviewer_role": str,
                "separate_session_from_executor": bool,
                "exact_report_identity_verified": bool,
            },
        )
        if valid:
            if independence["reviewer_role"] != "ARCHITECT":
                error(f"{label}: independence.reviewer_role must equal 'ARCHITECT'")
            if independence["separate_session_from_executor"] is not True:
                error(f"{label}: independent review requires separate_session_from_executor=true")

    state = get_path(doc, "state")
    eligible = get_path(doc, "promotion_readiness.eligible_for_candidate_capture")
    if state is not _MISSING and state not in REVIEW_STATES:
        error(f"{label}: unsupported review state {state!r}")
    if eligible is True and state != "ACCEPTED":
        error(f"{label}: only ACCEPTED review may be candidate-eligible")


def validate_continuation_template() -> None:
    label = "templates/continuation.yaml"
    doc = load_protocol_document(label)
    if doc is None:
        return
    validate_version(label, doc)
    for dotted, expected_type in [
        ("handoff_type", str),
        ("task.id", str), ("task.revision", int), ("task.path", str),
        ("phase", str),
        ("reviewed_report.repository", str), ("reviewed_report.path", str),
        ("reviewed_report.commit", str), ("reviewed_report.report_revision", int),
        ("promotion_candidate_head", str),
        ("expected_refs.dev", str), ("expected_refs.main", str),
        ("expected_state.lifecycle", str),
        ("prior_result", str), ("prior_lifecycle_state", str),
        ("next_authorized_action", str),
    ]:
        require_field(label, doc, dotted, expected_type)
    require_field(label, doc, "handoff_type", str, "CONTINUATION")
    phase = get_path(doc, "phase")
    if phase is not _MISSING and phase not in CONTINUATION_PHASES:
        error(f"{label}: unsupported continuation phase {phase!r}")
    expected_lifecycle = get_path(doc, "expected_state.lifecycle")
    if expected_lifecycle is not _MISSING and expected_lifecycle not in LIFECYCLE_STATES:
        error(f"{label}: unsupported expected lifecycle state {expected_lifecycle!r}")
    lifecycle = get_path(doc, "prior_lifecycle_state")
    if lifecycle is not _MISSING and lifecycle not in LIFECYCLE_STATES:
        error(f"{label}: unsupported lifecycle state {lifecycle!r}")
    action = get_path(doc, "next_authorized_action")
    if action is not _MISSING and action not in CONTINUATION_ACTIONS:
        error(f"{label}: unsupported next authorized action {action!r}")


def validate_template_consistency() -> None:
    docs = {
        name: load_protocol_document(f"templates/{name}.yaml")
        for name in ("task", "handoff", "report", "review", "continuation")
    }
    if any(doc is None for doc in docs.values()):
        return
    task = docs["task"]
    assert task is not None
    task_id = task.get("task_id")
    task_revision = task.get("task_revision")
    for name in ("handoff", "continuation"):
        doc = docs[name]
        assert doc is not None
        nested = doc.get("task")
        if not isinstance(nested, dict) or nested.get("id") != task_id or nested.get("revision") != task_revision:
            error(f"templates/{name}.yaml: task identity must match templates/task.yaml")
    for name in ("report", "review"):
        doc = docs[name]
        assert doc is not None
        if doc.get("task_id") != task_id or doc.get("task_revision") != task_revision:
            error(f"templates/{name}.yaml: task identity must match templates/task.yaml")


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
        "Supported protocol version", "one active target repository",
        "simultaneous ambiguous active target is forbidden",
        "explicit terminal handoff/result", "fresh repository-local task",
        "fresh exact handoff", "fresh exact base HEAD",
        "authority for repository A never grants authority for repository B",
        "report/review/verifier/promotion/release lineage remains repository-local",
        "PROGRAM", "ordered repository-local tasks",
        "not a universal multi-repository task authority",
        "two organizational roles", "Executor specializations",
        "templates/handoff.yaml", "templates/continuation.yaml", "handoff_snapshot",
        "RESOLVED", "NOT_APPLICABLE", "UNRESOLVED", "promotion_candidate_head",
        "REVERIFY / REVIEW_REQUIRED", "LOCAL", "FOLLOW_UP",
        "No orphan source files", "No speculative scale structure",
        "reviewed_report.commit", "single-parent direct child",
        "shared trusted", "create_branch: false", "PROMOTED_NOT_RELEASED",
        "AUTO_UNTIL_STOP", "CURRENT_PHASE_CAPABILITY_UNAVAILABLE",
        "capability_requirements", "release_authority", "RELEASED",
        "GitHub Actions must not become an iterative debugger",
        "Tool availability is not permission to consume quota",
    ])
    require_tokens(ROOT / "architect" / "SKILL.md", [
        "one active target repository", "close the current repository-specific phase",
        "explicitly identify the next `owner/repo`", "refresh canonical GitHub truth",
        "discard previous repository-specific assumptions",
        "simultaneous ambiguous active target is forbidden",
        "PROGRAM", "Chat", "Executor", "Model", "Effort", "Progress",
        "PROMPT TO COPY", "Program 2/4 · agent-standards · execution",
    ])
    require_tokens(ROOT / "executor" / "SKILL.md", [
        "active task/repository binding remains immutable", "explicit terminal handoff/result",
        "previous evidence finalized", "no outstanding mutation authority carried forward",
        "fresh repository-local task", "fresh exact handoff", "fresh exact base HEAD",
        "authority for repository A never grants authority for repository B",
        "report/review/verifier/promotion/release lineage remains repository-local",
    ])
    require_tokens(ROOT / "README.md", [
        "PROGRAM", "presentation only", "ordered repository-local tasks",
        "TASK LAUNCH", "Chat", "Executor", "Model", "Effort", "Progress",
        "Program 2/4 · agent-standards · execution", "fake percentages",
    ])
    require_tokens(ROOT / "contracts" / "IMPLEMENTATION_CONTRACT.md", [
        "template", "continuation_policy", "capability_requirements", "release_authority",
    ])
    require_tokens(ROOT / "contracts" / "IMPLEMENTATION_REPORT.md", [
        "template", "capability_preflight", "PROMOTED_NOT_RELEASED",
    ])
    require_tokens(ROOT / "contracts" / "ARCHITECT_REVIEW.md", [
        "template", "separate agent/session", "PROMOTED_NOT_RELEASED",
    ])


def main() -> int:
    errors.clear()
    warnings.clear()

    discovered = sorted(ROOT.rglob("SKILL.md"))
    allowed = {ROOT / name / "SKILL.md" for name in EXPECTED_SKILLS}
    unexpected = [path for path in discovered if path not in allowed]
    missing = sorted(path for path in allowed if not path.is_file())
    if unexpected or missing or set(discovered) != allowed:
        error(
            "curated skill locations mismatch; "
            f"missing={[str(p.relative_to(ROOT)) for p in missing]} "
            f"unexpected={[str(p.relative_to(ROOT)) for p in unexpected]}"
        )

    seen_names: dict[str, Path] = {}
    print("Skill word counts:")
    for path in discovered:
        metadata, text = parse_frontmatter(path)
        rel = path.relative_to(ROOT)
        if path not in allowed:
            continue
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
    validate_continuation_template()
    validate_template_consistency()
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
