"""Export the original signed network and a documented hub view to GraphML."""

from pathlib import Path
import json

import networkx as nx
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "soc-sign-bitcoinotc.csv.gz"
OUT = ROOT / "outputs" / "cytoscape"
HUB_VIEW_NODES = 41
SPOTLIGHT_NODES = 25
SPOTLIGHT_MIN_ABS_RATING = 5


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
    # A readable companion view: top 25 recipients and only strong opinions.
    spotlight_ids = {str(v) for v in ranked[:SPOTLIGHT_NODES]}
    spotlight = nx.DiGraph()
    for node in spotlight_ids:
        spotlight.add_node(node, **graph.nodes[node],
                           display_label=node if node in {str(v) for v in ranked[:5]} else "")
    for source, target, attrs in graph.edges(data=True):
        if source in spotlight_ids and target in spotlight_ids and abs(attrs["rating"]) >= SPOTLIGHT_MIN_ABS_RATING:
            spotlight.add_edge(source, target, **attrs,
                               year=int(pd.to_datetime(attrs["time_unix"], unit="s", utc=True).year))
    spotlight.remove_nodes_from(list(nx.isolates(spotlight)))
    OUT.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, OUT / "bitcoin_otc_full_signed_directed.graphml")
    nx.write_graphml(hub_view, OUT / "bitcoin_otc_hub_induced.graphml")
    nx.write_graphml(spotlight, OUT / "bitcoin_otc_spotlight.graphml")
    metadata = {
        "full_graph": {"nodes": len(graph), "edges": graph.number_of_edges()},
        "hub_view": {
            "selection": "top 41 users by positive in-degree, tie-break by ascending numeric user ID; induced signed directed edges",
            "nodes": len(hub_view),
            "edges": hub_view.number_of_edges(),
            "bias": "selected for high received positive ratings; not a representative network sample",
        },
        "spotlight_view": {
            "selection": "top 25 users by full-data positive in-degree, tie-break by ascending user ID; edges among them with absolute rating at least 5; hide users isolated by this edge filter",
            "nodes": len(spotlight),
            "edges": spotlight.number_of_edges(),
            "bias": "selected using full-data degree and strong ratings; not representative or a historical cohort",
        },
        "node_attributes": ["positive_in_degree", "positive_out_degree"],
        "edge_attributes": ["rating", "sign", "time_unix"],
        "style_suggestion": "map edge sign to color, rating magnitude to width, positive in-degree to node size; label only selected nodes",
    }
    (OUT / "export_summary.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
