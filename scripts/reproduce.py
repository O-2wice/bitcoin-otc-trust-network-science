"""Run the eight numerical analyses and record their provenance.

Run from the repository root: python scripts/reproduce.py
The source dataset and the environment in requirements.txt must be ready first.
Cytoscape exports, the network layout, report, and slides are separate builds.
"""

from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "reproduction"
SOURCE = ROOT / "data" / "soc-sign-bitcoinotc.csv.gz"
EXPECTED_SHA = "6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373"
PACKAGES = ("pandas", "numpy", "networkx", "matplotlib", "scipy", "notebook", "ipykernel")
TEXT_SUFFIXES = {".py", ".txt", ".csv", ".json"}
STEPS = (
    ("structural_analysis.py", "structure", (
        "network_metrics.csv", "directed_centrality.csv", "communities.csv",
        "metadata.json", "degree_distributions.png")),
    ("temporal_analysis.py", "temporal", (
        "annual_snapshots.csv", "annual_snapshots_rating_ge5.csv",
        "target_choice_by_prior_degree.csv", "target_choice_by_year.csv",
        "metadata.json", "growth_and_concentration.png", "target_choice_ratio.png")),
    ("node_removal.py", "robustness", (
        "node_removal_summary.csv", "node_removal_replicates.csv", "node_removal.png")),
    ("follow_up_checks.py", "follow_up", (
        "matched_target_choice.csv", "degree_preserving_null.csv",
        "structural_evolution.csv", "metadata.json", "matched_target_choice.png",
        "degree_preserving_null.png", "structural_evolution.png")),
    ("temporal_sensitivity.py", "sensitivity", (
        "annual_only_concentration.csv", "fixed_2011_cohort_concentration.csv",
        "annual_equal_volume_check.csv", "temporal_metadata.json",
        "annual_vs_cumulative_concentration.png", "fixed_cohort_concentration.png")),
    ("community_profiles.py", "sensitivity", (
        "community_profiles.csv", "community_stability.csv", "community_metadata.json",
        "community_link_profiles.png")),
    ("theory_comparison.py", "theory", (
        "reference_metrics.csv", "model_expectations.csv", "degree_tail_fits.csv",
        "attachment_benchmarks.csv", "reciprocation_by_prior_degree.csv",
        "percolation_curves.csv", "percolation_thresholds.csv", "centrality_comparison.csv",
        "metadata.json", "degree_ccdf_fits.png", "attachment_kernel.png",
        "percolation_vs_theory.png")),
    ("degree_correlations.py", "correlations", (
        "correlation_summary.csv", "directed_assortativity.csv", "rewired_assortativity.csv",
        "knn_by_degree.csv", "metadata.json", "degree_correlations.png")),
)


def sha256(path):
    """Hash a file. Text line endings are normalized so Windows and Linux agree."""
    data = path.read_bytes()
    if path.suffix in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def main():
    if sha256(SOURCE) != EXPECTED_SHA:
        raise ValueError("Unexpected source dataset checksum")
    requirements = ROOT / "requirements.txt"
    versions = {name: metadata.version(name) for name in PACKAGES}
    for line in requirements.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, pinned = line.split("==")
            if metadata.version(name) != pinned:
                raise ValueError(f"Install requirements.txt first: {name} does not match {pinned}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "logs").mkdir(exist_ok=True)
    manifest_path = OUT / "run_manifest.json"
    manifest = {
        "scope": "Eight numerical analysis scripts; separate visual, document, and presentation builds are excluded",
        "started_utc": utc_now(), "complete": False,
        "python_version": sys.version.split()[0],
        "python_executable": Path(sys.executable).name,
        "platform": platform.platform(),
        "package_versions": versions,
        "requirements_sha256": sha256(requirements),
        "source": "data/soc-sign-bitcoinotc.csv.gz",
        "source_sha256": sha256(SOURCE),
        "steps": [],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    environment = dict(os.environ)
    environment.setdefault("MPLBACKEND", "Agg")
    for script_name, directory, filenames in STEPS:
        script = ROOT / "scripts" / script_name
        log_path = OUT / "logs" / (script.stem + ".log")
        entry = {
            "script": script.relative_to(ROOT).as_posix(),
            "script_sha256": sha256(script),
            "started_utc": utc_now(),
            "log": log_path.relative_to(ROOT).as_posix(),
        }
        print(f"Running {script_name} ...", flush=True)
        start = time.perf_counter()
        with log_path.open("w") as log:
            result = subprocess.run(
                [sys.executable, str(script)], cwd=ROOT, env=environment,
                stdout=log, stderr=subprocess.STDOUT, check=False,
            )
        entry.update({"finished_utc": utc_now(),
                      "elapsed_seconds": round(time.perf_counter() - start, 3),
                      "exit_code": result.returncode})
        if result.returncode == 0:
            entry["output_sha256"] = {
                f"outputs/{directory}/{name}": sha256(ROOT / "outputs" / directory / name)
                for name in filenames
            }
        manifest["steps"].append(entry)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        if result.returncode:
            raise SystemExit(f"{script_name} failed; see {log_path}")
        print(f"Finished {script_name} in {entry['elapsed_seconds']:.1f}s", flush=True)

    manifest.update({"complete": True, "finished_utc": utc_now()})
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print("Completed eight analyses. Next: python scripts/verify_reproduction.py --check-manifest")


if __name__ == "__main__":
    main()
