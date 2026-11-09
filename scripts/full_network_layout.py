"""Draw the positive projection with a seeded spring layout and explicit isolates.

Run after structural_analysis.py. Positions are saved so the drawing can be
inspected independently of plotting. Layout distance has no substantive meaning.
"""

from pathlib import Path
import hashlib
import json

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "outputs/structure"
SEED = 2026
ITERATIONS = 30
SHA = "6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373"
COLORS = ("#D99A36", "#49AFA6", "#D96072", "#5288C1", "#9B7DB8")


def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA:
        raise ValueError("Unexpected source checksum")
    ratings = pd.read_csv(SOURCE, header=None, names=["source", "target", "rating", "time"])
    graph = nx.Graph()
    graph.add_nodes_from(sorted(set(ratings.source) | set(ratings.target)))
    positive = ratings[ratings.rating > 0]
    graph.add_edges_from(positive[["source", "target"]].itertuples(index=False, name=None))
    components = sorted(nx.connected_components(graph), key=lambda c: (-len(c), min(c)))
    main_nodes = sorted(components[0])
    main_graph = graph.subgraph(main_nodes)
    print(f"Laying out {len(main_nodes)} nodes in the largest component", flush=True)
    positions = nx.spring_layout(main_graph, seed=SEED, iterations=ITERATIONS,
                                 weight=None, method="energy")
    pd.DataFrame([{"node": v, "x": float(p[0]), "y": float(p[1])}
                  for v, p in positions.items()]).to_csv(OUT / "main_component_spring_positions.csv", index=False)
    groups = pd.read_csv(OUT / "communities.csv")
    sizes = groups.groupby("community").community_size.first().sort_values(ascending=False)
    largest = list(sizes.head(5).index)
    membership = dict(zip(groups.node, groups.community))
    degrees = dict(graph.degree())

    fig, axes = plt.subplots(1, 2, figsize=(12, 7), gridspec_kw={"width_ratios": [4, 1]})
    left, right = axes
    colors = [COLORS[largest.index(membership[v])] if membership[v] in largest else "#AEB8C2"
              for v in main_nodes]
    nx.draw_networkx_edges(main_graph, positions, ax=left, edge_color="#728393",
                           width=0.3, alpha=0.10)
    nx.draw_networkx_nodes(main_graph, positions, ax=left, nodelist=main_nodes,
                           node_color=colors, node_size=[2 + 2.5*np.log1p(degrees[v]) for v in main_nodes],
                           linewidths=0, alpha=0.85)
    left.set_title("Largest positive component: 5,551 users", fontsize=14, loc="left")
    left.set_axis_off()

    # Keep disconnected pieces separate; placing them near the main component
    # would visually imply links which do not exist.
    minor = [c for c in components[1:] if len(c) > 1]
    isolate_nodes = sorted(nx.isolates(graph))
    for index, component in enumerate(minor):
        part = graph.subgraph(sorted(component))
        local = nx.spring_layout(part, seed=SEED, scale=0.07)
        center = np.array([0.25 + 0.5*(index % 2), 0.92 - 0.13*(index // 2)])
        local = {v: point + center for v, point in local.items()}
        positions.update(local)
        nx.draw_networkx(part, local, ax=right, with_labels=False, node_size=12,
                         node_color="#728393", edge_color="#728393", width=0.8)
    for index, node in enumerate(isolate_nodes):
        positions[node] = np.array([0.08 + 0.055*(index % 16), 0.33 - 0.022*(index // 16)])
    nx.draw_networkx_nodes(graph, positions, nodelist=isolate_nodes, ax=right,
                           node_size=4, node_color="#AEB8C2", linewidths=0)
    right.text(0, 1.10, "Other components", fontsize=12, fontweight="bold")
    right.text(0, 1.03, "22 users in 8 groups", fontsize=10)
    right.text(0, 0.42, "308 isolates", fontsize=12, fontweight="bold")
    right.text(0, 0.36, "No incident positive rating", fontsize=9)
    right.set(xlim=(-0.05, 1.05), ylim=(-0.15, 1.2))
    right.set_axis_off()

    handles = [Line2D([0], [0], marker="o", ls="", color=color,
                      label=f"Group {i+1}: {int(sizes[group]):,} users")
               for i, (group, color) in enumerate(zip(largest, COLORS))]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=10,
               frameon=False, bbox_to_anchor=(0.46, 0.035))
    fig.suptitle("Positive-rating network: 5,881 users and 18,591 undirected links",
                 x=0.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(0.05, 0.015, "Color: Louvain group; gray: other groups. Size: degree. Spring positions are a drawing aid, not measured distance.", fontsize=9)
    fig.tight_layout(rect=(0, 0.12, 1, 0.95))
    fig.savefig(OUT / "full_positive_network_layout.png", dpi=180, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    pd.DataFrame([{"node": v, "x": float(positions[v][0]), "y": float(positions[v][1]),
                   "component": 0 if v in components[0] else 1}
                  for v in sorted(graph)]).to_csv(OUT / "full_positive_network_layout_positions.csv", index=False)
    (OUT / "full_positive_network_layout_metadata.json").write_text(json.dumps({
        "seed": SEED, "iterations": ITERATIONS, "layout": "NetworkX spring_layout, energy method",
        "main_component_nodes": len(main_graph), "minor_component_nodes": sum(map(len, minor)),
        "isolates": len(isolate_nodes), "source_sha256": SHA,
        "note": "Disconnected pieces occupy a separate panel with arbitrary panel coordinates."
    }, indent=2) + "\n")
    print("Saved full_positive_network_layout.png", flush=True)


if __name__ == "__main__":
    main()
