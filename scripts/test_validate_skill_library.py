#!/usr/bin/env python3
"""Adversarial regression tests for validate_skill_library.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path("scripts/validate_skill_library.py")
_VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "validate_skill_library_under_test",
    ROOT / VALIDATOR,
)
assert _VALIDATOR_SPEC is not None and _VALIDATOR_SPEC.loader is not None
VALIDATOR_MODULE = importlib.util.module_from_spec(_VALIDATOR_SPEC)
_VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)


class ValidatorRegressionTests(unittest.TestCase):
    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name) / "repo"
        shutil.copytree(ROOT, root)
        self.addCleanup(temp.cleanup)
        return temp, root

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        original_root = VALIDATOR_MODULE.ROOT
        try:
            VALIDATOR_MODULE.ROOT = root
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                returncode = VALIDATOR_MODULE.main()
        finally:
            VALIDATOR_MODULE.ROOT = original_root
        return subprocess.CompletedProcess(
            args=["python3", str(root / VALIDATOR)],
            returncode=returncode,
            stdout=stdout.getvalue(),
            stderr=stderr.getvalue(),
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

    def test_unterminated_quoted_scalar_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8")
            self.assertIn("task_id: TASK-0001", text)
            text = text.replace("task_id: TASK-0001", 'task_id: "TASK-0001', 1)
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("unterminated quoted scalar", output)

    def test_exact_execution_base_gate_is_required(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8")
            before = "  require_exact_match: true"
            self.assertIn(before, text)
            text = text.replace(before, "  require_exact_match_missing: true", 1)
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("missing required path 'execution_base.require_exact_match'", output)

    def test_structure_restriction_fields_are_required(self) -> None:
        cases = [
            ("scope.expected_files_are_restrictive", "  expected_files_are_restrictive: true", "  expected_files_are_restrictive_missing: true"),
            ("structure_policy.unlisted_new_files.allowed", "    allowed: false", "    allowed_missing: false"),
            ("structure_policy.unlisted_new_files.max", "    max: 0", "    max_missing: 0"),
            ("structure_policy.unlisted_new_files.within", "    within: []", "    within_missing: []"),
            ("structure_policy.unlisted_new_files.purpose", '    purpose: ""', '    purpose_missing: ""'),
            ("structure_policy.allow_new_top_level_directories", "  allow_new_top_level_directories: false", "  allow_new_top_level_directories_missing: false"),
            ("structure_policy.allow_new_shared_modules", "  allow_new_shared_modules: false", "  allow_new_shared_modules_missing: false"),
        ]
        for dotted, before, after in cases:
            with self.subTest(path=dotted):
                def mutate(root: Path, before=before, after=after) -> None:
                    path = root / "templates" / "task.yaml"
                    text = path.read_text(encoding="utf-8")
                    self.assertIn(before, text)
                    text = text.replace(before, after, 1)
                    path.write_text(text, encoding="utf-8")
                output = self.assert_rejected(mutate)
                self.assertIn(f"missing required path '{dotted}'", output)

    def test_report_pre_execution_evidence_fields_are_required(self) -> None:
        keys = [
            "handoff_type_confirmed", "task_identity_confirmed", "architect_binding_confirmed",
            "repository_confirmed", "branch_confirmed", "base_head_confirmed",
            "skill_revision_confirmed", "required_execution_skills_available",
            "structure_authority_confirmed", "working_tree_clean",
        ]
        for key in keys:
            with self.subTest(key=key):
                def mutate(root: Path, key=key) -> None:
                    path = root / "templates" / "report.yaml"
                    text = path.read_text(encoding="utf-8")
                    before = f"  {key}: false"
                    self.assertIn(before, text)
                    text = text.replace(before, f"  {key}_missing: false", 1)
                    path.write_text(text, encoding="utf-8")
                output = self.assert_rejected(mutate)
                self.assertIn(f"missing required path 'pre_execution_checks.{key}'", output)

    def test_review_identity_compliance_field_is_required(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "review.yaml"
            text = path.read_text(encoding="utf-8")
            before = "  identity: NOT_PROVEN"
            self.assertIn(before, text)
            text = text.replace(before, "  identity_missing: NOT_PROVEN", 1)
            path.write_text(text, encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("missing required path 'contract_compliance.identity'", output)

    def test_mapping_sequence_required_fields_and_types_are_enforced(self) -> None:
        cases = [
            ("templates/task.yaml", '  - id: AC-1\n    requirement: ""\n    evidence_required: ""', "  - banana: potato", "acceptance_criteria[0]"),
            ("templates/task.yaml", "    precedence: 1", '    precedence: "wrong"', "authority_sources[0].precedence"),
            ("templates/report.yaml", '  - path: ""\n    summary: ""\n    new_file: false\n    in_scope: false\n    structure_authorized: false', '  - summary: ""\n    new_file: false\n    in_scope: false\n    structure_authorized: false', "changed_files[0]"),
            ("templates/report.yaml", '  - criterion_id: AC-1\n    status: NOT_PROVEN\n    evidence: ""', '  - status: NOT_PROVEN\n    evidence: ""', "acceptance_evidence[0]"),
        ]
        for relative, before, after, expected in cases:
            with self.subTest(path=relative, expected=expected):
                def mutate(root: Path, relative=relative, before=before, after=after) -> None:
                    path = root / relative
                    text = path.read_text(encoding="utf-8")
                    self.assertIn(before, text)
                    path.write_text(text.replace(before, after, 1), encoding="utf-8")
                output = self.assert_rejected(mutate)
                self.assertIn(expected, output)

    def test_mapping_sequence_closed_values_and_keys_are_enforced(self) -> None:
        cases = [
            ("templates/report.yaml", "    classification: FOLLOW_UP", "    classification: BANANA", "unsupported value 'BANANA'"),
            ("templates/report.yaml", '    message: ""', '    message: ""\n    path: not-a-commit-record', "unexpected fields ['path']"),
        ]
        for relative, before, after, expected in cases:
            with self.subTest(expected=expected):
                def mutate(root: Path, relative=relative, before=before, after=after) -> None:
                    path = root / relative
                    text = path.read_text(encoding="utf-8")
                    self.assertIn(before, text)
                    path.write_text(text.replace(before, after, 1), encoding="utf-8")
                output = self.assert_rejected(mutate)
                self.assertIn(expected, output)

    def test_review_gap_disposition_schema_is_enforced(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "review.yaml"
            text = path.read_text(encoding="utf-8")
            before = "  - gap_id: GAP-001\n    decision: follow_up_task\n    rationale: \"\""
            self.assertIn(before, text)
            path.write_text(text.replace(before, "  - wrong_key: true", 1), encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("gap_disposition[0]", output)

    def test_defined_gap_classification_remains_accepted(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "report.yaml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("    classification: FOLLOW_UP", text)
        path.write_text(text.replace("    classification: FOLLOW_UP", "    classification: LOCAL", 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_newly_protected_canonical_fields_are_required(self) -> None:
        cases = [
            ("templates/task.yaml", "origin.type", "  type: user_request"),
            ("templates/task.yaml", "origin.task_id", '  task_id: ""'),
            ("templates/task.yaml", "origin.gap_id", '  gap_id: ""'),
            ("templates/task.yaml", "target.branch.role", "    role: integration"),
            ("templates/task.yaml", "execution_base.capture", "  capture: after_final_planning_commit"),
            ("templates/task.yaml", "architect_analysis_skills", "architect_analysis_skills: []"),
            ("templates/task.yaml", "external_skills.architect_analysis", "  architect_analysis: []"),
            ("templates/task.yaml", "external_skills.execution_required", "  execution_required: []"),
            ("templates/task.yaml", "external_skills.execution_recommended", "  execution_recommended: []"),
            ("templates/task.yaml", "objective", 'objective: ""'),
            ("templates/task.yaml", "scope.allowed_existing_files_or_components", '  allowed_existing_files_or_components:\n    - ""'),
            ("templates/task.yaml", "gap_policy.scope_expansion", "  scope_expansion: forbidden"),
            ("templates/task.yaml", "gap_policy.architecture_change", "  architecture_change: forbidden"),
            ("templates/task.yaml", "gap_policy.spec_change", "  spec_change: forbidden"),
            ("templates/task.yaml", "gap_policy.dependency_change", "  dependency_change: revised_contract_required"),
            ("templates/task.yaml", "gap_policy.public_contract_change", "  public_contract_change: revised_contract_required"),
            ("templates/task.yaml", "verification.authoritative_verification.required", "    required: false"),
            ("templates/task.yaml", "verification.authoritative_verification.mechanism", '    mechanism: ""'),
            ("templates/task.yaml", "verification.authoritative_verification.expected_signal", '    expected_signal: ""'),
            ("templates/report.yaml", "execution.branch.role", "    role: integration"),
            ("templates/report.yaml", "skill_library.repository", "  repository: phatnguyen03022001/agent-skills"),
            ("templates/report.yaml", "execution_skills_used.recommended", "  recommended: []"),
            ("templates/report.yaml", "execution_skills_used.external", "  external: []"),
            ("templates/report.yaml", "pushed", "pushed: false"),
            ("templates/report.yaml", "promoted_to_main", "promoted_to_main: false"),
            ("templates/report.yaml", "authoritative_verification.required", "  required: false"),
            ("templates/report.yaml", "authoritative_verification.performed", "  performed: false"),
            ("templates/report.yaml", "authoritative_verification.result", '  result: ""'),
            ("templates/report.yaml", "authoritative_verification.evidence", '  evidence: ""'),
            ("templates/report.yaml", "working_tree_after.clean", "  clean: false"),
            ("templates/report.yaml", "working_tree_after.summary", '  summary: ""'),
            ("templates/review.yaml", "promotion_readiness.reason", '  reason: ""'),
        ]
        for relative, dotted, before in cases:
            with self.subTest(path=dotted):
                def mutate(root: Path, relative=relative, before=before) -> None:
                    path = root / relative
                    text = path.read_text(encoding="utf-8")
                    needle = f"\n{before}\n"
                    self.assertIn(needle, text)
                    path.write_text(text.replace(needle, "\n", 1), encoding="utf-8")
                output = self.assert_rejected(mutate)
                self.assertIn(f"missing required path '{dotted}'", output)

    def test_review_ineligible_states_cannot_be_candidate_eligible(self) -> None:
        for state in ("REVISION_REQUIRED", "BLOCKED"):
            with self.subTest(state=state):
                _, root = self.fixture()
                path = root / "templates" / "review.yaml"
                text = path.read_text(encoding="utf-8")
                text = text.replace("state: REVISION_REQUIRED", f"state: {state}", 1)
                text = text.replace("  eligible_for_candidate_capture: false", "  eligible_for_candidate_capture: true", 1)
                path.write_text(text, encoding="utf-8")
                result = self.run_validator(root)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("only ACCEPTED review may be candidate-eligible", result.stdout + result.stderr)

    def test_review_accepted_eligibility_combinations_are_valid(self) -> None:
        for eligible in (True, False):
            with self.subTest(eligible=eligible):
                _, root = self.fixture()
                path = root / "templates" / "review.yaml"
                text = path.read_text(encoding="utf-8")
                text = text.replace("state: REVISION_REQUIRED", "state: ACCEPTED", 1)
                if eligible:
                    text = text.replace("  eligible_for_candidate_capture: false", "  eligible_for_candidate_capture: true", 1)
                path.write_text(text, encoding="utf-8")
                result = self.run_validator(root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_review_state_values_are_closed(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "review.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("state: REVISION_REQUIRED", "state: UNKNOWN", 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("unsupported review state", result.stdout + result.stderr)

    def test_exact_fifteen_skill_invariant_is_explicit(self) -> None:
        self.assertEqual(len(VALIDATOR_MODULE.EXPECTED_SKILLS), 15)

    def test_canonical_continuation_template_is_required_and_closed(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "continuation.yaml"
        self.assertTrue(path.is_file(), "missing canonical templates/continuation.yaml")
        text = path.read_text(encoding="utf-8")
        required = [
            "handoff_type: CONTINUATION", "phase: PROMOTION", "reviewed_report:",
            "promotion_candidate_head:", "expected_refs:", "prior_result:",
            "prior_lifecycle_state:", "next_authorized_action:",
        ]
        for token in required:
            self.assertIn(token, text)
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        path.unlink()
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing required protocol template: templates/continuation.yaml", result.stdout + result.stderr)

    def test_continuation_modes_are_closed_and_auto_until_stop_is_legal(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "task.yaml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("continuation_policy:\n  mode: MANUAL", text)
        path.write_text(text.replace("  mode: MANUAL", "  mode: AUTO_UNTIL_STOP", 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        _, root = self.fixture()
        path = root / "templates" / "task.yaml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("continuation_policy:\n  mode: MANUAL", text)
        path.write_text(text.replace("  mode: MANUAL", "  mode: FOREVER", 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("unsupported continuation mode", result.stdout + result.stderr)

    def test_malformed_continuation_policy_is_rejected(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8")
            before = "continuation_policy:\n  mode: MANUAL\n  stop_conditions:"
            self.assertIn(before, text)
            path.write_text(text.replace(before, "continuation_policy:\n  mode: MANUAL\n  stop_conditions: BLOCKED", 1), encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("stop_conditions", output)

    def test_capability_requirement_structure_is_phase_specific_and_closed(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8")
            before = "capability_requirements:\n  EXECUTION:\n    - repository_content_write"
            self.assertIn(before, text)
            path.write_text(text.replace(before, "capability_requirements:\n  EXECUTION: repository_content_write", 1), encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("capability_requirements.EXECUTION", output)

        def mutate_phase(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8")
            self.assertIn("  EXECUTION:", text)
            path.write_text(text.replace("  EXECUTION:", "  BANANA:", 1), encoding="utf-8")
        output = self.assert_rejected(mutate_phase)
        self.assertIn("unsupported capability phase", output)

    def test_release_authority_is_independent_from_git_promotion_authority(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "task.yaml"
        text = path.read_text(encoding="utf-8")
        release_block = (
            "release_authority:\n"
            "  create_version_tag: false\n"
            "  mutate_repository_metadata: false\n"
            "  publish_release: false"
        )
        self.assertIn(release_block, text)
        self.assertIn("  promote_to_main: false", text)
        path.write_text(text.replace("  promote_to_main: false", "  promote_to_main: true", 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        _, root = self.fixture()
        path = root / "templates" / "task.yaml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("  publish_release: false", text)
        path.write_text(text.replace("  publish_release: false", "  publish_release: no", 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("release_authority.publish_release", result.stdout + result.stderr)

    def test_legacy_expanded_protocol_v3_task_remains_valid(self) -> None:
        _, root = self.fixture()
        legacy = root / ".agent" / "tasks" / "TASK-0001" / "task.yaml"
        self.assertTrue(legacy.is_file())
        text = legacy.read_text(encoding="utf-8")
        self.assertNotIn("continuation_policy:", text)
        self.assertNotIn("release_authority:", text)
        (root / "templates" / "task.yaml").write_text(text, encoding="utf-8")
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_canonical_template_identity_consistency_includes_continuation(self) -> None:
        _, root = self.fixture()
        original_root = VALIDATOR_MODULE.ROOT
        try:
            VALIDATOR_MODULE.ROOT = root
            docs = {
                name: VALIDATOR_MODULE.load_protocol_document(f"templates/{name}.yaml")
                for name in ("task", "handoff", "report", "review", "continuation")
            }
        finally:
            VALIDATOR_MODULE.ROOT = original_root
        for name, doc in docs.items():
            self.assertIsNotNone(doc, name)
        task = docs["task"]
        handoff = docs["handoff"]
        report = docs["report"]
        review = docs["review"]
        continuation = docs["continuation"]
        assert task and handoff and report and review and continuation
        self.assertEqual(task["protocol_version"], 3)
        self.assertEqual(handoff["protocol_version"], 3)
        self.assertEqual(report["protocol_version"], 3)
        self.assertEqual(review["protocol_version"], 3)
        self.assertEqual(continuation["protocol_version"], 3)
        self.assertEqual(task["task_id"], handoff["task"]["id"])
        self.assertEqual(task["task_id"], report["task_id"])
        self.assertEqual(task["task_id"], review["task_id"])
        self.assertEqual(task["task_id"], continuation["task"]["id"])
        self.assertEqual(task["task_revision"], handoff["task"]["revision"])
        self.assertEqual(task["task_revision"], report["task_revision"])
        self.assertEqual(task["task_revision"], review["task_revision"])
        self.assertEqual(task["task_revision"], continuation["task"]["revision"])


if __name__ == "__main__":
    unittest.main()
