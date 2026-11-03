"""Export the original signed network and a documented hub view to GraphML."""

from pathlib import Path
import json

import networkx as nx
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "outputs" / "cytoscape"
HUB_VIEW_NODES = 41


def main():
    ratings = pd.read_csv(
        SOURCE, header=None, names=["source", "target", "rating", "time"]
    )
    nodes = sorted(set(ratings.source) | set(ratings.target))
    positive = ratings[ratings.rating > 0]
    in_degree = positive.groupby("target").size().to_dict()
    out_degree = positive.groupby("source").size().to_dict()
    graph = nx.DiGraph()
    for node in nodes:
        graph.add_node(
            str(node),
            positive_in_degree=int(in_degree.get(node, 0)),
            positive_out_degree=int(out_degree.get(node, 0)),
        )
    for row in ratings.itertuples(index=False):
        graph.add_edge(
            str(row.source), str(row.target),
            rating=int(row.rating),
            sign="positive" if row.rating > 0 else "negative" if row.rating < 0 else "zero",
            time_unix=float(row.time),
        )

    # A deliberate high-reputation view, not a representative random sample.
    # Ties in positive in-degree are broken by ascending numeric user ID.
    ranked = sorted(nodes, key=lambda v: (-in_degree.get(v, 0), v))
    keep = {str(v) for v in ranked[:HUB_VIEW_NODES]}
    hub_view = graph.subgraph(keep).copy()
    OUT.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, OUT / "bitcoin_otc_full_signed_directed.graphml")
    nx.write_graphml(hub_view, OUT / "bitcoin_otc_hub_induced.graphml")
    metadata = {
        "full_graph": {"nodes": len(graph), "edges": graph.number_of_edges()},
        "hub_view": {
            "selection": "top 41 users by positive in-degree, tie-break by ascending numeric user ID; induced signed directed edges",
            "nodes": len(hub_view),
            "edges": hub_view.number_of_edges(),
            "bias": "selected for high received positive ratings; not a representative network sample",
        },
        "node_attributes": ["positive_in_degree", "positive_out_degree"],
        "edge_attributes": ["rating", "sign", "time_unix"],
        "style_suggestion": "map edge sign to color, rating magnitude to width, positive in-degree to node size; label only selected nodes",
    }
    (OUT / "README.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
