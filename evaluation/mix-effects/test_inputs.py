"""Check authored mix-effects inputs and integration, never model answers."""

import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CASES = HERE / "cases.json"
PREPARER = HERE.parent / "close-bars" / "prepare_eval.py"
SPEC = importlib.util.spec_from_file_location("mix_prepare_eval", PREPARER)
prepare_eval = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare_eval)


class MixEffectsInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.digest = prepare_eval.load_cases(CASES)
        cls.commit = prepare_eval.git(REPO, "rev-parse", "HEAD").decode().strip()
        cls.bundle = prepare_eval.prepare_bundle(REPO, cls.commit, CASES)

    def test_manifest_ids_balance_and_hash(self):
        self.assertEqual([c["id"] for c in self.data["cases"]], [f"P{i}" for i in range(1, 11)])
        for skill in prepare_eval.SKILLS:
            self.assertEqual(sum(c["skill"] == skill for c in self.data["cases"]), 5)
        self.assertEqual(self.digest, hashlib.sha256(CASES.read_bytes()).hexdigest())

    def test_reversal_fixture_has_the_claimed_rates_and_mix(self):
        # Read the fractions from the task itself, not a second numeric fixture.
        prompt = self.data["cases"][0]["task_prompt"]
        pairs = [tuple(map(int, pair)) for pair in re.findall(r"(\d+)/(\d+)", prompt)]
        self.assertEqual(pairs, [(90, 100), (30, 100), (19, 20), (72, 180)])
        jan_routine, jan_complex, feb_routine, feb_complex = map(lambda p: Fraction(*p), pairs)
        self.assertGreater(feb_routine, jan_routine)
        self.assertGreater(feb_complex, jan_complex)
        jan = Fraction(pairs[0][0] + pairs[1][0], pairs[0][1] + pairs[1][1])
        feb = Fraction(pairs[2][0] + pairs[3][0], pairs[2][1] + pairs[3][1])
        self.assertEqual((jan, feb, feb - jan), (Fraction(3, 5), Fraction(91, 200), Fraction(-29, 200)))
        self.assertEqual(Fraction(pairs[1][1], pairs[0][1] + pairs[1][1]), Fraction(1, 2))
        self.assertEqual(Fraction(pairs[3][1], pairs[2][1] + pairs[3][1]), Fraction(9, 10))

    def test_discriminating_facts_and_countercontrols_are_retained(self):
        by_id = {c["id"]: c for c in self.data["cases"]}
        fragments = {
            "P1": ["mutually exclusive and exhaustive", "90/100", "30/100", "19/20", "72/180"],
            "P2": ["Completion rates fell for both request types", "adjacent table"],
            "P3": ["asks only", "120/200 = 60%", "91/200 = 45.5%"],
            "P4": ["all 200 requests", "(95% + 40%) / 2 = 67.5%"],
            "P5": ["40% routine", "60% complex", "hypothetical", "unavailable"],
            "P6": ["explicitly asks for an equal-weight average", "does not call this the share"],
            "P7": ["Counts, denominators, and their population shares are unavailable"],
            "P8": ["exactly 10 attendees", "exactly 8", "unique-attendee"],
            "P9": ["number of overlapping attendees and their completion outcomes are not supplied"],
            "P10": ["18 of 20", "6 of 20", "24 of 40"],
        }
        for case_id, required in fragments.items():
            for fragment in required:
                with self.subTest(case=case_id, fragment=fragment):
                    self.assertIn(fragment, by_id[case_id]["task_prompt"])
        for case_id in ("P3", "P6"):
            self.assertIn("no established material defect", " ".join(by_id[case_id]["acceptance_criteria"]))

    def test_exact_pinned_sources_and_manifest_provenance(self):
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
            self.assertEqual(case["model_prompt"].count("--- BEGIN skills/"), 2)
            self.assertTrue(case["model_prompt"].endswith(case["task_prompt"]))

    def test_review_only_content_stays_out_of_model_prompts(self):
        data = copy.deepcopy(self.data)
        secret = "MIX_EFFECTS_REVIEW_ONLY_57819"
        data["review_instructions"] = [secret]
        for case in data["cases"]:
            case["acceptance_criteria"] = [secret]
            case["material_failure_criteria"] = [secret]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            bundle = prepare_eval.prepare_bundle(REPO, self.commit, path)
        self.assertIn(secret, json.dumps(bundle["rubric"]))
        self.assertNotIn(secret, json.dumps(bundle["cases"]))
        self.assertNotEqual(bundle["provenance"]["cases_sha256"], self.digest)
        self.assertEqual(bundle["provenance"]["skill_files"], self.bundle["provenance"]["skill_files"])

    def test_cli_uses_selected_suite_and_preserves_existing_output(self):
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
        with self.assertRaises(ValueError):
            prepare_eval.write_bundle(self.bundle, REPO, CASES, CASES)

    def test_results_output_is_allowed_but_curated_sources_are_protected(self):
        # Exercise the real repository policy, using an automatically removed child.
        results = HERE / "results"
        results.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=results) as directory:
            output = Path(directory) / "bundle.json"
            prepare_eval.write_bundle(self.bundle, REPO, output, CASES)
            self.assertEqual(json.loads(output.read_text()), self.bundle)
        for relative, expected in (
            ("evaluation/mix-effects/cases.json", 1),
            ("evaluation/mix-effects/test_inputs.py", 1),
            ("evaluation/mix-effects/results/bundle.json", 0),
            ("evaluation/mix-effects/results/nested/response.txt", 0),
        ):
            with self.subTest(path=relative):
                result = subprocess.run(["git", "-C", str(REPO), "check-ignore", "--no-index", "--quiet", "--", relative],
                                        capture_output=True, timeout=30)
                self.assertEqual(result.returncode, expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
