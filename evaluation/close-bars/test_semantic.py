"""Check the semantic-evaluation inputs and harness, not model answer quality.

Run with: python3 -m unittest discover -s evaluation/close-bars -p 'test_*.py' -v
No model calls, source-repository mutations, or automatic semantic scoring occur.
"""

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CASES = HERE / "cases.json"
SPEC = importlib.util.spec_from_file_location("prepare_eval", HERE / "prepare_eval.py")
prepare_eval = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare_eval)


class CasesTests(unittest.TestCase):
    def setUp(self):
        self.data, self.digest = prepare_eval.load_cases(CASES)

    def load_data(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return prepare_eval.load_cases(path)

    def test_schema_ids_and_both_independent_skills(self):
        self.assertEqual(self.data["schema_version"], 1)
        self.assertEqual([c["id"] for c in self.data["cases"]], [f"P{i}" for i in range(1, 11)])
        self.assertEqual({c["skill"] for c in self.data["cases"]}, set(prepare_eval.SKILLS))
        self.assertEqual(self.digest, hashlib.sha256(CASES.read_bytes()).hexdigest())
        for case in self.data["cases"]:
            self.assertTrue(case["task_prompt"])
            self.assertTrue(case["acceptance_criteria"])
            self.assertTrue(case["material_failure_criteria"])

    def test_source_values_controls_and_targeted_regressions_are_retained(self):
        cases = {case["id"]: case for case in self.data["cases"]}
        for case_id, fragments in {
            "P1": ["42.1%", "42.4%"],
            "P2": ["51.2", "51.4", "51 s"],
            "P3": ["42%", "nearest whole percent"],
            "P4": ["adjacent table", "no value labels", "No rendering supplied"],
            "P5": ["42–43", "significantly better"],
            "P6": ["control 0", "test 2", "equal-exposure"],
            "P7": ["60-category", "broad-pattern overview", "accessible table"],
            "P8": ["−3.2", "−3.4", "test-minus-control"],
            "P9": ["51.24", "51.36", "one-decimal"],
            "P10": ["+0.3% relative to control", "percentage-point", "relative percentage"],
        }.items():
            with self.subTest(case_id=case_id):
                for fragment in fragments:
                    self.assertIn(fragment, cases[case_id]["task_prompt"])
        self.assertIn("no established material defect", " ".join(cases["P4"]["acceptance_criteria"]))
        self.assertIn("unnecessary", " ".join(cases["P7"]["acceptance_criteria"]))

    def test_malformed_schema_and_case_fields_are_rejected(self):
        malformed = [None, [], {}, {**self.data, "schema_version": 2}, {**self.data, "schema_version": True}]
        malformed.extend({**self.data, key: value} for key, value in [
            ("instructions", " "), ("review_instructions", []),
            ("review_instructions", "not a list"), ("cases", []), ("cases", {}),
        ])
        for key, value in [
            ("id", "P0"), ("id", "P01"), ("id", None),
            ("skill", "unknown-skill"), ("skill", []), ("task_prompt", ""),
            ("acceptance_criteria", []), ("acceptance_criteria", [None]),
            ("material_failure_criteria", "not a list"),
        ]:
            data = copy.deepcopy(self.data)
            data["cases"][0][key] = value
            malformed.append(data)
        missing = copy.deepcopy(self.data)
        del missing["cases"][0]["title"]
        malformed.append(missing)
        duplicate = copy.deepcopy(self.data)
        duplicate["cases"][1]["id"] = duplicate["cases"][0]["id"]
        malformed.append(duplicate)
        for data in malformed:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.load_data(data)

    def test_bad_json_duplicate_keys_and_invalid_utf8_are_rejected(self):
        for raw in (b"{", b'{"schema_version":1,"schema_version":1}', b"\xff"):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.json"
                path.write_bytes(raw)
                with self.assertRaises((ValueError, UnicodeError)):
                    prepare_eval.load_cases(path)


class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commit = prepare_eval.git(REPO, "rev-parse", "HEAD").decode().strip()
        cls.bundle = prepare_eval.prepare_bundle(REPO, cls.commit, CASES)

    def test_commit_hashes_and_exact_inline_content(self):
        provenance = self.bundle["provenance"]
        self.assertEqual(provenance["resolved_commit"], self.commit)
        self.assertEqual(provenance["requested_revision"], self.commit)
        self.assertEqual(provenance["cases_sha256"], hashlib.sha256(CASES.read_bytes()).hexdigest())
        self.assertEqual(provenance["preparer_sha256"], hashlib.sha256((HERE / "prepare_eval.py").read_bytes()).hexdigest())
        self.assertEqual(len(provenance["skill_files"]), 4)
        for source in provenance["skill_files"]:
            raw = prepare_eval.git(REPO, "show", f"{self.commit}:{source['path']}")
            self.assertEqual(source["sha256"], hashlib.sha256(raw).hexdigest())
            for case in self.bundle["cases"]:
                if f"skills/{case['skill']}/" in source["path"]:
                    self.assertIn(f"--- BEGIN {source['path']} ---\n{raw.decode('utf-8')}", case["model_prompt"])

    def test_each_prompt_contains_only_its_own_independent_skill(self):
        seen = set()
        for case in self.bundle["cases"]:
            seen.add(case["skill"])
            other = (set(prepare_eval.SKILLS) - {case["skill"]}).pop()
            self.assertEqual(case["model_prompt"].count("--- BEGIN skills/"), 2)
            self.assertNotIn(f"--- BEGIN skills/{other}/", case["model_prompt"])
            self.assertTrue(case["model_prompt"].endswith(case["task_prompt"]))
            self.assertNotIn("acceptance_criteria", case)
            self.assertNotIn("material_failure_criteria", case)
        self.assertEqual(seen, set(prepare_eval.SKILLS))

    def test_rubrics_never_enter_model_prompts(self):
        data, _ = prepare_eval.load_cases(CASES)
        secret = "REVIEW_ONLY_SENTINEL_49372"
        data["review_instructions"] = [secret + " global"]
        for case in data["cases"]:
            case["acceptance_criteria"] = [secret + " acceptance"]
            case["material_failure_criteria"] = [secret + " failure"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            bundle = prepare_eval.prepare_bundle(REPO, self.commit, path)
        self.assertIn(secret, json.dumps(bundle["rubric"]))
        self.assertNotIn(secret, json.dumps(bundle["cases"]))
        self.assertEqual([c["id"] for c in bundle["cases"]], [c["id"] for c in bundle["rubric"]["cases"]])

    def test_same_inputs_produce_same_bundle_and_alias_resolves(self):
        self.assertEqual(self.bundle, prepare_eval.prepare_bundle(REPO, self.commit, CASES))
        by_head = prepare_eval.prepare_bundle(REPO, "HEAD", CASES)
        self.assertEqual(by_head["provenance"]["resolved_commit"], self.commit)
        self.assertEqual(by_head["cases"], self.bundle["cases"])

    def test_invalid_revision_and_missing_skill_file_fail(self):
        for revision in ("nonexistent-eval-revision-49372", "--help"):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                prepare_eval.prepare_bundle(REPO, revision, CASES)
        original = prepare_eval.git

        def missing(repo, *args):
            if args[0] == "show":
                raise ValueError("Skill file is missing at the requested revision")
            return original(repo, *args)

        with patch.object(prepare_eval, "git", side_effect=missing), self.assertRaisesRegex(ValueError, "missing"):
            prepare_eval.prepare_bundle(REPO, self.commit, CASES)

    def test_git_errors_are_clear_and_do_not_fall_back_to_worktree(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            prepare_eval.prepare_bundle(directory, self.commit, CASES)

    def test_safe_output_and_refusal_to_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "new-directory" / "bundle.json"
            prepare_eval.write_bundle(self.bundle, REPO, output, CASES)
            self.assertEqual(json.loads(output.read_text()), self.bundle)
            before = output.read_bytes()
            with self.assertRaises(FileExistsError):
                prepare_eval.write_bundle(self.bundle, REPO, output, CASES)
            self.assertEqual(output.read_bytes(), before)
        for output in (CASES, HERE / "prepare_eval.py", REPO / "README.md", HERE / "untracked-output.json"):
            with self.subTest(output=output), self.assertRaises(ValueError):
                prepare_eval.write_bundle(self.bundle, REPO, output, CASES)

    def test_only_ignored_results_directory_is_permitted_inside_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for suite in ("close-bars", "missing-data"):
                with self.subTest(suite=suite):
                    relative = f"evaluation/{suite}/results/bundle.json"
                    output = root / relative
                    with patch.object(prepare_eval, "git", side_effect=[str(root).encode(), b""]) as mock_git:
                        prepare_eval.write_bundle(self.bundle, root, output, CASES)
                    self.assertTrue(output.is_file())
                    self.assertEqual(mock_git.call_args.args[1:], ("check-ignore", "--quiet", "--", relative))
                    rejected = output.with_name("not-ignored.json")
                    with patch.object(prepare_eval, "git", side_effect=[str(root).encode(), ValueError("not ignored")]):
                        with self.assertRaises(ValueError):
                            prepare_eval.write_bundle(self.bundle, root, rejected, CASES)
                    self.assertFalse(rejected.exists())

    def test_unapproved_results_and_source_paths_remain_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for relative in (
                "evaluation/other-suite/results/bundle.json",
                "evaluation/missing-data/results-copy/bundle.json",
                "evaluation/missing-data/cases.json",
                "evaluation/missing-data/results/../source.json",
            ):
                with self.subTest(relative=relative):
                    output = root / relative
                    with patch.object(prepare_eval, "git", return_value=str(root).encode()) as mock_git:
                        with self.assertRaisesRegex(ValueError, "results directory"):
                            prepare_eval.write_bundle(self.bundle, root, output, CASES)
                    self.assertEqual(mock_git.call_count, 1)
                    self.assertFalse(output.exists())

    def test_results_symlink_cannot_write_into_repository_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "skills"
            source.mkdir()
            results = root / "evaluation" / "missing-data" / "results"
            results.parent.mkdir(parents=True)
            results.symlink_to(source, target_is_directory=True)
            with patch.object(prepare_eval, "git", return_value=str(root).encode()):
                with self.assertRaises(ValueError):
                    prepare_eval.write_bundle(self.bundle, root, results / "bundle.json", CASES)
            self.assertFalse((source / "bundle.json").exists())

    def test_cli_outputs_bundle_and_reports_errors_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle.json"
            command = [sys.executable, str(HERE / "prepare_eval.py"), "--repo", str(REPO),
                       "--revision", self.commit, "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), self.bundle)
            retry = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(retry.returncode, 2)
            self.assertIn("error:", retry.stderr)
            self.assertNotIn("Traceback", retry.stderr)


class ReplacementProvenanceTests(unittest.TestCase):
    """Use real, isolated Git objects; replacement maps never touch the source repo."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name) / "repo"
        self.repo.mkdir()
        # Make the test's replacement overlay observable regardless of caller config.
        self.environment = patch.dict(os.environ)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        for key in ("GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE", "GIT_DIR",
                    "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
            os.environ.pop(key, None)
        self.run_git("init", "--quiet")
        self.sources = {}
        for skill, reference in prepare_eval.SKILLS.items():
            for relative in (f"skills/{skill}/SKILL.md", f"skills/{skill}/references/{reference}"):
                raw = f"Original committed source: {relative}\n".encode()
                self.sources[relative] = raw
                path = self.repo / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
        self.original = self.commit("Original source")
        self.expected = prepare_eval.prepare_bundle(self.repo, self.original, CASES)
        for relative in self.sources:
            (self.repo / relative).write_text(f"REPLACEMENT source: {relative}\n", encoding="utf-8")
        self.replacement = self.commit("Replacement source")

    def run_git(self, *args):
        return subprocess.run(
            ["git", "-c", "user.name=Evaluation test", "-c", "user.email=test@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.useReplaceRefs=true",
             "-C", str(self.repo), *args],
            capture_output=True, check=True,
        ).stdout.decode().strip()

    def commit(self, message):
        self.run_git("add", "--all")
        self.run_git("commit", "--quiet", "-m", message)
        return self.run_git("rev-parse", "HEAD")

    def assert_original_bundle(self, revision=None):
        revision = revision or self.original
        actual = prepare_eval.prepare_bundle(self.repo, revision, CASES)
        expected = copy.deepcopy(self.expected)
        expected["provenance"]["requested_revision"] = revision
        self.assertEqual(actual, expected)
        for source in actual["provenance"]["skill_files"]:
            self.assertEqual(source["sha256"], hashlib.sha256(self.sources[source["path"]]).hexdigest())

    def test_commit_replacement_cannot_change_pinned_prompts_or_hashes(self):
        self.run_git("replace", self.original, self.replacement)
        relative = next(iter(self.sources))
        self.assertIn("REPLACEMENT", self.run_git("show", f"{self.original}:{relative}"))
        self.assert_original_bundle()
        self.assertEqual(self.run_git("replace", "--list"), self.original)
        # A caller can still request the actual replacement commit explicitly.
        actual = prepare_eval.prepare_bundle(self.repo, self.replacement, CASES)
        self.assertEqual(actual["provenance"]["resolved_commit"], self.replacement)
        self.assertIn("REPLACEMENT", actual["cases"][0]["model_prompt"])

    def test_tree_replacement_cannot_change_pinned_prompts_or_hashes(self):
        tree = self.run_git("rev-parse", f"{self.original}^{{tree}}")
        other_tree = self.run_git("rev-parse", f"{self.replacement}^{{tree}}")
        self.run_git("replace", tree, other_tree)
        self.assertIn("REPLACEMENT", self.run_git("show", f"{self.original}:{next(iter(self.sources))}"))
        self.assert_original_bundle()

    def test_blob_replacements_cannot_change_either_skills_sources(self):
        for relative in self.sources:
            original = self.run_git("rev-parse", f"{self.original}:{relative}")
            replacement = self.run_git("rev-parse", f"{self.replacement}:{relative}")
            self.run_git("replace", original, replacement)
        self.assertIn("REPLACEMENT", self.run_git("show", f"{self.original}:{next(iter(self.sources))}"))
        self.assert_original_bundle()

    def test_replaced_parent_history_cannot_change_revision_resolution(self):
        # Replace the second commit with the root commit. Normal HEAD^ then fails,
        # while raw history must still resolve to the original source commit.
        self.run_git("replace", self.replacement, self.original)
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_git("rev-parse", "--verify", "HEAD^")
        self.assert_original_bundle("HEAD^")

    def test_custom_replacement_namespace_is_ignored_without_mutating_it(self):
        os.environ["GIT_REPLACE_REF_BASE"] = "refs/evaluation-replacements/"
        self.run_git("replace", self.original, self.replacement)
        self.assertIn("REPLACEMENT", self.run_git("show", f"{self.original}:{next(iter(self.sources))}"))
        self.assert_original_bundle()
        self.assertEqual(self.run_git("rev-parse", f"refs/evaluation-replacements/{self.original}"), self.replacement)

    def test_overlay_cannot_supply_a_file_absent_from_requested_commit(self):
        relative = next(iter(self.sources))
        (self.repo / relative).unlink()
        missing = self.commit("Missing source")
        self.run_git("replace", missing, self.original)
        self.assertIn("Original", self.run_git("show", f"{missing}:{relative}"))
        with self.assertRaises(ValueError):
            prepare_eval.prepare_bundle(self.repo, missing, CASES)

    def test_cli_ignores_replacements_and_preserves_overlay(self):
        self.run_git("replace", self.original, self.replacement)
        output = Path(self.directory.name) / "bundle.json"
        result = subprocess.run(
            [sys.executable, str(HERE / "prepare_eval.py"), "--repo", str(self.repo),
             "--revision", self.original, "--output", str(output)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(output.read_text()), self.expected)
        self.assertEqual(self.run_git("replace", "--list"), self.original)


if __name__ == "__main__":
    unittest.main()
