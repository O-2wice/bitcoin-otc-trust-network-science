"""Draw the entire positive undirected projection, including its isolates.

Run after structural_analysis.py. The low-opacity edges show the overall
structure; this is a full-network overview, not the signed directed graph.
"""

from pathlib import Path
import hashlib

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "outputs/structure/full_positive_network.png"
SHA = "6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373"
COLORS = ("#D99A36", "#49D6C5", "#F26B7E", "#6D9DD3", "#B997D3")


def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA:
        raise ValueError("Unexpected SNAP source checksum")
    ratings = pd.read_csv(SOURCE, header=None, names=["source", "target", "rating", "time"])
    graph = nx.Graph()
    graph.add_nodes_from(sorted(set(ratings.source) | set(ratings.target)))
    graph.add_edges_from(ratings.loc[ratings.rating > 0, ["source", "target"]]
                         .itertuples(index=False, name=None))
    # Degree-ranked shells keep the complete graph legible without hiding
    # isolates or requiring an extra layout package. Position within a shell
    # is a drawing choice, not geography or time.
    ranked = sorted(graph, key=lambda v: (-graph.degree(v), v))
    breaks = [59, 294, 1176, 2940]
    shells = [ranked[:breaks[0]]]
    shells += [ranked[a:b] for a, b in zip(breaks[:-1], breaks[1:])]
    shells.append(ranked[breaks[-1]:])
    positions = nx.shell_layout(graph, nlist=shells)
    groups = pd.read_csv(ROOT / "outputs/structure/communities.csv")
    largest = (groups.groupby("community").community_size.first()
               .sort_values(ascending=False).head(5).index.tolist())
    community = dict(zip(groups.node, groups.community))
    nodes = list(graph)
    degrees = dict(graph.degree())
    colors = [COLORS[largest.index(community[v])] if community[v] in largest else "#B8C3CC"
              for v in nodes]
    sizes = [2 + 5 * np.log1p(degrees[v]) for v in nodes]
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0D1420")
    ax.set_facecolor("#0D1420")
    nx.draw_networkx_edges(graph, positions, ax=ax, edge_color="#A5B6C0",
                           alpha=0.025, width=0.25)
    nx.draw_networkx_nodes(graph, positions, nodelist=nodes, node_size=sizes,
                           node_color=colors, alpha=0.85, linewidths=0, ax=ax)
    ax.set_axis_off()
    ax.set_title("All 5,881 users and 18,591 positive projected links", color="white", fontsize=18, pad=12)
    fig.text(0.5, 0.03, "Color: five largest Louvain groups; gray: other groups. Size: projected degree.\n"
             "Degree-ranked shell layout; direction, sign, and rating strength are omitted.",
             color="#C7D6DE", fontsize=11, ha="center")
    fig.savefig(OUT, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"Rendered {len(nodes)} nodes and {graph.number_of_edges()} links to {OUT}")


if __name__ == "__main__":
    main()
