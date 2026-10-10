#!/usr/bin/env python3
"""Prepare pinned, self-contained model prompts; never run or score a model."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


SKILLS = {
    "design-visual-explanation": "quantitative-explanations.md",
    "review-visual-explanation": "quantitative-review.md",
}

# Explicitly opt curated suites in; ignoring an arbitrary directory is not enough.
RESULTS_DIRS = (
    "evaluation/close-bars/results",
    "evaluation/missing-data/results",
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, check=False
    )
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def text_list(value):
    return isinstance(value, list) and bool(value) and all(map(nonempty_text, value))


def load_cases(path):
    raw = Path(path).read_bytes()
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    required = {"schema_version", "instructions", "review_instructions", "cases"}
    if not isinstance(data, dict) or set(data) != required:
        raise ValueError(f"Case file must contain exactly: {sorted(required)}")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unsupported case schema_version; expected 1")
    if not nonempty_text(data["instructions"]) or not text_list(data["review_instructions"]):
        raise ValueError("Instructions must be nonempty text; review_instructions a text list")
    if not isinstance(data["cases"], list) or not data["cases"]:
        raise ValueError("cases must be a nonempty list")
    fields = {"id", "title", "skill", "task_prompt", "acceptance_criteria", "material_failure_criteria"}
    seen = set()
    for case in data["cases"]:
        if not isinstance(case, dict) or set(case) != fields:
            raise ValueError(f"Each case must contain exactly: {sorted(fields)}")
        if not all(nonempty_text(case[key]) for key in ("id", "title", "skill", "task_prompt")):
            raise ValueError("Case id, title, skill, and task_prompt must be nonempty text")
        if not re.fullmatch(r"P[1-9][0-9]*", case["id"]) or case["id"] in seen:
            raise ValueError(f"Invalid or duplicate case ID: {case['id']}")
        seen.add(case["id"])
        if case["skill"] not in SKILLS:
            raise ValueError(f"Unknown skill: {case['skill']}")
        for key in ("acceptance_criteria", "material_failure_criteria"):
            if not text_list(case[key]):
                raise ValueError(f"{case['id']}: {key} must be a nonempty text list")
    return data, sha256(raw)


def prepare_bundle(repo, revision, cases_path):
    data, cases_hash = load_cases(cases_path)
    commit = git(repo, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}").decode().strip()
    sources, contexts = [], {}
    for skill in sorted({case["skill"] for case in data["cases"]}):
        paths = [f"skills/{skill}/SKILL.md", f"skills/{skill}/references/{SKILLS[skill]}"]
        parts = []
        for path in paths:
            raw = git(repo, "show", f"{commit}:{path}")
            sources.append({"path": path, "sha256": sha256(raw)})
            parts.append(f"--- BEGIN {path} ---\n{raw.decode('utf-8')}\n--- END {path} ---")
        contexts[skill] = "\n\n".join(parts)
    cases, rubrics = [], []
    for case in data["cases"]:
        prompt = (
            f"Use the supplied {case['skill']} skill and quantitative reference.\n"
            "Only these two skill files are supplied; do not load other files or links.\n\n"
            f"{contexts[case['skill']]}\n\nTASK\n{data['instructions']}\n\n{case['task_prompt']}"
        )
        cases.append({key: case[key] for key in ("id", "title", "skill", "task_prompt")})
        cases[-1]["model_prompt"] = prompt
        rubrics.append({key: case[key] for key in ("id", "acceptance_criteria", "material_failure_criteria")})
    return {
        "schema_version": 1,
        "kind": "model-evaluation-inputs",
        "provenance": {
            "requested_revision": revision,
            "resolved_commit": commit,
            "cases_sha256": cases_hash,
            "preparer_sha256": sha256(Path(__file__).read_bytes()),
            "skill_files": sources,
        },
        "cases": cases,
        "rubric": {"instructions": data["review_instructions"], "cases": rubrics},
        "limits": [
            "This bundle prepares inputs only; no model has been run or scored.",
            "Only skill text is read from the git revision; cases and preparer are local and separately hashed.",
            "Replaying identical prompts does not ensure identical model outputs.",
            "Inline loading does not test reference selection, rendered charts, or reader comprehension.",
        ],
    }


def write_bundle(bundle, repo, output, cases_path):
    root = Path(git(repo, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    output = Path(output).resolve()
    if output in (Path(cases_path).resolve(), Path(__file__).resolve()):
        raise ValueError("Output must not replace evaluation inputs or tooling")
    if output.is_relative_to(root):
        if not any(output.is_relative_to(root / path) for path in RESULTS_DIRS):
            raise ValueError(
                "Write outside the repository or inside an ignored results directory: "
                + ", ".join(RESULTS_DIRS)
            )
        try:
            git(root, "check-ignore", "--quiet", "--", str(output.relative_to(root)))
        except ValueError as error:
            raise ValueError("The results output path must be ignored by Git") from error
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(bundle, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def main(argv=None):
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=here.parents[1], help="Git checkout (default: this repository)")
    parser.add_argument("--revision", required=True, help="Git revision to read the two skill files from")
    parser.add_argument("--cases", type=Path, default=here / "cases.json", help="Local case manifest")
    parser.add_argument("--output", type=Path, required=True, help="New JSON file outside source or in ignored results/")
    args = parser.parse_args(argv)
    try:
        bundle = prepare_bundle(args.repo, args.revision, args.cases)
        write_bundle(bundle, args.repo, args.output, args.cases)
    except (OSError, ValueError, UnicodeError) as error:
        parser.exit(2, f"error: {error}\n")
    print(f"Prepared {len(bundle['cases'])} cases at {bundle['provenance']['resolved_commit']} -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
