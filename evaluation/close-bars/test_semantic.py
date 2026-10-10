"""Check the semantic-evaluation inputs and harness, not model answer quality.

Run with: python3 -m unittest discover -s evaluation/close-bars -p 'test_*.py' -v
No model calls, source-repository mutations, or automatic semantic scoring occur.
"""

import copy
import hashlib
import importlib.util
import json
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
            output = root / "evaluation" / "close-bars" / "results" / "bundle.json"
            with patch.object(prepare_eval, "git", side_effect=[str(root).encode(), b""]) as mock_git:
                prepare_eval.write_bundle(self.bundle, root, output, CASES)
            self.assertTrue(output.is_file())
            self.assertEqual(mock_git.call_args.args[1:], ("check-ignore", "--quiet", "--", "evaluation/close-bars/results/bundle.json"))
            rejected = output.with_name("not-ignored.json")
            with patch.object(prepare_eval, "git", side_effect=[str(root).encode(), ValueError("not ignored")]):
                with self.assertRaises(ValueError):
                    prepare_eval.write_bundle(self.bundle, root, rejected, CASES)
            self.assertFalse(rejected.exists())

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


if __name__ == "__main__":
    unittest.main()
