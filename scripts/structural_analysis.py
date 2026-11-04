"""Reproducible structural baseline for the Bitcoin OTC rating network.

Run from the project root: python scripts/structural_analysis.py
The SNAP source file must be present in data/; see data/README.md.
"""

from pathlib import Path
import hashlib
import json

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "outputs" / "structure"
SEED = 2026
MODEL_REPLICATES = 10
BETWEENNESS_SOURCES = 64
PATH_SOURCES = 32


def load_graphs():
    ratings = pd.read_csv(
        SOURCE, header=None, names=["source", "target", "rating", "time"]
    )
    if ratings.isna().any().any() or ratings.duplicated(["source", "target"]).any():
        raise ValueError("Unexpected missing values or repeated directed pairs")
    nodes = sorted(set(ratings.source) | set(ratings.target))
    positive = ratings[ratings.rating > 0]
    directed = nx.DiGraph()
    directed.add_nodes_from(nodes)
    for row in positive.itertuples(index=False):
        directed.add_edge(
            row.source, row.target,
            rating=int(row.rating),
            weight=int(row.rating),
            time_unix=float(row.time),
        )
    # The source score is retained as an edge attribute. Reported structural
    # measures and shortest paths use unweighted links (weight=None).
    projection = nx.Graph()
    projection.add_nodes_from(nodes)
    projection.add_edges_from(
        positive[["source", "target"]].itertuples(index=False, name=None)
    )
    return ratings, directed, projection


def sampled_mean_path_length(graph, sources=PATH_SOURCES, seed=SEED):
    """Mean of reachable distances from sampled sources in one connected graph."""
    rng = np.random.default_rng(seed)
    selected = rng.choice(list(graph), size=min(sources, len(graph)), replace=False)
    total = count = 0
    for node in selected:
        distances = nx.single_source_shortest_path_length(graph, int(node))
        total += sum(distances.values())
        count += len(distances) - 1
    return total / count


def summarize(graph, label, seed):
    degrees = np.fromiter((d for _, d in graph.degree()), dtype=int)
    largest_nodes = max(nx.connected_components(graph), key=len)
    largest = graph.subgraph(largest_nodes)
    return {
        "network": label,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "mean_degree": float(degrees.mean()),
        "degree_p95": float(np.quantile(degrees, 0.95)),
        "max_degree": int(degrees.max()),
        "density": nx.density(graph),
        "transitivity": nx.transitivity(graph),
        "components": nx.number_connected_components(graph),
        "largest_component_nodes": len(largest_nodes),
        "largest_component_share": len(largest_nodes) / len(graph),
        "sampled_mean_path_lcc": sampled_mean_path_length(largest, seed=seed),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ratings, directed, projection = load_graphs()
    n, m = projection.number_of_nodes(), projection.number_of_edges()
    # BA accepts an integer links-per-new-node parameter. m=3 is the closest
    # valid BA choice here; the remaining edge-count mismatch is reported.
    ba_links = round(m / n)
    observed = summarize(projection, "observed", SEED)
    rows = [observed]
    for i in range(MODEL_REPLICATES):
        seed = SEED + i
        er = nx.gnm_random_graph(n, m, seed=seed)
        ba = nx.barabasi_albert_graph(n, ba_links, seed=seed)
        rows.append(summarize(er, f"ER_{i + 1:02d}", seed))
        rows.append(summarize(ba, f"BA_{i + 1:02d}", seed))
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "network_metrics.csv", index=False)

    # Centrality remains directed. The approximation samples source vertices;
    # seed and sample count are fixed and reported rather than called exact.
    between = nx.betweenness_centrality(
        directed, k=BETWEENNESS_SOURCES, normalized=True, seed=SEED
    )
    centrality = pd.DataFrame({
        "node": list(directed),
        "positive_in_degree": [directed.in_degree(v) for v in directed],
        "positive_out_degree": [directed.out_degree(v) for v in directed],
        "betweenness_approx": [between[v] for v in directed],
    })
    centrality.sort_values("positive_in_degree", ascending=False).to_csv(
        OUT / "directed_centrality.csv", index=False
    )

    # Standard Louvain modularity is applied to the positive undirected
    # projection. It does not use the original signs or directions.
    communities = nx.community.louvain_communities(projection, seed=SEED)
    assignment = pd.DataFrame(
        [(node, i, len(group)) for i, group in enumerate(communities) for node in group],
        columns=["node", "community", "community_size"],
    )
    assignment.sort_values("node").to_csv(OUT / "communities.csv", index=False)
    modularity = nx.community.modularity(projection, communities)
    largest_observed = projection.subgraph(max(nx.connected_components(projection), key=len))
    observed_diameter = nx.diameter(largest_observed, usebounds=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    for graph, label in ((projection, "Observed"), (er, "ER example"), (ba, "BA example")):
        counts = pd.Series(dict(graph.degree())).value_counts().sort_index()
        counts = counts[counts.index > 0]
        ax.loglog(counts.index, counts / graph.number_of_nodes(), marker="o", linestyle="none", markersize=3, alpha=0.65, label=label)
    ax.set(xlabel="Undirected degree k", ylabel="Fraction of nodes with degree k", title="Degree distributions (one model realization shown)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "degree_distributions.png", dpi=180)
    plt.close(fig)

    metadata = {
        "source_rows": len(ratings),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "positive_directed_edges": directed.number_of_edges(),
        "projection_edges": m,
        "reciprocal_positive_pairs_collapsed": directed.number_of_edges() - m,
        "ba_links_per_new_node": ba_links,
        "ba_edge_count_mismatch_fraction": (ba.number_of_edges() - m) / m,
        "model_replicates": MODEL_REPLICATES,
        "betweenness_source_sample": BETWEENNESS_SOURCES,
        "path_source_sample": PATH_SOURCES,
        "louvain_community_count": len(communities),
        "louvain_modularity": modularity,
        "seed": SEED,
        "largest_observed_component_diameter_exact": observed_diameter,
        "diameter_method": "NetworkX diameter with usebounds=True on the largest positive undirected component",
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(summary.groupby(summary.network.str.split("_").str[0]).agg({
        "edges": ["mean", "std"], "mean_degree": ["mean", "std"],
        "transitivity": ["mean", "std"], "max_degree": ["mean", "std"],
        "largest_component_share": ["mean", "std"],
        "sampled_mean_path_lcc": ["mean", "std"],
    }).round(4).to_string())
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
