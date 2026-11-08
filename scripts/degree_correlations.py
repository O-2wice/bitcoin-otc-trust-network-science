"""Degree correlations and assortativity of the Bitcoin OTC positive network.

Run from the repository root: python scripts/degree_correlations.py
The SNAP source file must be present in data/; see data/README.md.

Questions answered
  1. Do high-degree users link to other high-degree users (assortative, r > 0)
     or to low-degree users (disassortative, r < 0)?
  2. Is that more than the degrees alone would force? A degree-preserving
     rewire keeps every user's degree but randomises who is linked to whom,
     so any difference from the rewires comes from the wiring itself.

The undirected analysis uses the same positive projection as the structural
analysis, the same eight seeds and the same swap budget as flagship_checks.py.
A directed version (out/in degree mixing) is reported as a second, smaller table.
"""

from pathlib import Path
import hashlib
import json

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from structural_analysis import load_graphs


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "outputs" / "correlations"
EXPECTED_SHA = "6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373"
SEEDS = tuple(range(2026, 2034))        # the same eight seeds as flagship_checks.py
SWAPS_PER_EDGE = 10                     # the same swap budget as flagship_checks.py
MIN_NODES_FOR_FIT = 5                   # a degree needs this many users to enter the k_nn fit
DIRECTED_TYPES = (("out", "in"), ("out", "out"), ("in", "in"), ("in", "out"))


def knn_curve(graph):
    """Average neighbour degree k_nn(k) of users with degree k (degree 0 excluded)."""
    knn = nx.average_degree_connectivity(graph)
    degrees = np.array(sorted(k for k in knn if k > 0))
    return degrees, np.array([knn[k] for k in degrees])


def fit_mu(graph):
    """Exponent mu in k_nn(k) ~ k^mu, or NaN when the data cannot support a fit.

    Only degrees held by at least MIN_NODES_FOR_FIT users are used, and a fit needs
    at least six such degrees spanning a factor of five or more.
    """
    degrees, knn = knn_curve(graph)
    counts = np.bincount([d for _, d in graph.degree()])
    keep = np.array([counts[k] >= MIN_NODES_FOR_FIT for k in degrees])
    if keep.sum() < 6 or degrees[keep].max() / degrees[keep].min() < 5:
        return float("nan")
    return float(np.polyfit(np.log(degrees[keep]), np.log(knn[keep]), 1)[0])


def structural_cutoff(graph):
    """k_s = sqrt(<k> N) = sqrt(2E). Hubs above this force negative degree correlations."""
    return float(np.sqrt(2 * graph.number_of_edges()))


def neutral_knn(graph):
    """<k^2>/<k>: the k_nn(k) of a network with no degree correlations."""
    degrees = np.array([d for _, d in graph.degree()])
    return float((degrees ** 2).mean() / degrees.mean())


def directed_assortativity(directed):
    return {f"{x}_{y}": nx.degree_assortativity_coefficient(directed, x=x, y=y)
            for x, y in DIRECTED_TYPES}


def summarise(observed, rewired):
    """Observed value against the spread of the rewired values."""
    rewired = np.asarray(rewired, dtype=float)
    std = rewired.std(ddof=1)
    return {"observed": observed,
            "rewired_mean": rewired.mean(), "rewired_std": std,
            "rewired_min": rewired.min(), "rewired_max": rewired.max(),
            "z_score": (observed - rewired.mean()) / std if std > 0 else float("nan"),
            "outside_rewired_range": bool(observed < rewired.min() or observed > rewired.max())}


def run_nulls(projection, directed):
    """Degree-preserving rewires of the undirected and directed graphs."""
    ks, knn_obs = knn_curve(projection)
    original_degree = dict(projection.degree())
    swaps = SWAPS_PER_EDGE * projection.number_of_edges()
    directed_swaps = SWAPS_PER_EDGE * directed.number_of_edges()
    directed_in, directed_out = dict(directed.in_degree()), dict(directed.out_degree())

    rows, knn_rows, mu_rewired = [], [], []
    for seed in SEEDS:
        rewired = projection.copy()
        nx.double_edge_swap(rewired, nswap=swaps, max_tries=20 * swaps, seed=seed)
        assert dict(rewired.degree()) == original_degree

        rewired_directed = directed.copy()
        nx.directed_edge_swap(rewired_directed, nswap=directed_swaps,
                              max_tries=20 * directed_swaps, seed=seed)
        assert dict(rewired_directed.in_degree()) == directed_in
        assert dict(rewired_directed.out_degree()) == directed_out

        knn_h = nx.average_degree_connectivity(rewired)
        knn_rows.append([knn_h[k] for k in ks])      # same degrees, so the same set of k
        mu_rewired.append(fit_mu(rewired))
        rows.append({"seed": seed,
                     "r_undirected": nx.degree_assortativity_coefficient(rewired),
                     **{f"r_{key}": value
                        for key, value in directed_assortativity(rewired_directed).items()}})
        print(f"  rewire {seed}: r = {rows[-1]['r_undirected']:+.4f}")
    return pd.DataFrame(rows), np.array(knn_rows), mu_rewired, swaps, directed_swaps


def figures(summary, rewires, directed_table, ks, knn_obs, knn_band, neutral, cutoff, max_degree):
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))

    mean, low, high = knn_band
    axes[0].fill_between(ks, low, high, color="gray", alpha=0.25, label="95% of rewires")
    axes[0].plot(ks, mean, "s-", color="gray", ms=3, lw=1, label="rewired mean")
    axes[0].plot(ks, knn_obs, "o-", color="firebrick", ms=4, lw=1,
                 label=f"observed (r = {summary['observed']:+.3f})")
    axes[0].axhline(neutral, color="black", ls="--", lw=1, label="no correlations: <k²>/<k>")
    axes[0].set_xscale("log"); axes[0].set_yscale("log")
    axes[0].set_xlabel("degree k"); axes[0].set_ylabel("k_nn(k)")
    axes[0].set_title("Average neighbour degree"); axes[0].legend(fontsize=8)

    axes[1].hist(rewires["r_undirected"], bins=8, color="gray", alpha=0.8,
                 label="8 degree-preserving rewires")
    axes[1].axvline(summary["observed"], color="firebrick", lw=2.5,
                    label=f"observed r = {summary['observed']:+.3f}")
    axes[1].set_xlabel("assortativity r"); axes[1].set_ylabel("count")
    axes[1].set_title(f"Observed vs rewired (k_max = {max_degree}, cutoff k_s = {cutoff:.0f})")
    axes[1].legend(fontsize=8)

    x = np.arange(len(directed_table))
    axes[2].bar(x - 0.2, directed_table["observed"], 0.4, color="firebrick", label="observed")
    axes[2].bar(x + 0.2, directed_table["rewired_mean"], 0.4, color="gray",
                yerr=[directed_table["rewired_mean"] - directed_table["rewired_min"],
                      directed_table["rewired_max"] - directed_table["rewired_mean"]],
                capsize=3, label="rewired mean (min to max)")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels([t.replace("_", "→") for t in directed_table["type"]])
    axes[2].axhline(0, color="black", lw=0.8)
    axes[2].set_xlabel("degree type at the rater → degree type at the rated user")
    axes[2].set_ylabel("directed assortativity")
    axes[2].set_title("Directed version (positive ratings)"); axes[2].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "degree_correlations.png", dpi=180)
    plt.close(fig)


def main():
    checksum = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if checksum != EXPECTED_SHA:
        raise ValueError("Unexpected source dataset checksum; see data/README.md")
    OUT.mkdir(parents=True, exist_ok=True)

    ratings, directed, projection = load_graphs()
    degrees = np.array([d for _, d in projection.degree()])
    print(f"Positive projection: {projection.number_of_nodes()} users, "
          f"{projection.number_of_edges()} links")

    print("Degree-preserving rewires:")
    rewires, knn_rewired, mu_rewired, swaps, directed_swaps = run_nulls(projection, directed)

    # Undirected summary
    observed_r = nx.degree_assortativity_coefficient(projection)
    summary = summarise(observed_r, rewires["r_undirected"])
    ks, knn_obs = knn_curve(projection)
    cutoff = structural_cutoff(projection)
    mu_obs = fit_mu(projection)
    summary_row = {
        "nodes": projection.number_of_nodes(), "edges": projection.number_of_edges(),
        "mean_degree": float(degrees.mean()), "max_degree": int(degrees.max()),
        "structural_cutoff": cutoff,
        "r_observed": summary["observed"], "r_rewired_mean": summary["rewired_mean"],
        "r_rewired_std": summary["rewired_std"], "r_rewired_min": summary["rewired_min"],
        "r_rewired_max": summary["rewired_max"], "z_score": summary["z_score"],
        "observed_outside_rewired_range": summary["outside_rewired_range"],
        "mu_observed": mu_obs, "mu_rewired_mean": float(np.nanmean(mu_rewired))
        if not np.all(np.isnan(mu_rewired)) else float("nan"),
    }
    pd.DataFrame([summary_row]).to_csv(OUT / "correlation_summary.csv", index=False)

    # Directed summary
    observed_directed = directed_assortativity(directed)
    directed_rows = []
    for x, y in DIRECTED_TYPES:
        key = f"{x}_{y}"
        directed_rows.append({"type": key, **summarise(observed_directed[key], rewires[f"r_{key}"])})
    directed_table = pd.DataFrame(directed_rows)
    directed_table.to_csv(OUT / "directed_assortativity.csv", index=False)

    # All individual values, observed first (seed -1, as in outputs/flagship)
    observed_row = {"seed": -1, "r_undirected": observed_r,
                    **{f"r_{k}": v for k, v in observed_directed.items()}}
    pd.concat([pd.DataFrame([observed_row]), rewires]).to_csv(
        OUT / "rewired_assortativity.csv", index=False)

    # k_nn(k) table
    low, high = np.percentile(knn_rewired, [2.5, 97.5], axis=0)
    counts = np.bincount(degrees)
    pd.DataFrame({"degree": ks, "users_with_degree": counts[ks], "knn_observed": knn_obs,
                  "knn_rewired_mean": knn_rewired.mean(axis=0),
                  "knn_rewired_p2_5": low, "knn_rewired_p97_5": high}).to_csv(
        OUT / "knn_by_degree.csv", index=False)

    figures(summary, rewires, directed_table, ks, knn_obs,
            (knn_rewired.mean(axis=0), low, high), neutral_knn(projection), cutoff,
            int(degrees.max()))

    metadata = {
        "source_sha256": checksum,
        "undirected_graph": "positive projection, all observed users (users without positive "
                            "links have no edges and do not affect r)",
        "directed_graph": "positive ratings, direction kept, reciprocal ratings kept",
        "seeds": SEEDS, "undirected_swaps_per_rewire": swaps,
        "directed_swaps_per_rewire": directed_swaps,
        "method": "NetworkX double_edge_swap (undirected) and directed_edge_swap (directed); "
                  "each preserves every user's degree (in- and out-degree for the directed case)",
        "structural_cutoff": "k_s = sqrt(2E) = sqrt(<k> N)",
        "k_nn_fit": f"mu reported only if at least 6 degrees held by >= {MIN_NODES_FOR_FIT} users "
                    "span a factor of 5; otherwise NaN",
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    print("\nUndirected assortativity")
    print(f"  observed r         = {summary['observed']:+.4f}")
    print(f"  rewired r          = {summary['rewired_mean']:+.4f} "
          f"(min {summary['rewired_min']:+.4f}, max {summary['rewired_max']:+.4f})")
    print(f"  outside all rewires: {summary['outside_rewired_range']},  z = {summary['z_score']:+.1f}")
    print(f"  k_max = {int(degrees.max())}, structural cutoff k_s = {cutoff:.0f}")
    print("Directed (rater degree type -> rated degree type)")
    for row in directed_rows:
        print(f"  {row['type']:8s} observed {row['observed']:+.4f}   rewired {row['rewired_mean']:+.4f}")
    print(f"\nWrote results to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
