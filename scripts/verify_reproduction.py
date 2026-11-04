"""Validate the source identity and headline values in stored analysis outputs.

This command does not rerun the analysis scripts or establish when the CSVs were
created. Run the analysis commands in REPRODUCIBILITY.md before using it to
check a new reproduction.
"""

import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "soc-sign-bitcoinotc.csv.gz"
EXPECTED_SHA256 = "6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373"


def close(actual, expected, tolerance=0.0005):
    assert abs(actual - expected) < tolerance, f"expected {expected}, got {actual}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-manifest", action="store_true",
                        help="also check the completed run manifest against current scripts, environment, and outputs")
    args = parser.parse_args()
    assert SOURCE.exists(), f"missing source file: {SOURCE}"
    actual_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert actual_hash == EXPECTED_SHA256, f"source SHA-256 differs: {actual_hash}"

    structure = pd.read_csv(ROOT / "outputs/structure/network_metrics.csv")
    observed = structure.set_index("network").loc["observed"]
    assert int(observed.nodes) == 5881
    assert int(observed.edges) == 18591
    close(observed.transitivity, 0.0570)
    assert int(observed.max_degree) == 788
    assert len(structure) == 21  # observed plus 10 ER and 10 BA realizations

    annual = pd.read_csv(ROOT / "outputs/temporal/annual_snapshots.csv").set_index("year_end")
    assert int(annual.loc[2011, "cumulative_positive_ratings"]) == 7745
    assert int(annual.loc[2015, "cumulative_positive_ratings"]) == 31989
    close(annual.loc[2011, "top_1_percent_incoming_share"], 0.1551)
    close(annual.loc[2015, "top_1_percent_incoming_share"], 0.2352)

    removal = pd.read_csv(ROOT / "outputs/robustness/node_removal_summary.csv")
    at_five = removal[removal.removed_nodes == 294].set_index("strategy")
    close(at_five.loc["highest_degree_first", "mean"], 0.4557)
    close(at_five.loc["uniform_random", "mean"], 0.8759)
    detail = pd.read_csv(ROOT / "outputs/robustness/node_removal_replicates.csv")
    assert len(detail[detail.removed_nodes == 294]) == 31

    matched = pd.read_csv(ROOT / "outputs/flagship/matched_target_choice.csv")
    high = matched.set_index("prior_positive_in_degree").loc["32+"]
    close(high.observed_over_expected, 1.6485)
    assert int(matched.observed_target_events.sum()) == 26993
    rewired = pd.read_csv(ROOT / "outputs/flagship/degree_preserving_null.csv")
    assert len(rewired) == 9  # observed plus eight degree-preserving rewires
    assert (rewired.edges == 18591).all()
    assert rewired.iloc[0].transitivity > rewired.iloc[1:].transitivity.max()
    evolution = pd.read_csv(ROOT / "outputs/flagship/structural_evolution.csv").set_index("year_end")
    close(evolution.loc[2011, "directed_reciprocity"], 0.8795)
    close(evolution.loc[2015, "directed_reciprocity"], 0.8389)

    annual_only = pd.read_csv(ROOT / "outputs/sensitivity/annual_only_concentration.csv").set_index("year")
    close(annual_only.loc[2013, "top_1_percent_incoming_share"], 0.2096)
    close(annual_only.loc[2015, "top_1_percent_incoming_share"], 0.1130)
    assert int(annual_only.loc[2015, "incoming_ratings_in_denominator"]) == 929
    cohort = pd.read_csv(ROOT / "outputs/sensitivity/fixed_2011_cohort_concentration.csv").set_index("year_end")
    assert (cohort.users_in_denominator == 1631).all()
    close(cohort.loc[2015, "top_1_percent_incoming_share"], 0.2218)
    profiles = pd.read_csv(ROOT / "outputs/sensitivity/community_profiles.csv").set_index("group_rank_by_size")
    assert int(profiles.loc[1, "users"]) == 1096
    close(profiles.loc[1, "within_group_endpoint_fraction"], 0.6840)
    community_meta = json.loads((ROOT / "outputs/sensitivity/community_metadata.json").read_text())
    assert community_meta["isolated_accounts_after_positive_filter"] == 308

    print("PASS: source checksum and headline values in the stored CSV outputs")
    if args.check_manifest:
        manifest_path = ROOT / "outputs/reproduction/run_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        assert manifest["complete"], "The recorded analysis run did not complete"
        assert len(manifest["steps"]) == 6
        assert manifest["source_sha256"] == actual_hash
        assert manifest["requirements_sha256"] == hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()
        assert manifest["python_version"] == sys.version.split()[0], "Python version differs from the recorded run"
        for name, version in manifest["package_versions"].items():
            assert metadata.version(name) == version, f"{name} version differs from the recorded run"
        for step in manifest["steps"]:
            assert step["exit_code"] == 0, f"Recorded run failed: {step['script']}"
            script_hash = hashlib.sha256((ROOT / step["script"]).read_bytes()).hexdigest()
            assert script_hash == step["script_sha256"], f"Script changed since recorded run: {step['script']}"
            for relative_path, expected_hash in step["output_sha256"].items():
                output_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
                assert output_hash == expected_hash, f"Output changed since recorded run: {relative_path}"
        print("PASS: recorded six-script run matches current source, scripts, environment, and listed outputs")
        print("The manifest records one execution; it does not establish scientific correctness or independent replication.")
    else:
        print("This checker reads existing outputs; it does not rerun the analyses or verify output freshness.")


if __name__ == "__main__":
    main()
