"""Check source identity and headline results after regenerating all CSV outputs."""

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "soc-sign-bitcoinotc.csv.gz"
EXPECTED_SHA256 = "6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373"


def close(actual, expected, tolerance=0.0005):
    assert abs(actual - expected) < tolerance, f"expected {expected}, got {actual}"


def main():
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

    print("PASS: source checksum, graph size, models, temporal trend, node removal, and flagship checks")


if __name__ == "__main__":
    main()
