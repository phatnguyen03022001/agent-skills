#!/usr/bin/env python3
"""Adversarial regression tests for validate_skill_library.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
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
                    legacy = root / ".agent" / "tasks" / "TASK-0001" / "task.yaml"
                    path.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
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
            ("templates/report.yaml", '  - type: file_growth\n    path: ""\n    evidence: ""\n    recommendation: split_candidate\n    action_taken: none', '  - path: ""\n    evidence: ""\n    recommendation: split_candidate\n    action_taken: none', "structural_observations[0]"),
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
                text = text.replace(
                    "  exact_report_identity_verified: false",
                    "  exact_report_identity_verified: true",
                    1,
                )
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

    def test_current_git_workflow_identity_is_github_workflow(self) -> None:
        current = "github-workflow"
        legacy = "github-" + "dev-main-workflow"
        self.assertIn(current, VALIDATOR_MODULE.EXPECTED_SKILLS)
        self.assertNotIn(legacy, VALIDATOR_MODULE.EXPECTED_SKILLS)
        path = ROOT / current / "SKILL.md"
        self.assertTrue(path.is_file())
        self.assertFalse((ROOT / legacy).exists())
        metadata, _ = VALIDATOR_MODULE.parse_frontmatter(path)
        self.assertEqual(metadata.get("name"), current)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        catalog = readme.split("<!-- SKILL_CATALOG_START -->", 1)[1].split("<!-- SKILL_CATALOG_END -->", 1)[0]
        self.assertIn(f"| `{current}` | workflow |", catalog)
        self.assertNotIn(legacy, catalog)

    def test_canonical_continuation_template_is_required_and_closed(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "continuation.yaml"
        self.assertTrue(path.is_file(), "missing canonical templates/continuation.yaml")
        text = path.read_text(encoding="utf-8")
        required = [
            "handoff_type: CONTINUATION", "phase: PROMOTION", "reviewed_report:",
            "promotion_candidate_head:", "expected_refs:", "expected_state:",
            "prior_result:", "prior_lifecycle_state:", "next_authorized_action:",
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

    def test_continuation_stop_conditions_are_non_waivable(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "templates" / "task.yaml"
            text = path.read_text(encoding="utf-8")
            self.assertIn("    - STALE_STATE\n", text)
            path.write_text(text.replace("    - STALE_STATE\n", "", 1), encoding="utf-8")
        output = self.assert_rejected(mutate)
        self.assertIn("missing non-waivable continuation stop conditions", output)

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

    def test_task0002_durable_objective_and_material_decision_doctrine(self) -> None:
        architect = (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        combined = architect + protocol
        for token in (
            "durable user objective",
            "governing, not infallible",
            "compatible",
            "trade-off",
            "regression",
            "explicit informed override",
            "casual assent",
        ):
            self.assertIn(token, combined)

    def test_task0002_current_capability_and_pre_mutation_verification_doctrine(self) -> None:
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        executor = (ROOT / "executor" / "SKILL.md").read_text(encoding="utf-8")
        architect = (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
        combined = protocol + executor + architect
        for token in (
            "known capability",
            "currently available capability",
            "least-powerful",
            "bounded escalation",
            "before the first mutation",
            "native verification",
        ):
            self.assertIn(token, combined)

    def test_task0002_remote_truth_and_local_divergence_doctrine(self) -> None:
        workflow = (ROOT / "github-workflow" / "SKILL.md").read_text(encoding="utf-8")
        executor = (ROOT / "executor" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        combined = workflow + executor + protocol
        for token in (
            "authorized remote Git state",
            "canonical repository truth",
            "local state is an execution copy",
            "local ahead",
            "local dirty",
            "remote drift",
        ):
            self.assertIn(token, combined)
        for token in ("auto-push", "reset", "adopt"):
            self.assertIn(token, combined)

    def test_task0002_task_launch_is_architect_only_non_authority_ux(self) -> None:
        architect = (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        combined = architect + protocol + readme
        for token in (
            "TASK LAUNCH",
            "Chat",
            "Executor",
            "Model",
            "Effort",
            "Progress",
            "short explanation",
            "PROMPT TO COPY",
            "presentation only",
            "not persisted",
        ):
            self.assertIn(token, combined)
        self.assertFalse(any("launch" in path.name.lower() for path in (ROOT / "templates").iterdir()))

    def test_task0002_local_hygiene_results_are_closed(self) -> None:
        self.assertEqual(
            getattr(VALIDATOR_MODULE, "LOCAL_HYGIENE_RESULTS", frozenset()),
            frozenset({"PASS", "RETAINED_FOR_EVIDENCE", "BLOCKED"}),
        )
        report = (ROOT / "templates" / "report.yaml").read_text(encoding="utf-8")
        self.assertIn("local_hygiene:", report)
        self.assertIn("  result: PASS", report)

        _, root = self.fixture()
        path = root / "templates" / "report.yaml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("  result: PASS", text)
        path.write_text(text.replace("  result: PASS", "  result: UNKNOWN", 1), encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("unsupported local hygiene result", result.stdout + result.stderr)

    def test_task0002_local_hygiene_deletion_safety_markers(self) -> None:
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        executor = (ROOT / "executor" / "SKILL.md").read_text(encoding="utf-8")
        combined = protocol + executor
        for token in (
            "run-owned root",
            "realpath",
            "symlink",
            "filesystem root",
            "home",
            "workspace root",
            "repository root",
            "pre-existing",
            "sibling project",
            "arbitrary user-supplied",
            "RETAINED_FOR_EVIDENCE",
            "BLOCKED",
        ):
            self.assertIn(token, combined)

    def test_task0002_legacy_v3_report_without_local_hygiene_remains_valid(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "report.yaml"
        text = path.read_text(encoding="utf-8")
        marker = "local_hygiene:\n"
        self.assertIn(marker, text)
        start = text.index(marker)
        end_marker = "\ncommits_created:\n"
        end = text.index(end_marker, start)
        path.write_text(text[:start] + text[end + 1 :], encoding="utf-8")
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_task0003_architect_sequential_repository_switching(self) -> None:
        architect = (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        combined = architect + protocol
        self.assertNotIn("NEW_ARCHITECT_SESSION_REQUIRED", combined)
        for token in (
            "one active target repository",
            "close the current repository-specific phase",
            "explicitly identify the next `owner/repo`",
            "refresh canonical GitHub truth",
            "discard previous repository-specific assumptions",
            "simultaneous ambiguous active target is forbidden",
        ):
            self.assertIn(token, combined)

    def test_task0003_executor_rebind_requires_terminal_execution(self) -> None:
        executor = (ROOT / "executor" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        combined = executor + protocol
        for token in (
            "active task/repository binding remains immutable",
            "explicit terminal handoff/result",
            "previous evidence finalized",
            "no outstanding mutation authority carried forward",
            "fresh repository-local task",
            "fresh exact handoff",
            "fresh exact base HEAD",
        ):
            self.assertIn(token, combined)

    def test_task0003_authority_and_lineage_never_carry_between_repositories(self) -> None:
        executor = (ROOT / "executor" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        combined = executor + protocol
        for token in (
            "authority for repository A never grants authority for repository B",
            "report/review/verifier/promotion/release lineage remains repository-local",
            "repository identity",
            "branch identity",
            "task ID/revision",
            "base HEAD",
        ):
            self.assertIn(token, combined)

    def test_task0003_program_is_presentation_only(self) -> None:
        architect = (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        combined = architect + protocol + readme
        for token in (
            "PROGRAM",
            "ordered repository-local tasks",
            "presentation only",
            "not a universal multi-repository task authority",
            "shared mutable cross-repository authority",
        ):
            self.assertIn(token, combined)
        program = ROOT / "templates" / "program.generated.json"
        self.assertTrue(program.is_file())
        self.assertEqual(json.loads(program.read_text(encoding="utf-8"))["authority"], "NONE")

    def test_task0003_task_launch_fields_and_concrete_program_progress(self) -> None:
        architect = (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        combined = architect + protocol + readme
        for token in (
            "Chat",
            "Executor",
            "Model",
            "Effort",
            "Progress",
            "Giải thích",
            "PROMPT TO COPY",
            "Program 2/4 · agent-standards · execution",
            "fake percentages",
        ):
            self.assertIn(token, combined)

    def test_task0003_two_roles_and_no_orchestration_framework(self) -> None:
        architect = (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        combined = architect + protocol
        for token in (
            "two organizational roles",
            "Architect and Executor",
            "Executor specializations",
            "no orchestrator",
            "no registry",
            "no queue",
            "no database",
            "no workflow engine",
        ):
            self.assertIn(token, combined)
        self.assertEqual(len(VALIDATOR_MODULE.EXPECTED_SKILLS), 15)
        self.assertIn("Supported protocol version: **3**", protocol)


class Task0004GovernanceTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_ac1_operator_profile_is_generic_context_not_authority(self) -> None:
        combined = self.read("architect/SKILL.md") + self.read("protocols/TASK_PROTOCOL.md")
        for token in (
            "optional operator profile",
            "host/session/operator",
            "durable preference/environment context",
            "not target-repository factual or mutation authority",
            "explicit current user decisions",
        ):
            self.assertIn(token, combined)
        for forbidden in ("architect-profile", "MacBook", "M3"):
            self.assertNotIn(forbidden, combined)

    def test_ac1_architect_role_is_provider_neutral(self) -> None:
        architect = self.read("architect/SKILL.md")
        for forbidden in (
            "Architect remains ChatGPT",
            "Architect is ChatGPT",
            "Architect must be ChatGPT",
            "Architect always uses ChatGPT",
        ):
            self.assertNotIn(forbidden, architect)

    def test_ac2_prompt_to_copy_is_compact_authority_locator(self) -> None:
        combined = (
            self.read("architect/SKILL.md")
            + self.read("protocols/TASK_PROTOCOL.md")
            + self.read("README.md")
        )
        for token in (
            "authority locator",
            "target owner/repo",
            "task ID/revision/path",
            "exact base HEAD",
            "current phase",
            "resolve canonical authority",
            "Do not duplicate",
        ):
            self.assertIn(token, combined)

    def test_ac3_executor_binding_terminal_is_not_task_lifecycle(self) -> None:
        combined = self.read("executor/SKILL.md") + self.read("protocols/TASK_PROTOCOL.md")
        for token in (
            "Executor-binding terminal",
            "whole-task lifecycle",
            "NEEDS_REVIEW",
            "STALE_STATE",
            "AUTHORITY_REQUIRED",
            "CURRENT_PHASE_CAPABILITY_UNAVAILABLE",
            "no mutation authority remains",
            "does not imply acceptance, promotion, or release",
        ):
            self.assertIn(token, combined)

    def test_ac4_one_current_architect_owns_final_judgment(self) -> None:
        combined = (
            self.read("architect/SKILL.md")
            + self.read("protocols/TASK_PROTOCOL.md")
            + self.read("contracts/ARCHITECT_REVIEW.md")
        )
        for token in (
            "one current governing Architect",
            "ACCEPT/REJECT/REVISE",
            "Executor specialization",
            "advisory evidence",
            "designated verifier",
        ):
            self.assertIn(token, combined)

    def test_ac5_execution_lanes_are_risk_proportional(self) -> None:
        combined = self.read("architect/SKILL.md") + self.read("protocols/TASK_PROTOCOL.md")
        for token in (
            "DIRECT",
            "BOUNDED",
            "HIGH_ASSURANCE",
            "small reversible low-risk",
            "normal task",
            "release-critical",
            "DIRECT never bypasses",
            "HIGH_ASSURANCE must not become the default",
        ):
            self.assertIn(token, combined)

    def test_ac6_git_topologies_are_target_authoritative(self) -> None:
        combined = (
            self.read("github-workflow/SKILL.md")
            + self.read("protocols/TASK_PROTOCOL.md")
        )
        for token in (
            "MAIN_ONLY",
            "DEV_MAIN",
            "DEV_STAGING_MAIN",
            "explicitly activated",
            "Never infer or create staging",
            "repository-specific branch policy",
        ):
            self.assertIn(token, combined)

    def test_ac7_normative_external_authority_is_immutable(self) -> None:
        combined = self.read("architect/SKILL.md") + self.read("protocols/TASK_PROTOCOL.md")
        for token in (
            "external repository used as normative authority",
            "immutable revision",
            "before mutation",
            "research/reference evidence",
            "does not become normative authority",
        ):
            self.assertIn(token, combined)

    def test_ac8_evidence_dedup_keeps_legacy_v3(self) -> None:
        protocol = self.read("protocols/TASK_PROTOCOL.md")
        for token in (
            "unconditional protocol boilerplate",
            "task-specific material authority",
            "record evidence once",
            "legacy inline evidence",
            "no parallel compact schema",
        ):
            self.assertIn(token, protocol)
        self.assertIn("Supported protocol version: **3**", protocol)

    def test_ac9_design_readiness_is_material_and_proportional(self) -> None:
        combined = (
            self.read("architect/SKILL.md")
            + self.read("gap-analysis/SKILL.md")
            + self.read("design-review/SKILL.md")
            + self.read("protocols/TASK_PROTOCOL.md")
        )
        for token in (
            "material-design-readiness",
            "applicable target product/design authority",
            "material missing decisions",
            "consequential implementation",
            "trivial, mechanical, reversible, or well-specified",
        ):
            self.assertIn(token, combined)

    def test_ac10_operator_attention_is_constrained_resource(self) -> None:
        combined = self.read("architect/SKILL.md") + self.read("protocols/TASK_PROTOCOL.md")
        for token in (
            "operator attention/manual labor",
            "constrained resource",
            "manual command/RPC bridge",
            "unavailable capability",
            "destructive/irreversible authority",
            "material paid-cost approval",
        ):
            self.assertIn(token, combined)

    def test_ac11_maintenance_defaults_to_no_change(self) -> None:
        combined = (
            self.read("architect/SKILL.md")
            + self.read("simplicity/SKILL.md")
            + self.read("protocols/TASK_PROTOCOL.md")
            + self.read("README.md")
        )
        for token in (
            "NO CHANGE REQUIRED",
            "evidence-backed defect",
            "recurring missing capability",
            "security issue",
            "compatibility failure",
            "material cost/usability/maintainability regression",
            "smallest safe correction",
            "Preference, novelty, elegance, architectural fashion, and hypothetical future scale",
        ):
            self.assertIn(token, combined)

    def test_ac12_fifteen_skill_taxonomy_is_closed_by_default(self) -> None:
        combined = (
            self.read("architect/SKILL.md")
            + self.read("simplicity/SKILL.md")
            + self.read("README.md")
        )
        for token in (
            "15-skill taxonomy",
            "closed by default",
            "materially distinct recurring responsibility",
            "exceptional correctness/security",
            "arbitrary numeric threshold",
        ):
            self.assertIn(token, combined)
        self.assertEqual(len(VALIDATOR_MODULE.EXPECTED_SKILLS), 15)
        self.assertEqual(len(list(ROOT.rglob("SKILL.md"))), 15)


class Task0007ProtocolCorrectnessTests(unittest.TestCase):
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

    def write_continuation(
        self,
        root: Path,
        *,
        refs: list[tuple[str, str]] | None = None,
        legacy: bool = False,
        phase: str,
        action: str,
        target_ref: str | None = None,
        lifecycle: str = "ACCEPTED",
        prior_lifecycle: str = "ACCEPTED",
        prior_result: str = "ACCEPTED",
    ) -> None:
        if legacy:
            refs_yaml = (
                "expected_refs:\n"
                "  dev: \"<exact expected dev SHA>\"\n"
                "  main: \"<exact expected main SHA>\"\n"
            )
        elif refs:
            refs_yaml = "expected_refs:\n" + "".join(
                f"  - ref: {ref}\n    commit: \"{commit}\"\n" for ref, commit in refs
            )
        else:
            refs_yaml = "expected_refs: []\n"
        target_yaml = f"promotion_target_ref: {target_ref}\n\n" if target_ref is not None else ""
        text = (
            "protocol_version: 3\n"
            "handoff_type: CONTINUATION\n\n"
            "task:\n"
            "  id: TASK-0001\n"
            "  revision: 1\n"
            "  path: .agent/tasks/TASK-0001/task.yaml\n\n"
            f"phase: {phase}\n\n"
            "reviewed_report:\n"
            "  repository: owner/repo\n"
            "  path: .agent/tasks/TASK-0001/report.yaml\n"
            "  commit: \"<exact commit containing reviewed report>\"\n"
            "  report_revision: 1\n\n"
            "promotion_candidate_head: \"<exact accepted-lineage candidate SHA>\"\n\n"
            f"{refs_yaml}\n"
            f"{target_yaml}"
            "expected_state:\n"
            f"  lifecycle: {lifecycle}\n\n"
            f"prior_result: {prior_result}\n"
            f"prior_lifecycle_state: {prior_lifecycle}\n"
            f"next_authorized_action: {action}\n"
        )
        (root / "templates" / "continuation.yaml").write_text(text, encoding="utf-8")

    def assert_passes(self, root: Path) -> None:
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_rejected(self, root: Path, expected: str) -> None:
        result = self.run_validator(root)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(expected, output)

    def test_task0007_canonical_topologies_are_topology_neutral(self) -> None:
        cases = [
            ([], "REVIEW", "STOP", None),
            ([("refs/heads/trunk", "trunk-sha")], "PROMOTION", "PROMOTE_TARGET_REF", "refs/heads/trunk"),
            ([
                ("refs/heads/integration", "integration-sha"),
                ("refs/heads/stable", "stable-sha"),
            ], "PROMOTION", "PROMOTE_TARGET_REF", "refs/heads/stable"),
            ([
                ("refs/heads/build", "build-sha"),
                ("refs/heads/candidate", "candidate-sha"),
                ("refs/heads/production", "production-sha"),
            ], "PROMOTION", "PROMOTE_TARGET_REF", "refs/heads/production"),
        ]
        for refs, phase, action, target in cases:
            with self.subTest(refs=refs):
                _, root = self.fixture()
                self.write_continuation(
                    root,
                    refs=refs,
                    phase=phase,
                    action=action,
                    target_ref=target,
                )
                self.assert_passes(root)

    def test_task0007_legacy_expanded_v3_continuation_remains_valid(self) -> None:
        _, root = self.fixture()
        self.write_continuation(
            root,
            legacy=True,
            phase="PROMOTION",
            action="PROMOTE_TO_MAIN",
        )
        self.assert_passes(root)

    def test_task0007_canonical_promotion_requires_exact_target_ref(self) -> None:
        _, root = self.fixture()
        self.write_continuation(
            root,
            refs=[("refs/heads/stable", "stable-sha")],
            phase="PROMOTION",
            action="PROMOTE_TARGET_REF",
            target_ref="refs/heads/other",
        )
        self.assert_rejected(root, "promotion_target_ref must identify a ref present in expected_refs")

        _, root = self.fixture()
        self.write_continuation(
            root,
            refs=[("refs/heads/stable", "stable-sha")],
            phase="PROMOTION",
            action="PROMOTE_TO_MAIN",
        )
        self.assert_rejected(root, "PROMOTE_TO_MAIN is legacy compatibility input")

    def test_task0007_lifecycle_snapshot_mismatch_is_rejected(self) -> None:
        _, root = self.fixture()
        self.write_continuation(
            root,
            legacy=True,
            phase="REVIEW",
            action="REQUEST_ARCHITECT_REVIEW",
            lifecycle="ACCEPTED",
            prior_lifecycle="VERIFIED",
        )
        self.assert_rejected(root, "expected_state.lifecycle must equal prior_lifecycle_state")

    def test_task0007_prior_result_is_not_forced_to_lifecycle(self) -> None:
        _, root = self.fixture()
        self.write_continuation(
            root,
            refs=[],
            phase="REVIEW",
            action="STOP",
            prior_result="NEEDS_REVIEW",
        )
        self.assert_passes(root)

    def test_task0007_phase_action_pairs_are_relational(self) -> None:
        _, root = self.fixture()
        self.write_continuation(
            root,
            legacy=True,
            phase="REVIEW",
            action="PUBLISH_RELEASE",
        )
        self.assert_rejected(root, "is not valid for continuation phase")

        valid_pairs = [
            ("REVIEW", "REQUEST_ARCHITECT_REVIEW"),
            ("REVIEW", "STOP"),
            ("VERIFICATION", "RUN_AUTHORITATIVE_VERIFICATION"),
            ("VERIFICATION", "STOP"),
            ("RELEASE", "CREATE_VERSION_TAG"),
            ("RELEASE", "MUTATE_REPOSITORY_METADATA"),
            ("RELEASE", "PUBLISH_RELEASE"),
            ("RELEASE", "FINAL_VERIFY"),
            ("RELEASE", "STOP"),
        ]
        for phase, action in valid_pairs:
            with self.subTest(phase=phase, action=action):
                _, root = self.fixture()
                self.write_continuation(
                    root,
                    legacy=True,
                    phase=phase,
                    action=action,
                )
                self.assert_passes(root)

    def test_task0007_review_acceptance_requires_exact_report_identity(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "review.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("state: REVISION_REQUIRED", "state: ACCEPTED", 1), encoding="utf-8")
        self.assert_rejected(root, "ACCEPTED review requires independence.exact_report_identity_verified=true")

        _, root = self.fixture()
        path = root / "templates" / "review.yaml"
        text = path.read_text(encoding="utf-8")
        text = text.replace("state: REVISION_REQUIRED", "state: ACCEPTED", 1)
        text = text.replace(
            "  exact_report_identity_verified: false",
            "  exact_report_identity_verified: true",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assert_passes(root)

        for state in ("REVISION_REQUIRED", "BLOCKED"):
            with self.subTest(nonaccepted=state):
                _, root = self.fixture()
                path = root / "templates" / "review.yaml"
                text = path.read_text(encoding="utf-8")
                if state == "BLOCKED":
                    text = text.replace("state: REVISION_REQUIRED", "state: BLOCKED", 1)
                path.write_text(text, encoding="utf-8")
                self.assert_passes(root)

    def test_task0007_canonical_docs_expose_topology_neutral_terms(self) -> None:
        continuation = (ROOT / "templates" / "continuation.yaml").read_text(encoding="utf-8")
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        workflow = (ROOT / "github-workflow" / "SKILL.md").read_text(encoding="utf-8")
        combined = continuation + protocol + workflow
        for token in (
            "PROMOTE_TARGET_REF",
            "promotion_target_ref",
            "target-authoritative",
            "compatibility input",
        ):
            self.assertIn(token, combined)
        self.assertIn("  - ref: refs/heads/integration", continuation)
        self.assertNotIn("expected_refs:\n  dev:", continuation)
        self.assertNotIn("next_authorized_action: PROMOTE_TO_MAIN", continuation)


class Task0011GeneratedProgramTests(unittest.TestCase):
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

    def mutate_program(self, root: Path, mutate) -> None:
        path = root / "templates" / "program.generated.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        mutate(document)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def assert_program_rejected(self, mutate, expected: str) -> None:
        _, root = self.fixture()
        self.mutate_program(root, mutate)
        result = self.run_validator(root)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(expected, output)

    def test_task0011_canonical_generated_program_is_non_authoritative_and_valid(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "program.generated.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(document["protocol_version"], 3)
        self.assertEqual(document["artifact_type"], "GENERATED_PROGRAM")
        self.assertEqual(document["authority"], "NONE")
        self.assertEqual(document["invalidation"], "FULL_REGENERATION_ON_MATERIAL_INPUT_CHANGE")
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_task0011_generated_program_rejects_invalid_graph_coverage_and_authority_shape(self) -> None:
        def duplicate_id(document) -> None:
            document["items"].append(json.loads(json.dumps(document["items"][0])))

        def broken_dependency(document) -> None:
            document["items"][0]["depends_on"] = ["ITEM-999"]

        def cycle(document) -> None:
            second = json.loads(json.dumps(document["items"][0]))
            second["id"] = "ITEM-002"
            second["depends_on"] = ["ITEM-001"]
            document["items"][0]["depends_on"] = ["ITEM-002"]
            document["items"].append(second)

        def missing_source_revision(document) -> None:
            document["synthesis"]["target"].pop("source_revision")

        def malformed_evidence(document) -> None:
            document["items"][0]["required_evidence"] = "not-a-list"

        def mutable_state(document) -> None:
            document["items"][0]["status"] = "READY"

        def uncovered_ref(document) -> None:
            document["coverage"]["required_refs"].append("TARGET:design#uncovered")

        def authority_escalation(document) -> None:
            document["authority"] = "TASK"

        cases = [
            (duplicate_id, "duplicate generated item id"),
            (broken_dependency, "depends on unknown item"),
            (cycle, "dependency graph must be acyclic"),
            (missing_source_revision, "synthesis.target"),
            (malformed_evidence, "required_evidence"),
            (mutable_state, "unexpected fields ['status']"),
            (uncovered_ref, "neither covered nor excluded"),
            (authority_escalation, "path 'authority' must equal 'NONE'"),
        ]
        for mutate, expected in cases:
            with self.subTest(expected=expected):
                self.assert_program_rejected(mutate, expected)

    def test_task0011_bounded_coverage_exclusion_is_valid(self) -> None:
        _, root = self.fixture()

        def mutate(document) -> None:
            ref = "TARGET:design#excluded"
            document["coverage"]["required_refs"].append(ref)
            document["coverage"]["exclusions"].append({
                "ref": ref,
                "rationale": "Explicitly outside this generated implementation program slice.",
            })

        self.mutate_program(root, mutate)
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_task0011_doctrine_preserves_judgment_full_regeneration_and_jit_task_authority(self) -> None:
        protocol = (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        architect = (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        combined = protocol + architect + readme
        for token in (
            "authority: NONE",
            "mathematically unique DAG",
            "whole generated program stale",
            "full regeneration",
            "just in time",
            "one active Executor binding",
        ):
            self.assertIn(token, combined)
        for forbidden in (
            "affected-region recomputation",
            "dependency cache",
            "planner service",
        ):
            self.assertIn(forbidden, protocol)


class Task0020GovernanceOwnershipTests(unittest.TestCase):
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

    def load_task(self, root: Path) -> dict[str, object]:
        original_root = VALIDATOR_MODULE.ROOT
        try:
            VALIDATOR_MODULE.ROOT = root
            document = VALIDATOR_MODULE.load_protocol_document("templates/task.yaml")
        finally:
            VALIDATOR_MODULE.ROOT = original_root
        assert document is not None
        return document

    def remove_sparse_optional_controls(self, root: Path) -> None:
        path = root / "templates" / "task.yaml"
        lines = path.read_text(encoding="utf-8").splitlines()
        output: list[str] = []
        skip_structure = False
        skip_control = False
        for line in lines:
            if line == "  expected_files_are_restrictive: true":
                continue
            if line == "structure_policy:":
                skip_structure = True
                continue
            if skip_structure and line == "continuation_policy:":
                skip_structure = False
            if skip_structure:
                continue
            if line in {"continuation_policy:", "capability_requirements:", "release_authority:"}:
                skip_control = True
                continue
            if skip_control and line and not line.startswith(" "):
                skip_control = False
            if skip_control:
                continue
            output.append(line)
        path.write_text("\n".join(output) + "\n", encoding="utf-8")

    def test_sparse_implementation_controls_normalize_to_bounded_local_defaults(self) -> None:
        _, root = self.fixture()
        self.remove_sparse_optional_controls(root)
        document = self.load_task(root)
        normalized = VALIDATOR_MODULE.normalize_task_document(document)

        scope = normalized["scope"]
        structure = normalized["structure_policy"]
        unlisted = structure["unlisted_new_files"]
        self.assertFalse(scope["expected_files_are_restrictive"])
        self.assertEqual(structure["expected_new_files"], [])
        self.assertTrue(unlisted["allowed"])
        self.assertEqual(unlisted["max"], -1)
        self.assertEqual(unlisted["within"], [])
        self.assertFalse(structure["allow_new_top_level_directories"])
        self.assertFalse(structure["allow_new_shared_modules"])
        self.assertEqual(normalized["continuation_policy"]["mode"], "MANUAL")
        self.assertEqual(normalized["capability_requirements"], {})
        self.assertEqual(
            normalized["release_authority"],
            {
                "create_version_tag": False,
                "mutate_repository_metadata": False,
                "publish_release": False,
            },
        )
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_expanded_v3_restrictions_remain_restrictive_after_normalization(self) -> None:
        _, root = self.fixture()
        legacy = root / ".agent" / "tasks" / "TASK-0001" / "task.yaml"
        self.assertTrue(legacy.is_file())
        (root / "templates" / "task.yaml").write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
        document = self.load_task(root)
        normalized = VALIDATOR_MODULE.normalize_task_document(document)
        self.assertTrue(normalized["scope"]["expected_files_are_restrictive"])
        self.assertFalse(normalized["structure_policy"]["unlisted_new_files"]["allowed"])
        self.assertEqual(normalized["structure_policy"]["unlisted_new_files"]["max"], 0)
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_positive_authority_still_fails_closed(self) -> None:
        _, root = self.fixture()
        self.remove_sparse_optional_controls(root)
        path = root / "templates" / "task.yaml"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "  allowed_existing_files_or_components:\n    - \"\"\n",
            "  allowed_existing_files_or_components_missing:\n    - \"\"\n",
            1,
        )
        path.write_text(text, encoding="utf-8")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("missing required path 'scope.allowed_existing_files_or_components'", result.stdout + result.stderr)

    def test_template_serializes_sparse_v3_without_a_second_task_dialect(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "task.yaml"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("task-lite", text)
        self.assertNotIn("task-compact", text)
        self.assertNotIn("protocol_version: 4", text)
        self.assertNotIn("  expected_files_are_restrictive:", text)
        self.assertNotIn("structure_policy:", text)
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class Task0021EvidenceLifecycleTests(unittest.TestCase):
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

    def remove_top_level_block(self, text: str, key: str) -> str:
        lines = text.splitlines(keepends=True)
        matches = [index for index, line in enumerate(lines) if line == f"{key}:\n"]
        if not matches:
            return text
        start = matches[0]
        end = start + 1
        while end < len(lines) and (not lines[end].strip() or lines[end][0].isspace()):
            end += 1
        return "".join(lines[:start] + lines[end:])

    def test_compact_report_can_omit_changed_file_enumeration(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "report.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text(self.remove_top_level_block(text, "changed_files"), encoding="utf-8")

        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_default_report_template_omits_operational_timing(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "report.yaml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("# operational_timing:\n", text)
        document = VALIDATOR_MODULE.load_protocol_document("templates/report.yaml")
        assert document is not None
        self.assertNotIn("operational_timing", document)

        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_report_accepts_explicit_two_timestamp_timing(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "report.yaml"
        text = self.remove_top_level_block(path.read_text(encoding="utf-8"), "operational_timing")
        text += (
            "\noperational_timing:\n"
            '  started_at_utc: "2026-09-03T10:00:00Z"\n'
            '  terminal_decision_at_utc: "2026-09-03T10:05:00Z"\n'
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_report_rejects_partial_operational_timing(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "report.yaml"
        text = self.remove_top_level_block(path.read_text(encoding="utf-8"), "operational_timing")
        text += '\noperational_timing:\n  started_at_utc: "2026-09-03T10:00:00Z"\n'
        path.write_text(text, encoding="utf-8")

        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("operational_timing", result.stdout + result.stderr)

    def test_report_rejects_non_utc_or_derived_timing_fields(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "report.yaml"
        text = self.remove_top_level_block(path.read_text(encoding="utf-8"), "operational_timing")
        text += (
            "\noperational_timing:\n"
            '  started_at_utc: "2026-09-03T17:00:00+07:00"\n'
            '  terminal_decision_at_utc: "2026-09-03T10:05:00Z"\n'
            "  elapsed_seconds: 300\n"
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("operational_timing", result.stdout + result.stderr)

    def test_review_rejects_partial_operational_timing(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "review.yaml"
        text = path.read_text(encoding="utf-8")
        text += '\noperational_timing:\n  started_at_utc: "2026-09-03T10:00:00Z"\n'
        path.write_text(text, encoding="utf-8")

        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("operational_timing", result.stdout + result.stderr)

    def test_review_accepts_explicit_two_timestamp_timing(self) -> None:
        _, root = self.fixture()
        path = root / "templates" / "review.yaml"
        text = path.read_text(encoding="utf-8")
        text += (
            "\noperational_timing:\n"
            '  started_at_utc: "2026-09-03T10:00:00Z"\n'
            '  terminal_decision_at_utc: "2026-09-03T10:05:00Z"\n'
        )
        path.write_text(text, encoding="utf-8")

        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_review_procedure_is_evidence_first_and_trigger_expanded(self) -> None:
        combined = (
            (ROOT / "architect" / "SKILL.md").read_text(encoding="utf-8")
            + (ROOT / "contracts" / "ARCHITECT_REVIEW.md").read_text(encoding="utf-8")
            + (ROOT / "protocols" / "TASK_PROTOCOL.md").read_text(encoding="utf-8")
        )
        for token in (
            "evidence-first",
            "exact report/task identity",
            "candidate diff boundary",
            "acceptance evidence",
            "deviations/gaps",
            "material risk triggers",
            "stop when material predicates are proven",
            "Deep implementation reconstruction occurs only for",
            "preference-only revision",
            "material consequence or contract/risk violation",
            "omitted by default",
            "explicitly requests",
        ):
            self.assertIn(token, combined)


EVAL_CORPUS = Path("scripts/fixtures/governance_eval_corpus.json")
EVAL_CASE_FIELDS = frozenset({
    "case_id",
    "pair_id",
    "scenario",
    "evaluation_kind",
    "expected_outcome",
    "rationale",
})
EVAL_KINDS = frozenset({"over_governance", "under_governance"})
EVAL_OUTCOMES = frozenset({"ALLOW_LOCAL", "ESCALATE_TO_ARCHITECT"})
EVAL_PAIR_MIN = 6
EVAL_PAIR_MAX = 8
TARGET_RULE_LEAKAGE = re.compile(r"\b(?:ielts|sf|salesforce)\b", re.IGNORECASE)


def eval_corpus_errors(document: object) -> list[str]:
    errors: list[str] = []
    if type(document) is not dict:
        return ["corpus must be an object"]
    if set(document) != {"cases"}:
        errors.append("corpus must contain only the cases field")
    cases = document.get("cases")
    if type(cases) is not list:
        return errors + ["cases must be a list"]

    case_ids: set[str] = set()
    pairs: dict[str, list[dict[str, object]]] = {}
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if type(case) is not dict:
            errors.append(f"{label} must be an object")
            continue
        missing = sorted(EVAL_CASE_FIELDS - set(case))
        unexpected = sorted(set(case) - EVAL_CASE_FIELDS)
        if missing:
            errors.append(f"{label} missing fields {missing}")
        if unexpected:
            errors.append(f"{label} has unexpected fields {unexpected}")
        if missing or unexpected:
            continue
        for field in EVAL_CASE_FIELDS:
            value = case[field]
            if type(value) is not str or not value.strip():
                errors.append(f"{label}.{field} must be a non-empty string")
        case_id = case["case_id"]
        pair_id = case["pair_id"]
        kind = case["evaluation_kind"]
        outcome = case["expected_outcome"]
        if type(case_id) is str:
            if case_id in case_ids:
                errors.append(f"duplicate case_id {case_id!r}")
            case_ids.add(case_id)
        if type(pair_id) is str:
            pairs.setdefault(pair_id, []).append(case)
        if type(kind) is str and kind not in EVAL_KINDS:
            errors.append(f"{label}.evaluation_kind has unsupported value {kind!r}")
        if type(outcome) is str and outcome not in EVAL_OUTCOMES:
            errors.append(f"{label}.expected_outcome has unsupported value {outcome!r}")

    pair_count = len(pairs)
    if not EVAL_PAIR_MIN <= pair_count <= EVAL_PAIR_MAX:
        errors.append(f"pair count must be between {EVAL_PAIR_MIN} and {EVAL_PAIR_MAX}")
    for pair_id, pair_cases in pairs.items():
        if len(pair_cases) != 2:
            errors.append(f"pair {pair_id!r} must contain exactly two cases")
            continue
        kinds = {case["evaluation_kind"] for case in pair_cases}
        if kinds != EVAL_KINDS:
            errors.append(f"pair {pair_id!r} must contain one case of each evaluation kind")

    serialized = json.dumps(document, ensure_ascii=False)
    leaked = sorted({match.group(0).lower() for match in TARGET_RULE_LEAKAGE.finditer(serialized)})
    if leaked:
        errors.append(f"target-specific rule leakage: {leaked}")
    return errors


class Task0022GovernanceEvaluationTests(unittest.TestCase):
    def load_corpus(self, root: Path = ROOT) -> object:
        path = root / EVAL_CORPUS
        self.assertTrue(path.is_file(), f"missing evaluation corpus: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def assert_corpus_rejected(self, mutate, expected: str) -> None:
        document = json.loads(json.dumps(self.load_corpus()))
        mutate(document)
        errors = eval_corpus_errors(document)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_canonical_corpus_is_small_generic_and_integrity_valid(self) -> None:
        document = self.load_corpus()
        errors = eval_corpus_errors(document)
        self.assertEqual(errors, [])
        assert isinstance(document, dict)
        cases = document["cases"]
        assert isinstance(cases, list)
        self.assertEqual(len(cases), len({case["case_id"] for case in cases}))
        self.assertEqual({case["evaluation_kind"] for case in cases}, EVAL_KINDS)
        self.assertEqual({case["expected_outcome"] for case in cases}, EVAL_OUTCOMES)

    def test_integrity_rejects_duplicate_case_ids(self) -> None:
        self.assert_corpus_rejected(
            lambda document: document["cases"].__setitem__(1, document["cases"][0]),
            "duplicate case_id",
        )

    def test_integrity_rejects_incomplete_pairs(self) -> None:
        self.assert_corpus_rejected(
            lambda document: document["cases"].pop(),
            "must contain exactly two cases",
        )

    def test_integrity_rejects_unsupported_kind_and_outcome(self) -> None:
        def mutate(document: dict[str, object]) -> None:
            case = document["cases"][0]
            case["evaluation_kind"] = "materiality_classifier"
            case["expected_outcome"] = "PRESCRIBE_WORDING"

        self.assert_corpus_rejected(mutate, "unsupported value")

    def test_integrity_rejects_missing_required_fields(self) -> None:
        def mutate(document: dict[str, object]) -> None:
            document["cases"][0].pop("rationale")

        self.assert_corpus_rejected(mutate, "missing fields")

    def test_integrity_rejects_malformed_required_fields(self) -> None:
        def mutate(document: dict[str, object]) -> None:
            document["cases"][0]["scenario"] = "   "

        self.assert_corpus_rejected(mutate, "must be a non-empty string")

    def test_integrity_rejects_pair_count_drift(self) -> None:
        def mutate(document: dict[str, object]) -> None:
            document["cases"].extend(
                [
                    {
                        **document["cases"][0],
                        "case_id": "extra-local",
                        "pair_id": "extra-pair",
                        "evaluation_kind": "over_governance",
                    },
                    {
                        **document["cases"][1],
                        "case_id": "extra-material",
                        "pair_id": "extra-pair",
                        "evaluation_kind": "under_governance",
                    },
                    {
                        **document["cases"][0],
                        "case_id": "overflow-local",
                        "pair_id": "overflow-pair",
                        "evaluation_kind": "over_governance",
                    },
                    {
                        **document["cases"][1],
                        "case_id": "overflow-material",
                        "pair_id": "overflow-pair",
                        "evaluation_kind": "under_governance",
                    },
                ]
            )

        self.assert_corpus_rejected(mutate, "pair count")

    def test_integrity_rejects_target_specific_rule_leakage(self) -> None:
        def mutate(document: dict[str, object]) -> None:
            document["cases"][0]["scenario"] = "Use IELTS-specific product semantics."

        self.assert_corpus_rejected(mutate, "target-specific rule leakage")


if __name__ == "__main__":
    unittest.main()
