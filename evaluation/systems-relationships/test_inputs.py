"""Validate authored systems inputs and routing, never grade model answers."""

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
PREPARER = HERE.parent / "close-bars" / "prepare_eval.py"
SPEC = importlib.util.spec_from_file_location("systems_prepare_eval", PREPARER)
prepare_eval = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare_eval)


class SystemsInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.digest = prepare_eval.load_cases(CASES)
        cls.commit = prepare_eval.git(REPO, "rev-parse", "HEAD").decode().strip()
        cls.bundle = prepare_eval.prepare_bundle(REPO, cls.commit, CASES)

    def with_manifest(self, data, callback):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return callback(path)

    def test_manifest_balance_and_hash(self):
        self.assertEqual(self.data["schema_version"], 2)
        self.assertEqual(self.data["reference_group"], "systems")
        self.assertEqual([c["id"] for c in self.data["cases"]], [f"P{i}" for i in range(1, 11)])
        for skill in prepare_eval.SKILLS:
            self.assertEqual(sum(c["skill"] == skill for c in self.data["cases"]), 5)
        self.assertEqual(self.digest, hashlib.sha256(CASES.read_bytes()).hexdigest())

    def test_discriminating_source_facts_and_controls_are_retained(self):
        # Guard authored test conditions, not words in a model's answer.
        by_id = {case["id"]: case for case in self.data["cases"]}
        fragments = {
            "P1": ["9 reels waiting", "2 reels being scanned", "at most 3", "08:00–09:00", "12 reels"],
            "P2": ["asks only", "no arrival rates", "makes no congestion"],
            "P3": ["deliberately bypassed", "not reached", "result is unknown", "earliest established difference"],
            "P4": ["partial log", "does not say whether", "do not invent a corrected test outcome"],
            "P5": ["next unacknowledged chunk", "Cancelled with no resume", "every chunk is acknowledged"],
            "P6": ["first unfinished tile", "returns to 'Load assets'", "Restart whole job"],
            "P7": ["only if both", "at least one", "withheld when neither", "does not guarantee transmission"],
            "P8": ["exactly when", "waives only the deposit", "bypassing membership", "expired membership"],
            "P9": ["Collector C7", "Receiver R2", "Buffer B5", "not a physical location or ownership claim"],
            "P10": ["paint intentionally unnecessary", "happened next", "Selected examples, not the full routing policy"],
        }
        for case_id, required in fragments.items():
            for fragment in required:
                with self.subTest(case=case_id, fragment=fragment):
                    self.assertIn(fragment, by_id[case_id]["task_prompt"])
        for case_id in ("P2", "P10"):
            self.assertIn("no established material defect", " ".join(by_id[case_id]["acceptance_criteria"]))

    def test_only_exact_pinned_systems_sources_are_inlined(self):
        provenance = self.bundle["provenance"]
        self.assertEqual(provenance["resolved_commit"], self.commit)
        self.assertEqual(provenance["cases_sha256"], self.digest)
        self.assertEqual(provenance["preparer_sha256"], hashlib.sha256(PREPARER.read_bytes()).hexdigest())
        expected_paths = {
            f"skills/{skill}/{suffix}"
            for skill in prepare_eval.SKILLS
            for suffix in ("SKILL.md", "references/systems-and-relationships.md")
        }
        self.assertEqual({s["path"] for s in provenance["skill_files"]}, expected_paths)
        self.assertEqual(len(provenance["skill_files"]), 4)
        for case in self.bundle["cases"]:
            self.assertEqual(case["model_prompt"].count("--- BEGIN skills/"), 2)
            self.assertIn("skill and systems reference", case["model_prompt"])
            self.assertTrue(case["model_prompt"].endswith(case["task_prompt"]))
            other = (set(prepare_eval.SKILLS) - {case["skill"]}).pop()
            self.assertNotIn(f"--- BEGIN skills/{other}/", case["model_prompt"])
            for source in provenance["skill_files"]:
                raw = prepare_eval.git(REPO, "show", f"{self.commit}:{source['path']}")
                self.assertEqual(source["sha256"], hashlib.sha256(raw).hexdigest())
                if source["path"].startswith(f"skills/{case['skill']}/"):
                    self.assertIn(f"--- BEGIN {source['path']} ---\n{raw.decode('utf-8')}", case["model_prompt"])

    def test_schema_groups_are_bounded_and_explicit(self):
        malformed = []
        for value in (None, [], {}, 1, "", "unknown", "../systems", "systems-and-relationships.md"):
            malformed.append({**self.data, "reference_group": value})
        missing = copy.deepcopy(self.data)
        del missing["reference_group"]
        malformed.extend([missing, {**self.data, "schema_version": 1},
                          {**self.data, "schema_version": 3}, {**self.data, "schema_version": True},
                          {**self.data, "unexpected": "field"}])
        for data in malformed:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.with_manifest(data, prepare_eval.load_cases)

    def test_legacy_and_explicit_quantitative_manifests_have_identical_prompts(self):
        for suite in ("close-bars", "missing-data", "mix-effects"):
            with self.subTest(suite=suite):
                path = HERE.parent / suite / "cases.json"
                legacy, _ = prepare_eval.load_cases(path)
                original = prepare_eval.prepare_bundle(REPO, self.commit, path)
                explicit = {**legacy, "schema_version": 2, "reference_group": "quantitative"}
                new = self.with_manifest(explicit, lambda p: prepare_eval.prepare_bundle(REPO, self.commit, p))
                self.assertEqual(original["cases"], new["cases"])
                self.assertEqual(original["rubric"], new["rubric"])
                self.assertEqual(original["provenance"]["skill_files"], new["provenance"]["skill_files"])
                self.assertNotEqual(original["provenance"]["cases_sha256"], new["provenance"]["cases_sha256"])
                for case in original["cases"]:
                    self.assertTrue(case["model_prompt"].startswith(
                        f"Use the supplied {case['skill']} skill and quantitative reference.\n"
                        "Only these two skill files are supplied; do not load other files or links.\n\n"
                    ))
                for source in original["provenance"]["skill_files"]:
                    self.assertNotIn("systems-and-relationships", source["path"])

    def test_missing_pinned_systems_reference_fails_without_fallback(self):
        original = prepare_eval.git
        calls = []
        def missing(repo, *args):
            calls.append(args)
            if args[0] == "show" and "systems-and-relationships" in args[1]:
                raise ValueError("Missing pinned systems reference")
            return original(repo, *args)
        with patch.object(prepare_eval, "git", side_effect=missing):
            with self.assertRaisesRegex(ValueError, "Missing pinned systems"):
                prepare_eval.prepare_bundle(REPO, self.commit, CASES)
        self.assertFalse(any("quantitative" in str(args) for args in calls))

    def test_review_only_content_stays_out_of_model_prompts(self):
        data = copy.deepcopy(self.data)
        secret = "SYSTEMS_REVIEW_ONLY_83472"
        data["review_instructions"] = [secret]
        for case in data["cases"]:
            case["acceptance_criteria"] = [secret]
            case["material_failure_criteria"] = [secret]
        bundle = self.with_manifest(data, lambda p: prepare_eval.prepare_bundle(REPO, self.commit, p))
        self.assertIn(secret, json.dumps(bundle["rubric"]))
        self.assertNotIn(secret, json.dumps(bundle["cases"]))
        self.assertNotEqual(bundle["provenance"]["cases_sha256"], self.digest)
        self.assertEqual(bundle["provenance"]["skill_files"], self.bundle["provenance"]["skill_files"])

    def test_cli_selects_systems_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle.json"
            command = [sys.executable, str(PREPARER), "--repo", str(REPO), "--revision", self.commit,
                       "--cases", str(CASES), "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), self.bundle)
            before = output.read_bytes()
            retry = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(retry.returncode, 2)
            self.assertEqual(output.read_bytes(), before)

    def test_results_output_allowed_and_curated_sources_protected(self):
        results = HERE / "results"
        results.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=results) as directory:
            output = Path(directory) / "bundle.json"
            prepare_eval.write_bundle(self.bundle, REPO, output, CASES)
            self.assertEqual(json.loads(output.read_text()), self.bundle)
        for relative, expected in (
            ("evaluation/systems-relationships/cases.json", 1),
            ("evaluation/systems-relationships/test_inputs.py", 1),
            ("evaluation/systems-relationships/results/bundle.json", 0),
            ("evaluation/systems-relationships/results/nested/answer.txt", 0),
        ):
            with self.subTest(path=relative):
                result = subprocess.run(["git", "-C", str(REPO), "check-ignore", "--no-index", "--quiet", "--", relative],
                                        capture_output=True, timeout=30)
                self.assertEqual(result.returncode, expected, result.stderr)
        for output in (CASES, HERE / "test_inputs.py", HERE / "results-copy" / "bundle.json"):
            with self.subTest(output=output), self.assertRaises(ValueError):
                prepare_eval.write_bundle(self.bundle, REPO, output, CASES)


if __name__ == "__main__":
    unittest.main()
