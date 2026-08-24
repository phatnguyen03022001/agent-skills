#!/usr/bin/env python3
"""Adversarial regression tests for validate_skill_library.py."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path("scripts/validate_skill_library.py")


class ValidatorRegressionTests(unittest.TestCase):
    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name) / "repo"
        shutil.copytree(ROOT, root)
        self.addCleanup(temp.cleanup)
        return temp, root

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(root / VALIDATOR)],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def assert_rejected(self, mutate) -> str:
        _, root = self.fixture()
        mutate(root)
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_canonical_library_passes(self) -> None:
        _, root = self.fixture()
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_hidden_nested_sixteenth_skill_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / ".hidden" / "SKILL.md"
            path.parent.mkdir()
            path.write_text("---\nname: hidden\ndescription: Use when hidden.\n---\n", encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("unexpected=['.hidden/SKILL.md']", output)

    def test_duplicate_key_inside_sequence_mapping_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8")
            text = text.replace('    role: ""\n    precedence: 1', '    role: ""\n    source: duplicate\n    precedence: 1')
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("duplicate mapping key 'source'", output)

    def test_malformed_sequence_mapping_item_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8").replace('  - source: ""', '  - source ""', 1)
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("scalar sequence item cannot have nested content", output)

    def test_invalid_nested_sequence_structure_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8").replace('  required:\n    - executor', '  required:\n      - executor', 1)
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("must indent by two spaces", output)

    def test_missing_acceptance_criteria_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8").replace("acceptance_criteria:", "acceptance_missing:", 1)
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("missing required path 'acceptance_criteria'", output)

    def test_unexpected_skill_frontmatter_key_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "architect" / "SKILL.md"
            text = path.read_text(encoding="utf-8").replace("description:", "version: 1\ndescription:", 1)
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("unexpected frontmatter key 'version'", output)

    def test_execution_ready_requires_report_commit_authority(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8")
            text = text.replace("status: UNRESOLVED", "status: NOT_APPLICABLE", 1)
            text = text.replace('rationale: ""', 'rationale: "structure unchanged"', 1)
            text = text.replace("execution_ready: false", "execution_ready: true", 1)
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("requires Executor git_authority.commit", output)


if __name__ == "__main__":
    unittest.main()
