"""Three follow-up checks: matched target choice, degree-preserving null, evolution.

Run after downloading the SNAP file: python scripts/follow_up_checks.py
All choices are measured immediately before each event; no future degree is used.
"""

from collections import Counter, deque
from pathlib import Path
import hashlib
import json

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "outputs/follow_up"
SHA = "6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373"
WINDOW = 90 * 24 * 60 * 60
SEEDS = tuple(range(2026, 2034))
DEGREE_LABELS = ("0", "1", "2-3", "4-7", "8-15", "16-31", "32+")


def degree_bin(degree):
    return min(6, int(np.log2(degree)) + 1) if degree else 0


def matched_target_choice(positive):
    """Uniform choice within the chosen target's prior tenure/activity stratum.

    Tenure is days since the user's first *observed* positive rating. Activity
    counts positive ratings given or received in the preceding 90 days.
    This is a sensitivity benchmark, not a causal model of platform exposure.
    """
    ids = pd.Index(sorted(set(positive.source) | set(positive.target)))
    lookup = {node: i for i, node in enumerate(ids)}
    n = len(ids)
    active = np.zeros(n, dtype=bool)
    first_seen = np.zeros(n, dtype=float)
    indegree = np.zeros(n, dtype=int)
    recent = np.zeros(n, dtype=int)
    rated = [set() for _ in range(n)]
    history = deque()
    observed = np.zeros(7, dtype=int)
    expected = np.zeros(7, dtype=float)
    covered = eligible = first_time = small_stratum = 0
    candidates_sizes = []
    for source, target, _, time in positive[["source", "target", "rating", "time"]].itertuples(index=False, name=None):
        u, v = lookup[source], lookup[target]
        while history and history[0][0] < time - WINDOW:
            _, old_u, old_v = history.popleft()
            recent[old_u] -= 1
            recent[old_v] -= 1
        if active[v]:
            eligible += 1
            # Coarse groups keep comparisons understandable.
            tenure = (time - first_seen) / 86400
            tenure_group = np.digitize(tenure, [90, 365])
            activity_group = np.digitize(recent, [1, 3, 10])
            mask = active & (tenure_group == tenure_group[v]) & (activity_group == activity_group[v])
            mask[u] = False
            choices = np.flatnonzero(mask)
            choices = np.array([w for w in choices if w not in rated[u]], dtype=int)
            if len(choices) >= 5 and v in choices:
                covered += 1
                candidates_sizes.append(len(choices))
                observed[degree_bin(indegree[v])] += 1
                bins = np.bincount([degree_bin(d) for d in indegree[choices]], minlength=7)
                expected += bins / len(choices)
            else:
                small_stratum += 1
        else:
            first_time += 1
        for w in (u, v):
            if not active[w]:
                active[w] = True
                first_seen[w] = time
        indegree[v] += 1
        recent[u] += 1
        recent[v] += 1
        rated[u].add(v)
        history.append((time, u, v))
    table = pd.DataFrame({"prior_positive_in_degree": DEGREE_LABELS,
                          "observed_target_events": observed,
                          "matched_null_expected_events": expected})
    table["observed_over_expected"] = table.observed_target_events / table.matched_null_expected_events
    meta = {"existing_target_events": eligible, "first_time_target_events": first_time,
            "matched_events": covered, "excluded_small_stratum_events": small_stratum,
            "coverage_of_existing_target_events": covered / eligible,
            "median_matched_candidate_count": float(np.median(candidates_sizes)),
            "tenure_bins_days": ["under 90", "90 to 364", "365 or more"],
            "activity_bins_prior_90_days": ["0", "1 to 2", "3 to 9", "10 or more"],
            "minimum_candidates_including_chosen_target": 5}
    assert covered == observed.sum() and np.isclose(covered, expected.sum())
    return table, meta


def degree_preserving_null(positive, nodes):
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(positive[["source", "target"]].itertuples(index=False, name=None))
    original_degree = dict(graph.degree())
    rows = [{"network": "observed", "seed": -1, "transitivity": nx.transitivity(graph),
             "edges": graph.number_of_edges()}]
    swaps = 10 * graph.number_of_edges()
    for seed in SEEDS:
        rewired = graph.copy()
        nx.double_edge_swap(rewired, nswap=swaps, max_tries=20 * swaps, seed=seed)
        assert dict(rewired.degree()) == original_degree
        rows.append({"network": "degree_preserving_rewire", "seed": seed,
                     "transitivity": nx.transitivity(rewired), "edges": rewired.number_of_edges()})
    return pd.DataFrame(rows), swaps


def structural_evolution(positive):
    rows = []
    for year in range(2011, 2016):
        subset = positive[positive.year <= year]
        directed = nx.from_pandas_edgelist(subset, "source", "target", create_using=nx.DiGraph)
        projected = directed.to_undirected()
        largest = max(map(len, nx.connected_components(projected)))
        rows.append({"year_end": year, "active_users": len(directed),
                     "directed_positive_ratings": len(directed.edges),
                     "positive_projection_edges": len(projected.edges),
                     "largest_component_share_of_active": largest / len(directed),
                     "projection_transitivity": nx.transitivity(projected),
                     "directed_reciprocity": nx.reciprocity(directed)})
    return pd.DataFrame(rows)


def figures(matched, rewired, evolution):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(matched.prior_positive_in_degree, matched.observed_over_expected, color="#D99A36")
    ax.axhline(1, color="#173946", ls="--", lw=1)
    ax.set(xlabel="Prior positive in-degree", ylabel="Observed / matched expectation",
           title="Target choice after matching tenure and recent activity")
    fig.tight_layout()
    fig.savefig(OUT / "matched_target_choice.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    null = rewired[rewired.network != "observed"].transitivity
    ax.scatter(range(1, len(null) + 1), null, color="#49AFA6", label="Degree-preserving rewires")
    ax.axhline(rewired.iloc[0].transitivity, color="#D99A36", lw=2, label="Observed")
    ax.set(xlabel="Rewire seed", ylabel="Transitivity", title="Clustering beyond the degree sequence")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "degree_preserving_null.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
    for ax, column, label in zip(axes,
                                 ("largest_component_share_of_active", "projection_transitivity", "directed_reciprocity"),
                                 ("Largest component share", "Transitivity (undirected network)", "Directed reciprocity")):
        ax.plot(evolution.year_end, evolution[column], marker="o", color="#D99A36")
        ax.set(xlabel="Year end", ylabel=label)
        ax.set_xticks(evolution.year_end)
    axes[0].set_ylim(0.95, 1.0)
    fig.suptitle("Structure of the cumulative positive-rating network")
    fig.tight_layout()
    fig.savefig(OUT / "structural_evolution.png", dpi=180)
    plt.close(fig)


def main():
    checksum = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if checksum != SHA:
        raise ValueError(f"Unexpected SNAP file checksum: {checksum}")
    ratings = pd.read_csv(SOURCE, header=None, names=["source", "target", "rating", "time"])
    if ratings.duplicated(["source", "target"]).any() or not ratings.time.is_monotonic_increasing:
        raise ValueError("Expected unique ordered pairs and chronological file order")
    ratings["year"] = pd.to_datetime(ratings.time, unit="s", utc=True).dt.year
    positive = ratings[ratings.rating > 0].copy()
    OUT.mkdir(parents=True, exist_ok=True)
    matched, matched_meta = matched_target_choice(positive)
    rewired, swaps = degree_preserving_null(positive, sorted(set(ratings.source) | set(ratings.target)))
    evolution = structural_evolution(positive)
    matched.to_csv(OUT / "matched_target_choice.csv", index=False)
    rewired.to_csv(OUT / "degree_preserving_null.csv", index=False)
    evolution.to_csv(OUT / "structural_evolution.csv", index=False)
    metadata = {"source_sha256": checksum, "matched_choice": matched_meta,
                "rewire": {"projection": "simple undirected positive graph, all observed users",
                           "seeds": SEEDS, "successful_swaps_per_replicate": swaps,
                           "method": "NetworkX double_edge_swap, preserves each projected node degree"},
                "evolution": "Cumulative positive ratings at 2011-2015 UTC year ends; active users only"}
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    figures(matched, rewired, evolution)
    print(matched.round(3).to_string(index=False))
    print(json.dumps(matched_meta, indent=2))
    print(rewired.round(4).to_string(index=False))
    print(evolution.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
