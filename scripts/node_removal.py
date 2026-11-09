"""Compare random failure with degree-targeted removal on the positive projection."""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from structural_analysis import load_graphs


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "robustness"
SEED = 2026
REPLICATES = 30
FRACTIONS = (0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1)


def largest_share(graph, original_n):
    if not graph:
        return 0.0
    return len(max(nx.connected_components(graph), key=len)) / original_n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    _, _, graph = load_graphs()
    n = len(graph)
    nodes = np.array(sorted(graph), dtype=int)
    # Rank users once using degree in the original graph. Ties use user ID.
    ranked = [u for u, _ in sorted(graph.degree(), key=lambda item: (-item[1], item[0]))]
    rng = np.random.default_rng(SEED)
    rows = []
    for fraction in FRACTIONS:
        k = round(fraction * n)
        targeted = graph.copy()
        targeted.remove_nodes_from(ranked[:k])
        rows.append({"strategy": "highest_degree_first", "replicate": 0,
                     "removed_nodes": k, "removed_fraction": k / n,
                     "largest_component_fraction_original_nodes": largest_share(targeted, n)})
        for replicate in range(REPLICATES):
            # Start from a fresh copy for each random draw.
            random_graph = graph.copy()
            random_graph.remove_nodes_from(rng.choice(nodes, size=k, replace=False))
            rows.append({"strategy": "uniform_random", "replicate": replicate + 1,
                         "removed_nodes": k, "removed_fraction": k / n,
                         "largest_component_fraction_original_nodes": largest_share(random_graph, n)})

    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "node_removal_replicates.csv", index=False)
    summary = detail.groupby(["strategy", "removed_nodes", "removed_fraction"], as_index=False)[
        "largest_component_fraction_original_nodes"
    ].agg(["mean", "std"])
    summary.to_csv(OUT / "node_removal_summary.csv", index=False)

    random = summary[summary.strategy == "uniform_random"]
    targeted = summary[summary.strategy == "highest_degree_first"]
    fig, ax = plt.subplots(figsize=(7, 4.3))
    ax.plot(100 * random.removed_fraction, random["mean"], marker="o", label="Uniform random (30 runs)")
    ax.fill_between(100 * random.removed_fraction,
                    random["mean"] - random["std"].fillna(0),
                    random["mean"] + random["std"].fillna(0), alpha=0.18)
    ax.plot(100 * targeted.removed_fraction, targeted["mean"], marker="s",
            label="Highest original degree first")
    ax.set(xlabel="Users removed (% of original network)",
           ylabel="Largest component / original users",
           title="Node removal in the undirected positive network")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "node_removal.png", dpi=180)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
