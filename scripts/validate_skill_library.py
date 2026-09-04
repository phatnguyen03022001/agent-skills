#!/usr/bin/env python3
"""Validate the curated Agent Skills library and reusable task protocol."""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from datetime import datetime
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
RFC3339_UTC_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)$"
)

CONTINUATION_MODES = frozenset({"MANUAL", "AUTO_UNTIL_STOP"})
CONTINUATION_STOP_CONDITIONS = frozenset({
    "BLOCKED", "STALE_STATE", "AUTHORITY_REQUIRED",
    "CURRENT_PHASE_CAPABILITY_UNAVAILABLE", "REVIEW_REQUIRED",
    "REVERIFY_REQUIRED", "USER_STOP",
})
CAPABILITY_PHASES = frozenset({"EXECUTION", "REVIEW", "VERIFICATION", "PROMOTION", "RELEASE"})
CONTINUATION_PHASES = frozenset({"REVIEW", "VERIFICATION", "PROMOTION", "RELEASE"})
CONTINUATION_ACTIONS = frozenset({
    "REQUEST_ARCHITECT_REVIEW", "RUN_AUTHORITATIVE_VERIFICATION", "PROMOTE_TARGET_REF", "PROMOTE_TO_MAIN",
    "CREATE_VERSION_TAG", "MUTATE_REPOSITORY_METADATA", "PUBLISH_RELEASE", "FINAL_VERIFY", "STOP",
})
CONTINUATION_PHASE_ACTIONS: dict[str, frozenset[str]] = {
    "REVIEW": frozenset({"REQUEST_ARCHITECT_REVIEW", "STOP"}),
    "VERIFICATION": frozenset({"RUN_AUTHORITATIVE_VERIFICATION", "STOP"}),
    "PROMOTION": frozenset({"PROMOTE_TARGET_REF", "PROMOTE_TO_MAIN", "STOP"}),
    "RELEASE": frozenset({
        "CREATE_VERSION_TAG", "MUTATE_REPOSITORY_METADATA", "PUBLISH_RELEASE", "FINAL_VERIFY", "STOP",
    }),
}
LIFECYCLE_STATES = frozenset({
    "PLANNED", "REPORTED", "ACCEPTED", "VERIFIED", "PROMOTED_NOT_RELEASED", "RELEASED",
})
PROGRAM_ARTIFACT_TYPE = "GENERATED_PROGRAM"
PROGRAM_AUTHORITY = "NONE"
PROGRAM_INVALIDATION = "FULL_REGENERATION_ON_MATERIAL_INPUT_CHANGE"
CASE_ROUTER_PATH = ".agent/case-router.yaml"
ADMITTED_CASE_ID = "EXECUTE"

# One normalized semantic model serves both sparse protocol-v3 serialization and
# explicit expanded-v3 task artifacts.  -1 means that no exact-file count cap is
# imposed inside an already-authorized semantic/component boundary.
TASK_NORMALIZATION_DEFAULTS: dict[str, Any] = {
    "scope": {
        "expected_files_are_restrictive": False,
    },
    "structure_policy": {
        "expected_new_files": [],
        "unlisted_new_files": {
            "allowed": True,
            "max": -1,
            "within": [],
            "purpose": "Executor-local structure inside the authorized semantic/component boundary",
        },
        "allow_new_top_level_directories": False,
        "allow_new_shared_modules": False,
    },
    "continuation_policy": {
        "mode": "MANUAL",
        "stop_conditions": [
            "BLOCKED",
            "STALE_STATE",
            "AUTHORITY_REQUIRED",
            "CURRENT_PHASE_CAPABILITY_UNAVAILABLE",
            "REVIEW_REQUIRED",
            "REVERIFY_REQUIRED",
            "USER_STOP",
        ],
    },
    "capability_requirements": {},
    "release_authority": {
        "create_version_tag": False,
        "mutate_repository_metadata": False,
        "publish_release": False,
    },
}

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


def load_json_document(relative_path: str) -> dict[str, Any] | None:
    path = ROOT / relative_path
    if not path.is_file():
        error(f"missing required generated program template: {relative_path}")
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        error(f"{relative_path}: invalid JSON: {exc}")
        return None
    if type(document) is not dict:
        error(f"{relative_path}: top-level JSON document must be mapping")
        return None
    return document


def validate_case_navigation() -> None:
    label = CASE_ROUTER_PATH
    document = load_protocol_document(label)
    if document is None:
        return

    valid_document = require_mapping_schema(label, document, "case-router", {"cases": list})
    cases = get_path(document, "cases")
    if not valid_document or type(cases) is not list:
        return

    entries = require_mapping_sequence_schema(
        label,
        document,
        "cases",
        {"id": str, "capabilities": list},
    )
    if len(cases) != 1:
        error(f"{label}: path 'cases' must contain exactly one admitted case")

    seen_case_ids: set[str] = set()
    for index, entry in entries:
        case_id = entry["id"]
        if case_id in seen_case_ids:
            error(f"{label}: duplicate case id {case_id!r}")
        seen_case_ids.add(case_id)
        if case_id != ADMITTED_CASE_ID:
            error(f"{label}: unsupported case id {case_id!r}")

        capabilities = validate_string_list(
            label,
            entry["capabilities"],
            f"cases[{index}].capabilities",
            require_non_empty=True,
        )
        for capability in capabilities:
            if not CAPABILITY_RE.fullmatch(capability):
                error(f"{label}: invalid capability key {capability!r}")
            elif capability not in EXPECTED_SKILLS or not (ROOT / capability / "SKILL.md").is_file():
                error(f"{label}: unsupported capability key {capability!r}")
        if case_id == ADMITTED_CASE_ID and capabilities != ["executor"]:
            error(f"{label}: EXECUTE must route to exactly ['executor']")


_MISSING = object()


def normalize_task_document(document: dict[str, Any]) -> dict[str, Any]:
    """Materialize one canonical meaning for omitted optional task controls."""
    normalized = deepcopy(document)

    scope = normalized.get("scope")
    if type(scope) is dict:
        scope.setdefault(
            "expected_files_are_restrictive",
            TASK_NORMALIZATION_DEFAULTS["scope"]["expected_files_are_restrictive"],
        )

    for key in (
        "structure_policy",
        "continuation_policy",
        "capability_requirements",
        "release_authority",
    ):
        if key not in normalized or normalized[key] == {}:
            normalized[key] = deepcopy(TASK_NORMALIZATION_DEFAULTS[key])

    return normalized

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
CONTINUATION_REF_SCHEMA: dict[str, type] = {"ref": str, "commit": str}
PROGRAM_ITEM_SCHEMA: dict[str, type] = {
    "id": str,
    "traceability": list,
    "depends_on": list,
    "obligations": list,
    "acceptance_refs": list,
    "required_evidence": list,
    "required_capabilities": list,
}
PROGRAM_EXCLUSION_SCHEMA: dict[str, type] = {"ref": str, "rationale": str}
PROGRAM_EXTERNAL_AUTHORITY_SCHEMA: dict[str, type] = {"source": str, "revision": str}


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


def validate_string_list(
    label: str,
    value: Any,
    item_path: str,
    *,
    require_non_empty: bool = False,
) -> list[str]:
    if type(value) is not list:
        error(f"{label}: path '{item_path}' must be list")
        return []
    if require_non_empty and not value:
        error(f"{label}: path '{item_path}' must not be empty")
    valid: list[str] = []
    for index, item in enumerate(value):
        if type(item) is not str or not item.strip():
            error(f"{label}: path '{item_path}[{index}]' must be non-empty string")
            continue
        valid.append(item)
    if len(valid) == len(value) and len(valid) != len(set(valid)):
        error(f"{label}: path '{item_path}' must not contain duplicates")
    return valid


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


def validate_operational_timing(label: str, doc: dict[str, Any]) -> None:
    timing = get_path(doc, "operational_timing")
    if timing is _MISSING:
        return
    valid = require_mapping_schema(
        label,
        timing,
        "operational_timing",
        {
            "started_at_utc": str,
            "terminal_decision_at_utc": str,
        },
    )
    if not valid:
        return
    for field in ("started_at_utc", "terminal_decision_at_utc"):
        value = timing[field]
        if not RFC3339_UTC_RE.fullmatch(value):
            error(f"{label}: path 'operational_timing.{field}' must be RFC 3339 UTC timestamp")
            continue
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            error(f"{label}: path 'operational_timing.{field}' must be a valid RFC 3339 UTC timestamp")


def validate_generated_program_template() -> None:
    label = "templates/program.generated.json"
    doc = load_json_document(label)
    if doc is None:
        return

    top_valid = require_mapping_schema(
        label,
        doc,
        "program",
        {
            "protocol_version": int,
            "artifact_type": str,
            "authority": str,
            "invalidation": str,
            "synthesis": dict,
            "coverage": dict,
            "items": list,
        },
    )
    require_field(label, doc, "protocol_version", int, SUPPORTED_PROTOCOL_VERSION)
    require_field(label, doc, "artifact_type", str, PROGRAM_ARTIFACT_TYPE)
    require_field(label, doc, "authority", str, PROGRAM_AUTHORITY)
    require_field(label, doc, "invalidation", str, PROGRAM_INVALIDATION)
    if not top_valid:
        return

    synthesis = doc["synthesis"]
    synthesis_valid = require_mapping_schema(
        label,
        synthesis,
        "synthesis",
        {"target": dict, "external_authorities": list, "synthesis_policy": dict},
    )
    if synthesis_valid:
        target = synthesis["target"]
        if require_mapping_schema(
            label,
            target,
            "synthesis.target",
            {"repository": str, "source_revision": str},
        ):
            for key in ("repository", "source_revision"):
                if not target[key].strip():
                    error(f"{label}: path 'synthesis.target.{key}' must be non-empty")

        policy = synthesis["synthesis_policy"]
        if require_mapping_schema(
            label,
            policy,
            "synthesis.synthesis_policy",
            {"id": str, "revision": str},
        ):
            for key in ("id", "revision"):
                if not policy[key].strip():
                    error(f"{label}: path 'synthesis.synthesis_policy.{key}' must be non-empty")

        external_seen: set[tuple[str, str]] = set()
        for index, authority in enumerate(synthesis["external_authorities"]):
            item_path = f"synthesis.external_authorities[{index}]"
            if not require_mapping_schema(
                label,
                authority,
                item_path,
                PROGRAM_EXTERNAL_AUTHORITY_SCHEMA,
            ):
                continue
            if not authority["source"].strip() or not authority["revision"].strip():
                error(f"{label}: path '{item_path}' requires non-empty immutable source and revision")
                continue
            identity = (authority["source"], authority["revision"])
            if identity in external_seen:
                error(f"{label}: duplicate external authority identity {identity!r}")
            external_seen.add(identity)

    coverage = doc["coverage"]
    required_refs: list[str] = []
    exclusion_refs: set[str] = set()
    if require_mapping_schema(
        label,
        coverage,
        "coverage",
        {"required_refs": list, "exclusions": list},
    ):
        required_refs = validate_string_list(label, coverage["required_refs"], "coverage.required_refs")
        required_ref_set = set(required_refs)
        for index, exclusion in enumerate(coverage["exclusions"]):
            item_path = f"coverage.exclusions[{index}]"
            if not require_mapping_schema(label, exclusion, item_path, PROGRAM_EXCLUSION_SCHEMA):
                continue
            ref = exclusion["ref"]
            rationale = exclusion["rationale"]
            if not ref.strip() or not rationale.strip():
                error(f"{label}: path '{item_path}' requires non-empty ref and bounded rationale")
                continue
            if ref in exclusion_refs:
                error(f"{label}: duplicate exclusion ref {ref!r}")
            exclusion_refs.add(ref)
            if ref not in required_ref_set:
                error(f"{label}: exclusion ref {ref!r} is not present in coverage.required_refs")

    item_ids: set[str] = set()
    item_dependencies: dict[str, list[str]] = {}
    covered_refs: set[str] = set()
    required_ref_set = set(required_refs)
    for index, item in enumerate(doc["items"]):
        item_path = f"items[{index}]"
        if not require_mapping_schema(label, item, item_path, PROGRAM_ITEM_SCHEMA):
            continue
        item_id = item["id"]
        if not item_id.strip():
            error(f"{label}: path '{item_path}.id' must be non-empty")
            continue
        if item_id in item_ids:
            error(f"{label}: duplicate generated item id {item_id!r}")
        item_ids.add(item_id)

        traceability = validate_string_list(
            label, item["traceability"], f"{item_path}.traceability", require_non_empty=True
        )
        dependencies = validate_string_list(label, item["depends_on"], f"{item_path}.depends_on")
        obligations = validate_string_list(label, item["obligations"], f"{item_path}.obligations")
        validate_string_list(
            label, item["acceptance_refs"], f"{item_path}.acceptance_refs", require_non_empty=True
        )
        validate_string_list(
            label, item["required_evidence"], f"{item_path}.required_evidence", require_non_empty=True
        )
        capabilities = validate_string_list(
            label, item["required_capabilities"], f"{item_path}.required_capabilities"
        )
        for capability in capabilities:
            if not CAPABILITY_RE.fullmatch(capability):
                error(f"{label}: path '{item_path}.required_capabilities' contains invalid semantic capability {capability!r}")

        item_dependencies[item_id] = dependencies
        covered_refs.update(traceability)
        covered_refs.update(obligations)
        for ref in traceability + obligations:
            if ref not in required_ref_set:
                error(f"{label}: item {item_id!r} references unselected coverage ref {ref!r}")

    for item_id, dependencies in item_dependencies.items():
        for dependency in dependencies:
            if dependency not in item_ids:
                error(f"{label}: item {item_id!r} depends on unknown item {dependency!r}")
            if dependency == item_id:
                error(f"{label}: item {item_id!r} cannot depend on itself")

    graph = {
        item_id: [dependency for dependency in dependencies if dependency in item_ids]
        for item_id, dependencies in item_dependencies.items()
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(item_id: str) -> bool:
        if item_id in visiting:
            return True
        if item_id in visited:
            return False
        visiting.add(item_id)
        for dependency in graph.get(item_id, []):
            if visit(dependency):
                return True
        visiting.remove(item_id)
        visited.add(item_id)
        return False

    if any(visit(item_id) for item_id in graph):
        error(f"{label}: dependency graph must be acyclic")

    for ref in required_refs:
        covered = ref in covered_refs
        excluded = ref in exclusion_refs
        if not covered and not excluded:
            error(f"{label}: required coverage ref {ref!r} is neither covered nor excluded")
        if covered and excluded:
            error(f"{label}: coverage ref {ref!r} cannot be both covered and excluded")


def validate_task_template() -> None:
    label = "templates/task.yaml"
    doc = load_protocol_document(label)
    if doc is None:
        return
    doc = normalize_task_document(doc)
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
        ("execution.authorized_base_head", str), ("execution.final_execution_head", str),
        ("skill_library.repository", str), ("skill_library.authorized_revision", str),
        ("pushed", bool),
        ("authoritative_verification", dict),
        ("authoritative_verification.required", bool),
        ("authoritative_verification.performed", bool),
        ("authoritative_verification.result", str),
        ("authoritative_verification.evidence", str),
        ("result", str),
    ]:
        require_field(label, doc, dotted, expected_type)

    for dotted, expected_type in [
        ("execution.pre_execution_head", str),
        ("skill_library.observed_revision", str),
        ("promoted_to_main", bool),
    ]:
        value = get_path(doc, dotted)
        if value is not _MISSING and type(value) is not expected_type:
            error(f"{label}: path '{dotted}' must be {expected_type.__name__}, got {type(value).__name__}")

    execution_skills = get_path(doc, "execution_skills_used")
    if execution_skills is not _MISSING:
        require_mapping_schema(
            label,
            execution_skills,
            "execution_skills_used",
            {"required": list, "recommended": list, "external": list},
        )

    pre_checks = get_path(doc, "pre_execution_checks")
    if pre_checks is not _MISSING:
        require_mapping_schema(
            label,
            pre_checks,
            "pre_execution_checks",
            {
                "protocol_version_supported": bool,
                "handoff_type_confirmed": bool,
                "task_at_base_confirmed": bool,
                "task_identity_confirmed": bool,
                "architect_binding_confirmed": bool,
                "repository_confirmed": bool,
                "branch_confirmed": bool,
                "base_head_confirmed": bool,
                "skill_revision_confirmed": bool,
                "required_execution_skills_available": bool,
                "structure_authority_confirmed": bool,
                "working_tree_clean": bool,
            },
        )

    working_tree_after = get_path(doc, "working_tree_after")
    if working_tree_after is not _MISSING:
        require_mapping_schema(
            label,
            working_tree_after,
            "working_tree_after",
            {"clean": bool, "summary": str},
        )

    optional_sequences = {"changed_files", "commits_created", "discovered_gaps", "structural_observations"}
    for dotted, schema in REPORT_SEQUENCE_SCHEMAS.items():
        if dotted in optional_sequences and get_path(doc, dotted) is _MISSING:
            continue
        closed_values = {"classification": GAP_CLASSIFICATIONS} if dotted == "discovered_gaps" else None
        require_mapping_sequence_schema(label, doc, dotted, schema, closed_values)
    for dotted in ("deviations_from_task", "blockers"):
        value = get_path(doc, dotted)
        if value is not _MISSING and type(value) is not list:
            error(f"{label}: path '{dotted}' must be list")
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

    validate_operational_timing(label, doc)


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
    ]:
        require_field(label, doc, dotted, expected_type)
    for dotted, schema in REVIEW_SEQUENCE_SCHEMAS.items():
        if get_path(doc, dotted) is _MISSING:
            continue
        items = require_mapping_sequence_schema(label, doc, dotted, schema)
        if dotted == "follow_up_tasks":
            for index, item in items:
                require_mapping_schema(
                    label, item["origin"], f"follow_up_tasks[{index}].origin", FOLLOW_UP_ORIGIN_SCHEMA
                )

    promotion_readiness = get_path(doc, "promotion_readiness")
    if promotion_readiness is not _MISSING:
        require_mapping_schema(
            label,
            promotion_readiness,
            "promotion_readiness",
            {"eligible_for_candidate_capture": bool, "reason": str},
        )

    notes = get_path(doc, "notes")
    if notes is not _MISSING and type(notes) is not list:
        error(f"{label}: path 'notes' must be list")

    validate_operational_timing(label, doc)

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
    if state == "ACCEPTED":
        exact_identity = get_path(doc, "independence.exact_report_identity_verified")
        if exact_identity is not True:
            error(f"{label}: ACCEPTED review requires independence.exact_report_identity_verified=true")
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
        ("expected_state.lifecycle", str),
        ("prior_result", str), ("prior_lifecycle_state", str),
        ("next_authorized_action", str),
    ]:
        require_field(label, doc, dotted, expected_type)
    require_field(label, doc, "handoff_type", str, "CONTINUATION")

    expected_refs = get_path(doc, "expected_refs")
    canonical_ref_names: set[str] = set()
    legacy_expected_refs = False
    if expected_refs is _MISSING:
        error(f"{label}: missing required path 'expected_refs'")
    elif type(expected_refs) is list:
        items = require_mapping_sequence_schema(label, doc, "expected_refs", CONTINUATION_REF_SCHEMA)
        for index, item in items:
            ref = item["ref"]
            commit = item["commit"]
            if not ref or not commit:
                error(f"{label}: expected_refs[{index}] requires non-empty ref and commit identity")
            canonical_ref_names.add(ref)
    elif type(expected_refs) is dict:
        legacy_expected_refs = True
        require_field(label, doc, "expected_refs.dev", str)
        require_field(label, doc, "expected_refs.main", str)
    else:
        error(f"{label}: path 'expected_refs' must be canonical list or legacy dev/main mapping")

    phase = get_path(doc, "phase")
    if phase is not _MISSING and phase not in CONTINUATION_PHASES:
        error(f"{label}: unsupported continuation phase {phase!r}")
    expected_lifecycle = get_path(doc, "expected_state.lifecycle")
    if expected_lifecycle is not _MISSING and expected_lifecycle not in LIFECYCLE_STATES:
        error(f"{label}: unsupported expected lifecycle state {expected_lifecycle!r}")
    lifecycle = get_path(doc, "prior_lifecycle_state")
    if lifecycle is not _MISSING and lifecycle not in LIFECYCLE_STATES:
        error(f"{label}: unsupported lifecycle state {lifecycle!r}")
    if (
        type(expected_lifecycle) is str
        and type(lifecycle) is str
        and expected_lifecycle != lifecycle
    ):
        error(f"{label}: expected_state.lifecycle must equal prior_lifecycle_state for the bound snapshot")

    action = get_path(doc, "next_authorized_action")
    if action is not _MISSING and action not in CONTINUATION_ACTIONS:
        error(f"{label}: unsupported next authorized action {action!r}")
    if phase in CONTINUATION_PHASE_ACTIONS and action in CONTINUATION_ACTIONS:
        if action not in CONTINUATION_PHASE_ACTIONS[phase]:
            error(f"{label}: action {action!r} is not valid for continuation phase {phase!r}")

    if action == "PROMOTE_TO_MAIN" and not legacy_expected_refs:
        error(f"{label}: PROMOTE_TO_MAIN is legacy compatibility input and requires expected_refs.dev/main")
    if action == "PROMOTE_TARGET_REF":
        if type(expected_refs) is not list:
            error(f"{label}: PROMOTE_TARGET_REF requires canonical topology-neutral expected_refs")
        target_ref = get_path(doc, "promotion_target_ref")
        if type(target_ref) is not str or not target_ref:
            error(f"{label}: PROMOTE_TARGET_REF requires non-empty promotion_target_ref")
        elif target_ref not in canonical_ref_names:
            error(f"{label}: promotion_target_ref must identify a ref present in expected_refs")


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
        "Decision ownership and consequence-based materiality",
        "implementation judgment and local HOW by default",
        "Uncertainty, unfamiliarity, or a preference difference alone is not an escalation trigger",
        "Protocol-v3 task normalization/defaults",
        "same protocol-v3 semantic model",
        "missing authority remains fail-closed",
        "semantic/component boundary",
        "A newly discovered companion surface",
        "Local structure is Executor-owned",
        "material structure and remain Architect-owned",
        "LOCAL needs no Architect approval",
        "simultaneous ambiguous active target is forbidden",
        "explicit terminal handoff/result", "fresh repository-local task",
        "fresh exact handoff", "fresh exact base HEAD",
        "authority for repository A never grants authority for repository B",
        "report/review/verifier/promotion/release lineage remains repository-local",
        "PROGRAM", "ordered repository-local tasks",
        "not a universal multi-repository task authority",
        "program.generated.json", "authority: NONE", "mathematically unique DAG",
        "whole generated program stale", "fully regenerate", "Task authority remains just in time",
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
        "Normal Executor reports are evidence indexes",
        "changed-file enumeration may be omitted",
        "omission never means PASS, permission, or hidden success",
        "Sparse reports remain evidence-backed rather than self-attested",
        "Evidence-first Architect review",
        "Deep implementation reconstruction occurs only for",
        "preference-only revision",
        "Operational timing is omitted by default",
        "explicitly requests",
        "No timing-enabled or telemetry-mode field",
    ])
    require_tokens(ROOT / "architect" / "SKILL.md", [
        "material WHAT, BOUNDARY, and PROOF",
        "delegates implementation judgment to Executor by default",
        "uncertainty alone does not require escalation",
        "normalization/default table",
        "Omitted implementation prescription",
        "one active target repository", "close the current repository-specific phase",
        "explicitly identify the next `owner/repo`", "refresh canonical GitHub truth",
        "discard previous repository-specific assumptions",
        "simultaneous ambiguous active target is forbidden",
        "PROGRAM", "program.generated.json", "full regeneration", "just in time",
        "Chat", "Executor", "Model", "Effort", "Progress",
        "PROMPT TO COPY", "Program 2/4 · agent-standards · execution",
        "evidence-first sequence", "candidate diff boundary", "material risk triggers",
        "stop when material predicates are proven", "preference-only revision",
        "default hot path", "explicitly requests", "No timing-enabled or telemetry-mode field",
    ])
    require_tokens(ROOT / "executor" / "SKILL.md", [
        "inspect existing repository patterns before choosing implementation HOW",
        "implementation judgment belongs to Executor by default",
        "smallest sufficient repo-native implementation",
        "LOCAL needs no Architect approval",
        "automatic pre-mutation blockers",
        "active task/repository binding remains immutable", "explicit terminal handoff/result",
        "previous evidence finalized", "no outstanding mutation authority carried forward",
        "fresh repository-local task", "fresh exact handoff", "fresh exact base HEAD",
        "authority for repository A never grants authority for repository B",
        "report/review/verifier/promotion/release lineage remains repository-local",
        "Operational timing is omitted from the default Executor hot path",
        "Normal reports are evidence indexes", "changed-file enumeration may be omitted",
        "omission never means PASS, permission, or hidden success",
        "Sparse reports remain evidence-backed rather than self-attested",
        "explicitly requests", "No timing-enabled or telemetry-mode field",
    ])
    require_tokens(ROOT / "README.md", [
        "PROGRAM", "presentation only", "ordered repository-local tasks",
        "program.generated.json", "authority `NONE`",
        "TASK LAUNCH", "Chat", "Executor", "Model", "Effort", "Progress",
        "Program 2/4 · agent-standards · execution", "fake percentages",
    ])
    require_tokens(ROOT / "contracts" / "IMPLEMENTATION_CONTRACT.md", [
        "positive semantic/component scope",
        "normalization/default table",
        "Missing exact-file or local-structure prescription",
        "Missing authority fields never default to permission",
        "template", "continuation_policy", "capability_requirements", "release_authority",
    ])
    require_tokens(ROOT / "contracts" / "IMPLEMENTATION_REPORT.md", [
        "template", "capability_preflight", "PROMOTED_NOT_RELEASED",
        "compact evidence index", "changed-file enumeration may be omitted",
        "omission never means PASS, permission, or hidden success", "explicitly requests",
        "No timing-enabled or telemetry-mode field",
    ])
    require_tokens(ROOT / "contracts" / "ARCHITECT_REVIEW.md", [
        "template", "separate agent/session", "PROMOTED_NOT_RELEASED",
        "evidence-first", "candidate diff boundary", "deviations/gaps",
        "material risk triggers", "stop when material predicates are proven",
        "preference-only revision", "omitted by default", "explicitly requests",
        "No timing-enabled or telemetry-mode field",
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
    validate_generated_program_template()
    validate_case_navigation()
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
