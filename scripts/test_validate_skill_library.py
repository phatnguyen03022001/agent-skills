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
        workflow = (ROOT / "github-dev-main-workflow" / "SKILL.md").read_text(encoding="utf-8")
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
        end_marker = "\nchanged_files:\n"
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
        self.assertFalse(any("program" in path.name.lower() for path in (ROOT / "templates").iterdir()))

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
            self.read("github-dev-main-workflow/SKILL.md")
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


if __name__ == "__main__":
    unittest.main()
