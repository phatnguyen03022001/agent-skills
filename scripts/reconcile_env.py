#!/usr/bin/env python3
"""Reconcile one operator env file against one example without exposing values."""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


KEY_RE = re.compile(r"^(?P<export>export[ \t]+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>.*)$")
PLACEHOLDER = '"<thiếu key>"'
EXTRAS_HEADING = "# Operator-only entries"


class InputError(Exception):
    """An input is outside the intentionally small supported dotenv subset."""


@dataclass(frozen=True)
class Line:
    kind: str
    text: str
    key: str | None = None
    prefix: str | None = None
    value: str | None = None


def safe_existing_file(path: Path, *, required: bool) -> os.stat_result | None:
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        if required:
            raise InputError("required input is unavailable") from None
        return None
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise InputError("input must be a regular non-symlink file")
    return info


def validate_value(value: str) -> None:
    if value.endswith("\\"):
        raise InputError("multiline values are unsupported")
    if value.startswith("'") or value.startswith('"'):
        quote = value[0]
        closing: int | None = None
        escaped = False
        for index, character in enumerate(value[1:], start=1):
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                closing = index
                break
        if closing != len(value) - 1:
            raise InputError("malformed quoted value")
        return
    if "#" in value or "'" in value or '"' in value:
        raise InputError("ambiguous unquoted value")


def parse_lines(raw_lines: list[str], *, retain_template_lines: bool) -> list[Line]:
    parsed: list[Line] = []
    keys: set[str] = set()
    for raw in raw_lines:
        if not raw.strip():
            parsed.append(Line("blank", raw))
            continue
        if raw.lstrip().startswith("#"):
            parsed.append(Line("comment", raw))
            continue
        match = KEY_RE.fullmatch(raw)
        if match is None:
            raise InputError("malformed assignment")
        key = match.group("key")
        if key in keys:
            raise InputError("duplicate key")
        keys.add(key)
        value = match.group("value")
        validate_value(value)
        prefix = (match.group("export") or "") + key + "="
        parsed.append(Line("assignment", raw, key=key, prefix=prefix, value=value))
    if retain_template_lines and not parsed:
        raise InputError("example input has no supported entries")
    return parsed


def parse(path: Path, *, retain_template_lines: bool) -> list[Line]:
    try:
        return parse_lines(path.read_text(encoding="utf-8").splitlines(), retain_template_lines=retain_template_lines)
    except (OSError, UnicodeError) as exc:
        raise InputError("input cannot be read as supported text") from exc


def split_env(
    lines: list[Line], template_keys: set[str], template_comments: set[str]
) -> tuple[dict[str, Line], list[Line], list[Line]]:
    values: dict[str, Line] = {}
    extras: list[Line] = []
    comments: list[Line] = []
    marker_index = next(
        (index for index, line in enumerate(lines) if line.kind == "comment" and line.text == EXTRAS_HEADING),
        None,
    )
    for index, line in enumerate(lines):
        if marker_index is not None and index == marker_index:
            if comments and comments[-1].kind == "blank":
                comments.pop()
            continue
        if line.kind == "assignment":
            if line.key in template_keys:
                values[line.key] = line
            else:
                extras.append(line)
        elif line.kind == "comment" and line.text not in template_comments:
            comments.append(line)
        elif line.kind == "blank":
            continue
    return values, comments, extras


def render(template: list[Line], env: list[Line]) -> tuple[str, int, int, int]:
    template_keys = {line.key for line in template if line.kind == "assignment" and line.key is not None}
    template_comments = {line.text for line in template if line.kind == "comment"}
    values, comments, extras = split_env(env, template_keys, template_comments)
    output: list[str] = []
    missing = 0
    for line in template:
        if line.kind != "assignment":
            output.append(line.text)
            continue
        current = values.get(line.key)
        if current is None:
            missing += 1
            output.append(f"{line.prefix}{PLACEHOLDER}")
        else:
            output.append(f"{line.prefix}{current.value}")
    if comments or extras:
        output.extend(["", EXTRAS_HEADING])
        output.extend(line.text for line in comments)
        output.extend(line.text for line in extras)
    text = "\n".join(output) + "\n"
    placeholders = sum(
        line.kind == "assignment" and line.value in {PLACEHOLDER, "'<thiếu key>'"}
        for line in parse_text(text)
    )
    return text, missing, len(extras), placeholders


def parse_text(text: str) -> list[Line]:
    """Parse generated text without reading another path."""
    return parse_lines(text.splitlines(), retain_template_lines=False)


def atomic_write(path: Path, text: str, existing: os.stat_result | None) -> None:
    descriptor: int | None = None
    temporary = ""
    try:
        descriptor, temporary = tempfile.mkstemp(prefix=".reconcile-env-", dir=path.parent)
        mode = stat.S_IMODE(existing.st_mode) if existing is not None else 0o600
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            descriptor = None
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = ""
        if existing is not None:
            os.chmod(path, mode)
    except OSError as exc:
        raise InputError("atomic write failed") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", required=True, type=Path)
    parser.add_argument("--env", required=True, type=Path)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args(argv)
    example = Path(os.path.abspath(arguments.example))
    env = Path(os.path.abspath(arguments.env))
    try:
        if example == env:
            raise InputError("example and env paths must differ")
        example_info = safe_existing_file(example, required=True)
        env_info = safe_existing_file(env, required=False)
        if env_info is not None and (example_info.st_dev, example_info.st_ino) == (env_info.st_dev, env_info.st_ino):
            raise InputError("example and env paths must differ")
        template = parse(example, retain_template_lines=True)
        current = parse(env, retain_template_lines=False) if env_info is not None else []
        reconciled, missing, extras, placeholders = render(template, current)
        old = env.read_text(encoding="utf-8") if env_info is not None else ""
        needed = old != reconciled
        if arguments.write and needed:
            atomic_write(env, reconciled, env_info)
        result = "RECONCILED" if arguments.write else ("RECONCILIATION_REQUIRED" if needed else "RECONCILIATION_CURRENT")
        print(f"{result} keys={sum(line.kind == 'assignment' for line in template)} missing={missing} extras={extras} placeholders={placeholders}")
        return 1 if placeholders or (needed and not arguments.write) else 0
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
