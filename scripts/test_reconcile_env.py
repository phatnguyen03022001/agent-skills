#!/usr/bin/env python3
"""Synthetic command-level tests for the bounded env reconciler."""

from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import reconcile_env


ROOT = Path(__file__).resolve().parents[1]
COMMAND = ROOT / "scripts" / "reconcile_env.py"


class ReconcileEnvTests(unittest.TestCase):
    def fixture(self, example_text: str, env_text: str | None = None) -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        example = root / "sample.example"
        env = root / "sample.env"
        example.write_text(example_text, encoding="utf-8")
        if env_text is not None:
            env.write_text(env_text, encoding="utf-8")
        return temp, example, env

    def invoke(self, example: Path, env: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(COMMAND), "--example", str(example), "--env", str(env), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_check_write_order_extras_comments_and_idempotency(self) -> None:
        _, example, env = self.fixture(
            "# Template heading\nexport ALPHA=template\nBETA=template\nGAMMA=template\n",
            "# operator note\nBETA='synthetic value with spaces'\nALPHA=opaque\\ value\nEXTRA=keep\\ this\n",
        )
        check = self.invoke(example, env)
        self.assertNotEqual(check.returncode, 0)
        self.assertNotIn("synthetic value", check.stdout + check.stderr)
        write = self.invoke(example, env, "--write")
        self.assertNotEqual(write.returncode, 0, write.stdout + write.stderr)
        expected = (
            "# Template heading\n"
            "export ALPHA=opaque\\ value\n"
            "BETA='synthetic value with spaces'\n"
            'GAMMA="<thiếu key>"\n'
            "\n# Operator-only entries\n# operator note\nEXTRA=keep\\ this\n"
        )
        self.assertEqual(env.read_text(encoding="utf-8"), expected)
        before = env.read_bytes()
        repeated = self.invoke(example, env, "--write")
        self.assertNotEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertEqual(env.read_bytes(), before)

    def test_missing_file_is_private_and_unresolved_marker_fails(self) -> None:
        _, example, env = self.fixture("ALPHA=template\n")
        result = self.invoke(example, env, "--write")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(env.is_file())
        self.assertEqual(env.read_text(encoding="utf-8"), 'ALPHA="<thiếu key>"\n')
        self.assertEqual(stat.S_IMODE(env.stat().st_mode) & 0o077, 0)
        self.assertNotIn("template", result.stdout + result.stderr)

    def test_existing_permissions_are_not_widened(self) -> None:
        _, example, env = self.fixture("ALPHA=template\nBETA=template\n", "ALPHA=opaque\n")
        os.chmod(env, 0o640)
        result = self.invoke(example, env, "--write")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(stat.S_IMODE(env.stat().st_mode), 0o640)

    def test_invalid_inputs_leave_existing_file_and_no_temp_files(self) -> None:
        cases = [
            ("ALPHA=template\nALPHA=second\n", "ALPHA=opaque\n"),
            ("ALPHA=template\n", "ALPHA='unterminated\n"),
            ("ALPHA=template\\\nNEXT=value\n", "ALPHA=opaque\n"),
            ("ALPHA=template\n", "broken syntax\n"),
            ("ALPHA=template\n", 'ALPHA="synthetic"garbage"\n'),
            ("ALPHA=template\n", 'ALPHA="escaped\\"\n'),
        ]
        for example_text, env_text in cases:
            with self.subTest(example=example_text, env=env_text):
                _, example, env = self.fixture(example_text, env_text)
                before = env.read_bytes()
                result = self.invoke(example, env, "--write")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(env.read_bytes(), before)
                self.assertEqual(list(env.parent.glob(".reconcile-env-*")), [])
                self.assertNotIn("opaque", result.stdout + result.stderr)

    def test_atomic_replace_failure_preserves_file_and_cleans_temp(self) -> None:
        _, example, env = self.fixture("ALPHA=template\n", "ALPHA=opaque\n")
        before = env.read_bytes()
        with patch.object(reconcile_env.os, "replace", side_effect=OSError("synthetic failure")):
            with self.assertRaises(reconcile_env.InputError):
                reconcile_env.atomic_write(env, "ALPHA=replaced\n", env.stat())
        self.assertEqual(env.read_bytes(), before)
        self.assertEqual(list(env.parent.glob(".reconcile-env-*")), [])

    def test_rejects_same_path_symlink_and_non_regular_inputs(self) -> None:
        _, example, env = self.fixture("ALPHA=template\n", "ALPHA=opaque\n")
        same = self.invoke(example, example, "--write")
        self.assertNotEqual(same.returncode, 0)
        link = env.parent / "linked.env"
        link.symlink_to(env)
        symlink = self.invoke(example, link, "--write")
        self.assertNotEqual(symlink.returncode, 0)
        directory = env.parent / "not-a-file"
        directory.mkdir()
        non_regular = self.invoke(example, directory, "--write")
        self.assertNotEqual(non_regular.returncode, 0)
        for result in (same, symlink, non_regular):
            self.assertNotIn("opaque", result.stdout + result.stderr)

    def test_supported_quoted_placeholder_remains_unresolved(self) -> None:
        _, example, env = self.fixture("ALPHA=template\n", "ALPHA='<thiếu key>'\n")
        result = self.invoke(example, env, "--write")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_identical_template_blanks_do_not_create_extra_section(self) -> None:
        _, example, env = self.fixture("# heading\n\nALPHA=template\n", "# heading\n\nALPHA=opaque\n")
        result = self.invoke(example, env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Operator-only", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
