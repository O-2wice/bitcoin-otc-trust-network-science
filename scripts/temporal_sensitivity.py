"""Separate concentration in new yearly ratings from accumulated ratings.

Run from the project root: python scripts/temporal_sensitivity.py
The fixed-cohort check follows users observed by the end of 2011. It counts
ratings received by those users from any source, including later entrants.
"""

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from temporal_analysis import EXPECTED_SHA, SOURCE, annual_snapshots, gini


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "sensitivity"
YEARS = range(2011, 2016)
EQUAL_VOLUME_DRAWS = 1000
EQUAL_VOLUME_FRACTION = 0.8
SEED = 2026


def top_percent_share(sources, targets):
    """Top 1% incoming share among users appearing in these ratings."""
    users = np.unique(np.concatenate([sources, targets]))
    counts = np.bincount(np.searchsorted(users, targets), minlength=len(users))
    top_count = max(1, int(np.ceil(0.01 * len(users))))
    return np.sort(counts)[-top_count:].sum() / counts.sum()


def equal_volume_check(positive):
    """Ask whether the annual fall survives equal rating volume in every year.

    The top 1% contains 25 users in 2013 but only 4 in 2015, and the share depends
    on how many ratings a year has. Every year, including the smallest, is therefore
    redrawn to 80% of the smallest year's rating count, so each one has a spread.
    The share held by a fixed number of recipients gives a second view.
    """
    rng = np.random.default_rng(SEED)
    yearly = {year: positive[positive.year == year] for year in YEARS}
    size = int(EQUAL_VOLUME_FRACTION * min(len(part) for part in yearly.values()))
    fixed_recipients = max(1, int(np.ceil(0.01 * len(
        set(yearly[2015].source) | set(yearly[2015].target)))))
    rows = []
    for year, part in yearly.items():
        sources, targets = part.source.to_numpy(), part.target.to_numpy()
        equal, equal_fixed = [], []
        for _ in range(EQUAL_VOLUME_DRAWS):
            chosen = rng.choice(len(part), size, replace=False)
            equal.append(top_percent_share(sources[chosen], targets[chosen]))
            counts = np.bincount(np.unique(targets[chosen], return_inverse=True)[1])
            equal_fixed.append(np.sort(counts)[-fixed_recipients:].sum() / size)
        counts = part.groupby("target").size().to_numpy()
        rows.append({
            "year": year, "ratings": len(part),
            "top_1_percent_share": top_percent_share(sources, targets),
            "equal_volume_ratings": size,
            "equal_volume_share_mean": np.mean(equal),
            "equal_volume_share_low": np.quantile(equal, 0.025),
            "equal_volume_share_high": np.quantile(equal, 0.975),
            "fixed_recipients": fixed_recipients,
            "fixed_recipients_share": np.sort(counts)[-fixed_recipients:].sum() / len(part),
            "fixed_recipients_equal_volume_mean": np.mean(equal_fixed),
            "fixed_recipients_equal_volume_low": np.quantile(equal_fixed, 0.025),
            "fixed_recipients_equal_volume_high": np.quantile(equal_fixed, 0.975),
        })
    return pd.DataFrame(rows)


def summarize_incoming(ratings, users):
    """Count one incoming link per rating; include users receiving zero."""
    counts = ratings.groupby("target").size().reindex(users, fill_value=0).to_numpy()
    top_count = max(1, int(np.ceil(0.01 * len(users))))
    total = int(counts.sum())
    assert total > 0 and len(counts) == len(users)
    share = float(np.sort(counts)[-top_count:].sum() / total)
    inequality = gini(counts)
    assert 0 <= share <= 1 and 0 <= inequality <= 1
    return {"users_in_denominator": len(users), "incoming_ratings_in_denominator": total,
            "top_group_size": top_count, "top_1_percent_incoming_share": share,
            "incoming_degree_gini": inequality}


def main():
    checksum = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if checksum != EXPECTED_SHA:
        raise ValueError("Unexpected source checksum")
    ratings = pd.read_csv(SOURCE, header=None, names=["source", "target", "rating", "time"])
    ratings["year"] = pd.to_datetime(ratings.time, unit="s", utc=True).dt.year
    positive = ratings[ratings.rating > 0].copy()
    before_2012 = positive[positive.year <= 2011]
    cohort = sorted(set(before_2012.source) | set(before_2012.target))

    annual_rows, fixed_rows = [], []
    for year in YEARS:
        yearly = positive[positive.year == year]
        users = sorted(set(yearly.source) | set(yearly.target))
        annual = {"year": year, **summarize_incoming(yearly, users)}
        assert annual["incoming_ratings_in_denominator"] == len(yearly)
        annual_rows.append(annual)

        cumulative = positive[positive.year <= year]
        fixed = {"year_end": year, **summarize_incoming(cumulative, cohort)}
        fixed["share_of_all_cumulative_ratings_received_by_cohort"] = (
            fixed["incoming_ratings_in_denominator"] / len(cumulative)
        )
        fixed_rows.append(fixed)

    annual = pd.DataFrame(annual_rows)
    fixed = pd.DataFrame(fixed_rows)
    cumulative = annual_snapshots(positive, threshold=1)
    assert fixed.users_in_denominator.nunique() == 1
    assert fixed.incoming_ratings_in_denominator.is_monotonic_increasing

    OUT.mkdir(parents=True, exist_ok=True)
    annual.to_csv(OUT / "annual_only_concentration.csv", index=False)
    fixed.to_csv(OUT / "fixed_2011_cohort_concentration.csv", index=False)
    equal_volume = equal_volume_check(positive)
    equal_volume.to_csv(OUT / "annual_equal_volume_check.csv", index=False)
    metadata = {
        "source_sha256": checksum,
        "edge_rule": "One directed positive rating per observed ordered pair; score > 0",
        "annual_users": "Users appearing as source or target in that UTC calendar year's positive ratings, including zero incoming counts",
        "annual_rating_denominator": "All positive ratings recorded within that UTC calendar year only",
        "fixed_cohort": "All users appearing in a positive rating by 2011 UTC year end; cumulative incoming ratings from any source",
        "fixed_cohort_size": len(cohort),
        "fixed_cohort_rating_denominator": "Cumulative positive ratings received by members of the fixed cohort, not all ratings in the network",
        "top_group": "Ceiling of 1% of each specified user population; highest incoming counts reselected at each snapshot",
        "equal_volume_check": f"{EQUAL_VOLUME_DRAWS} redraws of every year's ratings to {EQUAL_VOLUME_FRACTION:.0%} of the smallest year's count, plus the share held by a fixed number of recipients",
        "limits": "Annual samples differ across years; fixed cohort is selected early and does not represent later entrants. Neither view identifies active trust relationships or a causal mechanism.",
    }
    (OUT / "temporal_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].plot(cumulative.year_end, 100 * cumulative.top_1_percent_incoming_share,
                 marker="o", color="#D99A36", label="All ratings accumulated so far")
    axes[0].plot(annual.year, 100 * annual.top_1_percent_incoming_share,
                 marker="s", color="#287D8E", label="Ratings recorded in that year only")
    axes[0].set(xlabel="Year (UTC)", ylabel="Top 1% share of incoming ratings (%)",
                title="Accumulated and new yearly ratings differ")
    axes[0].legend(fontsize=8)
    axes[1].bar(annual.year, annual.incoming_ratings_in_denominator, color="#287D8E")
    axes[1].set(xlabel="Year (UTC)", ylabel="Positive ratings recorded in that year",
                title="Rating volume also changes")
    for ax in axes:
        ax.set_xticks(list(YEARS))
    fig.tight_layout()
    fig.savefig(OUT / "annual_vs_cumulative_concentration.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(cumulative.year_end, 100 * cumulative.top_1_percent_incoming_share,
            marker="o", color="#D99A36", label="All users observed by each year end")
    ax.plot(fixed.year_end, 100 * fixed.top_1_percent_incoming_share,
            marker="s", color="#287D8E", label="Fixed group observed by end of 2011")
    ax.set(xlabel="Year end (UTC)", ylabel="Top 1% share within each population (%)",
           title="Cumulative concentration rises in a fixed cohort too", xticks=list(YEARS))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fixed_cohort_concentration.png", dpi=200)
    plt.close(fig)
    print("Annual-only ratings:\n" + annual.round(4).to_string(index=False))
    print("Fixed 2011 cohort:\n" + fixed.round(4).to_string(index=False))
    print("Equal-volume check:\n" + equal_volume.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
