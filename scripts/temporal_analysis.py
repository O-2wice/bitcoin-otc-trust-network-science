"""Temporal rating accumulation and degree-conditioned target choice.

Run from project root: python scripts/temporal_analysis.py
The analysis uses positive ratings only and retains file order for timestamp ties.
"""

from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "outputs" / "temporal"
EXPECTED_SHA = "6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373"
DEGREE_BINS = [(0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (16, 31), (32, None)]
LABELS = ["0", "1", "2-3", "4-7", "8-15", "16-31", "32+"]


def bucket(degree):
    for i, (low, high) in enumerate(DEGREE_BINS):
        if degree >= low and (high is None or degree <= high):
            return i
    raise ValueError(degree)


def gini(values):
    """Return 0 for equal incoming counts and larger values for more inequality."""
    values = np.asarray(values, dtype=float)
    if len(values) == 0 or values.sum() == 0:
        return float("nan")
    ordered = np.sort(values)
    n = len(ordered)
    return float((2 * np.arange(1, n + 1) - n - 1) @ ordered / (n * ordered.sum()))


def annual_snapshots(positive, threshold):
    # The first and last years are partial; use full years for the trend.
    rows = []
    for year in range(2011, 2016):
        observed = positive[positive.year <= year]
        nodes = sorted(set(observed.source) | set(observed.target))
        incoming = observed.groupby("target").size().reindex(nodes, fill_value=0).to_numpy()
        k = max(1, int(np.ceil(0.01 * len(nodes))))
        rows.append({
            "rating_threshold": threshold,
            "year_end": year,
            "active_positive_users": len(nodes),
            "cumulative_positive_ratings": len(observed),
            "top_1_percent_incoming_share": np.sort(incoming)[-k:].sum() / incoming.sum(),
            "incoming_degree_gini": gini(incoming),
            "top_group_size": k,
        })
    return pd.DataFrame(rows)


def target_choice(positive):
    """Compare selected prior-degree bins with uniform eligible-target exposure.

    At each event, candidates are users seen in an earlier positive event,
    excluding the rater and users they already rated positively. First-time targets are outside this
    candidate set and omitted from the target-choice comparison. The null
    expectation is uniform choice among eligible active users at that event.
    """
    indegree = Counter()
    counts = Counter()  # active users by current in-degree
    active = set()
    rated_targets = defaultdict(set)
    observed = np.zeros(len(DEGREE_BINS), dtype=int)
    expected = np.zeros(len(DEGREE_BINS), dtype=float)
    yearly_observed = defaultdict(lambda: np.zeros(len(DEGREE_BINS), dtype=int))
    yearly_expected = defaultdict(lambda: np.zeros(len(DEGREE_BINS), dtype=float))
    eligible_events = 0
    new_target_events = 0
    insufficient_events = 0
    for source, target, year in positive[["source", "target", "year"]].itertuples(index=False, name=None):
        # Use the network as it looked BEFORE this rating. This avoids giving
        # the target credit for the current rating when measuring prior degree.
        if target in active:
            # Available targets = previously seen users, except the rater and
            # users whom this rater already rated positively.
            choices = len(active) - int(source in active) - len(rated_targets[source])
            if choices:
                eligible_events += 1
                unavailable_by_degree = Counter(indegree[v] for v in rated_targets[source])
                for degree, count in counts.items():
                    available = count - int(source in active and indegree[source] == degree) - unavailable_by_degree[degree]
                    # If choice were uniform, this fraction is the chance of
                    # selecting someone with this prior in-degree.
                    increment = available / choices
                    expected[bucket(degree)] += increment
                    yearly_expected[year][bucket(degree)] += increment
                observed[bucket(indegree[target])] += 1
                yearly_observed[year][bucket(indegree[target])] += 1
            else:
                insufficient_events += 1
        else:
            new_target_events += 1
        # Update the network AFTER recording the observed and expected counts.
        for node in (source, target):
            if node not in active:
                active.add(node)
                counts[0] += 1
        old = indegree[target]
        counts[old] -= 1
        if counts[old] == 0:
            del counts[old]
        indegree[target] += 1
        counts[old + 1] += 1
        rated_targets[source].add(target)
    result = pd.DataFrame({
        "prior_positive_in_degree": LABELS,
        "observed_target_events": observed,
        "uniform_null_expected_events": expected,
    })
    result["observed_over_expected"] = result.observed_target_events / result.uniform_null_expected_events
    by_year = pd.DataFrame([
        {"year": year, "prior_positive_in_degree": label,
         "observed_target_events": int(yearly_observed[year][i]),
         "uniform_null_expected_events": float(yearly_expected[year][i]),
         "observed_over_expected": float(yearly_observed[year][i] / yearly_expected[year][i]) if yearly_expected[year][i] else None}
        for year in sorted(yearly_observed) for i, label in enumerate(LABELS)
    ])
    metadata = {
        "eligible_existing_target_events": eligible_events,
        "first_time_target_events_excluded": new_target_events,
        "insufficient_candidate_events_excluded": insufficient_events,
        "expected_sum": float(expected.sum()),
        "observed_sum": int(observed.sum()),
    }
    return result, by_year, metadata


def main():
    checksum = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if checksum != EXPECTED_SHA:
        raise ValueError(f"Unexpected source SHA-256: {checksum}")
    ratings = pd.read_csv(SOURCE, header=None, names=["source", "target", "rating", "time"])
    if not ratings.time.is_monotonic_increasing:
        raise ValueError("Source ratings are not time ordered")
    ratings["year"] = pd.to_datetime(ratings.time, unit="s", utc=True).dt.year
    positive = ratings[ratings.rating > 0].copy()
    OUT.mkdir(parents=True, exist_ok=True)
    annual = annual_snapshots(positive, 1)
    annual_strong = annual_snapshots(ratings[ratings.rating >= 5].copy(), 5)
    choice, choice_year, choice_meta = target_choice(positive)
    annual.to_csv(OUT / "annual_snapshots.csv", index=False)
    annual_strong.to_csv(OUT / "annual_snapshots_rating_ge5.csv", index=False)
    choice.to_csv(OUT / "target_choice_by_prior_degree.csv", index=False)
    choice_year.to_csv(OUT / "target_choice_by_year.csv", index=False)
    metadata = {
        "source_sha256": checksum,
        "positive_ratings": len(positive),
        "full_years": [2011, 2012, 2013, 2014, 2015],
        "timestamp_ties": int(positive.time.duplicated().sum()),
        "event_order": "SNAP file order for equal timestamps",
        "null": "uniform eligible active target at each positive-rating event, excluding the rater and users already rated positively by that rater",
        "limits": "descriptive association; activity, tenure, and unobserved platform membership may confound target choice",
        **choice_meta,
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(annual.year_end, annual.active_positive_users, marker="o", label="Users")
    axes[0].set(xlabel="Year end (UTC)", ylabel="Users seen in positive ratings", title="Observed network growth")
    axes[0].set_xticks(annual.year_end)
    ax2 = axes[0].twinx()
    ax2.plot(annual.year_end, annual.cumulative_positive_ratings, marker="s", color="tab:orange", label="Ratings")
    ax2.set_ylabel("Cumulative positive ratings")
    axes[1].plot(annual.year_end, annual.top_1_percent_incoming_share, marker="o", label="Top 1% share")
    axes[1].plot(annual.year_end, annual.incoming_degree_gini, marker="s", label="Gini")
    axes[1].set(xlabel="Year end (UTC)", ylabel="Concentration", title="Incoming positive ratings")
    axes[1].set_xticks(annual.year_end)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "growth_and_concentration.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(choice.prior_positive_in_degree, choice.observed_over_expected)
    ax.axhline(1, color="black", linestyle="--", linewidth=1)
    ax.set(xlabel="Target's positive in-degree before rating", ylabel="Observed / uniform-null expected", title="Degree-conditioned target choice")
    fig.tight_layout()
    fig.savefig(OUT / "target_choice_ratio.png", dpi=180)
    plt.close(fig)
    print(annual.round(4).to_string(index=False))
    print("Sensitivity: ratings >= 5")
    print(annual_strong.round(4).to_string(index=False))
    print(choice.round(3).to_string(index=False))
    print(choice_year[choice_year.prior_positive_in_degree == "32+"].round(3).to_string(index=False))
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
