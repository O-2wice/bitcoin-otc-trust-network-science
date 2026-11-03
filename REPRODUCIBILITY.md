# How the Bitcoin OTC graph is reconstructed

The source is a file of **rating records**, not publication records. Each row has four fields: `source,target,rating,time`, where the first two fields are user IDs and `time` is a Unix timestamp. Download the original file from [SNAP](https://snap.stanford.edu/data/soc-sign-bitcoinotc.html) as `data/soc-sign-bitcoinotc.csv.gz`. Its expected SHA-256 is `6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373`.

| Stage | Exact rule in this project | Example or check |
| --- | --- | --- |
| 1. Identity resolution | Treat each integer user ID as one node. The dataset contains no names or account metadata, so we do not merge IDs or infer that two IDs belong to the same person. | IDs `6` and `2` are distinct nodes. There are 5,881 IDs appearing as a rater or recipient. |
| 2. Event filtering | Audit missing cells, self-ratings, repeated ordered pairs, sign, and time. No rows are removed for missing values, self-ratings, or duplicates because the source has none. The **full signed graph** uses every rating. The primary **positive graph** keeps only `rating > 0`; a separate sensitivity calculation uses `rating >= 5`. | The source has 35,592 rows: 32,029 positive, 3,563 negative, and zero neutral ratings. |
| 3. Edge construction | Each row creates a directed edge from the rater to the recipient. Keep score and timestamp as edge attributes. Rating magnitude is a weight, not a count of repeated edges or transactions. | Source row `6,2,4,1289241911.72836` creates `6 → 2` with rating `+4` at that Unix time. It contributes one positive incoming edge to user `2`. |
| 4. Graph object | Build a NetworkX `DiGraph` for positive ratings and retain **all 5,881 observed IDs**, including those without positive incident edges. For ER, BA, Louvain, paths, and removal experiments, create a separate simple undirected positive projection: add `{u,v}` if either direction has a positive rating. | The directed positive graph has 32,029 edges; the projection has 18,591 links because reciprocal positive pairs collapse. The projection loses direction, score, and sign. |
| 5. Measures and models | Compute positive in/out-degree and approximate betweenness on the directed graph. Compute clustering, components, paths, communities, and ER/BA comparisons on the undirected projection. Use cumulative year-end positive-rating snapshots for growth and concentration; compare target choices with a uniform eligible-target benchmark. The node-removal experiment compares 30 random replicates with removal by original projected degree. | Scripts in `scripts/` record the definitions and fixed seeds. Output CSVs and figures are in `outputs/`. |

The first row illustrates why direction matters: `6 → 2` means **user 6 rated user 2**, not that they traded, that user 2 rated user 6, or that trust was objectively established. A negative row remains in the signed graph but does not enter the positive graph. A year-end snapshot includes ratings **recorded by** that date; it does not assert that every old rating was still an active relationship.

## Recreate and check the reported outputs

From the repository root, after installing `requirements.txt` into a Python 3.12 environment and downloading the source file:

```bash
python scripts/structural_analysis.py
python scripts/temporal_analysis.py
python scripts/node_removal.py
python scripts/verify_reproduction.py
```

The last command checks the source checksum and key reported values. The scripts use fixed seeds, but image rendering and minor floating-point details may vary across platforms. See `cytoscape/README.md` for the additional manual steps to recreate the Cytoscape view. The LaTeX report is kept outside GitHub for now.
