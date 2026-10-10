"""Validate missing-data eval sources and shared harness integration, not answers.

These tests never call or keyword-grade a model. Source-fragment assertions keep
the authored cases' discriminating facts from disappearing during maintenance.
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


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CASES = HERE / "cases.json"
PREPARER = HERE.parent / "close-bars" / "prepare_eval.py"
SPEC = importlib.util.spec_from_file_location("shared_prepare_eval", PREPARER)
prepare_eval = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare_eval)


class MissingDataInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.digest = prepare_eval.load_cases(CASES)
        cls.commit = prepare_eval.git(REPO, "rev-parse", "HEAD").decode().strip()
        cls.bundle = prepare_eval.prepare_bundle(REPO, cls.commit, CASES)

    def test_manifest_ids_balance_and_content_hash(self):
        cases = self.data["cases"]
        self.assertEqual([case["id"] for case in cases], [f"P{i}" for i in range(1, 11)])
        for skill in prepare_eval.SKILLS:
            self.assertEqual(sum(case["skill"] == skill for case in cases), 5)
        self.assertEqual(self.digest, hashlib.sha256(CASES.read_bytes()).hexdigest())

    def test_discriminating_source_facts_and_controls_are_retained(self):
        by_id = {case["id"]: case for case in self.data["cases"]}
        required = {
            "P1": ["Wednesday 0 observed", "Tuesday missing", "Thursday missing", "no point markers"],
            "P2": ["one reading on each of June 1–4", "no June 3 row", "Complete four-day record"],
            "P3": ["B: not reported", "C: 0 observed", "no associated values or status table"],
            "P4": ["Visits occur when requested", "no daily or weekly sampling schedule", "No lines"],
            "P5": ["12 estimated by the publisher", "linear interpolation", "0 observed"],
            "P6": ["no September 2 observation or estimate", "explicit September 2", "no continuous-trend claim"],
            "P7": ["nothing about intended cadence, coverage window", "shows the missing days"],
            "P8": ["adjacent always-visible associated table", "B: not reported; C: 0 observed"],
            "P9": ["no reason", "Service stopped during outage", "May not reported"],
            "P10": ["all 30 calendar days", "29 reported daily counts summing to 290", "genuine 0", "September 16 is explicitly missing"],
        }
        for case_id, fragments in required.items():
            with self.subTest(case_id=case_id):
                for fragment in fragments:
                    self.assertIn(fragment, by_id[case_id]["task_prompt"])
        for case_id in ("P4", "P6", "P8"):
            self.assertIn("no established material defect", " ".join(by_id[case_id]["acceptance_criteria"]))

    def test_shared_preparer_keeps_exact_revision_and_sources(self):
        provenance = self.bundle["provenance"]
        self.assertEqual(provenance["resolved_commit"], self.commit)
        self.assertEqual(provenance["cases_sha256"], self.digest)
        self.assertEqual(provenance["preparer_sha256"], hashlib.sha256(PREPARER.read_bytes()).hexdigest())
        self.assertEqual(len(provenance["skill_files"]), 4)
        for source in provenance["skill_files"]:
            raw = prepare_eval.git(REPO, "show", f"{self.commit}:{source['path']}")
            self.assertEqual(source["sha256"], hashlib.sha256(raw).hexdigest())
            for case in self.bundle["cases"]:
                if source["path"].startswith(f"skills/{case['skill']}/"):
                    self.assertIn(f"--- BEGIN {source['path']} ---\n{raw.decode('utf-8')}", case["model_prompt"])
        for case in self.bundle["cases"]:
            other = (set(prepare_eval.SKILLS) - {case["skill"]}).pop()
            self.assertNotIn(f"--- BEGIN skills/{other}/", case["model_prompt"])
            self.assertEqual(case["model_prompt"].count("--- BEGIN skills/"), 2)
            self.assertTrue(case["model_prompt"].endswith(case["task_prompt"]))

    def test_rubric_and_review_instructions_stay_out_of_model_input(self):
        data = copy.deepcopy(self.data)
        sentinel = "MISSING_DATA_REVIEW_ONLY_92154"
        data["review_instructions"] = [sentinel + " review"]
        for case in data["cases"]:
            case["acceptance_criteria"] = [sentinel + " accept"]
            case["material_failure_criteria"] = [sentinel + " fail"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            bundle = prepare_eval.prepare_bundle(REPO, self.commit, path)
        self.assertIn(sentinel, json.dumps(bundle["rubric"]))
        self.assertNotIn(sentinel, json.dumps(bundle["cases"]))
        self.assertEqual([case["id"] for case in bundle["cases"]],
                         [case["id"] for case in bundle["rubric"]["cases"]])

    def test_local_manifest_changes_have_separate_provenance(self):
        data = copy.deepcopy(self.data)
        data["cases"][0]["task_prompt"] += " Local manifest provenance probe."
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            changed = prepare_eval.prepare_bundle(REPO, self.commit, path)
        before = self.bundle["provenance"]
        after = changed["provenance"]
        self.assertNotEqual(before["cases_sha256"], after["cases_sha256"])
        for key in ("resolved_commit", "preparer_sha256", "skill_files"):
            self.assertEqual(before[key], after[key])
        self.assertIn("Local manifest provenance probe.", changed["cases"][0]["model_prompt"])

    def test_cli_selects_this_manifest_without_replacing_sources(self):
        before = CASES.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle.json"
            command = [sys.executable, str(PREPARER), "--repo", str(REPO),
                       "--revision", self.commit, "--cases", str(CASES), "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), self.bundle)
            retry = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(retry.returncode, 2)
            self.assertNotIn("Traceback", retry.stderr)
        self.assertEqual(CASES.read_bytes(), before)
        with self.assertRaises(ValueError):
            prepare_eval.write_bundle(self.bundle, REPO, CASES, CASES)

    def test_git_allows_curated_sources_and_ignores_generated_results(self):
        for relative, expected_returncode in (
            ("evaluation/missing-data/cases.json", 1),
            ("evaluation/missing-data/test_inputs.py", 1),
            ("evaluation/missing-data/results/bundle.json", 0),
            ("evaluation/missing-data/results/nested/response.txt", 0),
        ):
            with self.subTest(path=relative):
                result = subprocess.run(["git", "-C", str(REPO), "check-ignore", "--no-index", "--quiet", "--", relative],
                                        capture_output=True, check=False)
                self.assertEqual(result.returncode, expected_returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
