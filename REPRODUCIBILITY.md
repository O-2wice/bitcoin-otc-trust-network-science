# How the Bitcoin OTC graph is reconstructed

The source is a file of **rating records**, not publication records. Each row has four fields: `source,target,rating,time`, where the first two fields are user IDs and `time` is a Unix timestamp. Download the original file from [SNAP](https://snap.stanford.edu/data/soc-sign-bitcoinotc.html) as `data/soc-sign-bitcoinotc.csv.gz`. Its expected SHA-256 is `6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373`.

| Stage | Exact rule in this project | Example or check |
| --- | --- | --- |
| 1. Identity resolution | Treat each integer user ID as one node. The dataset contains no names or account metadata, so we do not merge IDs or infer that two IDs belong to the same person. | IDs `6` and `2` are distinct nodes. There are 5,881 IDs appearing as a rater or recipient. |
| 2. Event filtering | Audit missing cells, self-ratings, repeated ordered pairs, sign, and time. No rows are removed for missing values, self-ratings, or duplicates because the source has none. The **full signed graph** uses every rating. The primary **positive graph** keeps only `rating > 0`; a separate sensitivity calculation uses `rating >= 5`. | The source has 35,592 rows: 32,029 positive, 3,563 negative, and zero neutral ratings. |
| 3. Edge construction | Each row creates a directed edge from the rater to the recipient. The positive NetworkX graph keeps the source score as `rating`, the same score as `weight`, and the timestamp as `time_unix`. The reported structural measures count unweighted links. The score is not a count of transactions. | Source row `6,2,4,1289241911.72836` creates `6 → 2` with `rating=4`, `weight=4`, and `time_unix=1289241911.72836`. It contributes one positive incoming edge to user `2`. |
| 4. Graph object | Build a NetworkX `DiGraph` for positive ratings and retain **all 5,881 observed IDs**, including those without positive incident edges. For ER, BA, Louvain, paths, and removal experiments, create a separate simple undirected network of positive ratings: add `{u,v}` if either direction has a positive rating. | The directed positive graph has 32,029 edges; the undirected network has 18,591 links because reciprocal positive pairs collapse. The undirected representation loses direction, score, and sign. |
| 5. Measures and models | Compute positive in/out-degree and approximate betweenness on the directed graph. Compute clustering, components, paths, communities, ER/BA models, and degree-preserving rewires on the undirected network. Use cumulative year-end positive-rating snapshots for growth, concentration, connectivity, transitivity, and reciprocity; compare target choices with uniform and tenure/activity-matched eligible-target benchmarks. The node-removal experiment compares 30 random replicates with removal by original degree in the undirected network. | Scripts in `scripts/` record the definitions and fixed seeds. Output CSVs and figures are in `outputs/`. |

The first row illustrates why direction matters: `6 → 2` means **user 6 rated user 2**, not that they traded, that user 2 rated user 6, or that trust was objectively established. A negative row remains in the signed graph but does not enter the positive graph. A year-end snapshot includes ratings **recorded by** that date; it does not assert that every old rating was still an active relationship.

## Why these weights and distances?

The source, not the researchers, assigns the rating score from -10 to +10. We choose a binary positive-link rule (`rating > 0`) because the main question asks **who received favorable ratings and how the link pattern is organized**. A `+4` and a `+9` each contribute one positive incoming link; their different scores remain available as attributes. The `rating >= 5` calculation checks whether the temporal concentration trend survives a stricter rule.

All reported shortest paths count **hops**, with one undirected positive link equal to distance 1. The sampled mean path length and exact diameter use the largest connected component of the undirected network of positive ratings. Directed betweenness also counts unweighted hops along directed positive-rating edges. ER and BA are unweighted, so this makes their structural comparison consistent with the observed undirected network.

A high rating is a stronger stated opinion, **not** a longer distance. Using `rating` directly as a shortest-path cost would reverse its meaning; using `1/rating` would impose an unvalidated trust-to-distance formula. We therefore do neither. These path measures describe graph topology only: a path of ratings does not establish a real route for trust, information, or trade. Weight-sensitive trust analysis would require a separate research question and a justified transformation of scores.

## Recreate and check the reported outputs

From the repository root, after installing `requirements.txt` into a Python 3.12 environment and downloading the source file:

```bash
python scripts/reproduce.py
python scripts/verify_reproduction.py --check-manifest
```

The first command runs six scripts in order: structural analysis, temporal analysis, node removal, the matched/rewired checks, annual/fixed-cohort sensitivity, and community profiles. It records package versions, the Python version, each script's hash, runtime, log, and generated output hashes in `outputs/reproduction/run_manifest.json`. The requirements describe the environment used for this recorded rerun, including **Python 3.12.13**; they do not establish which package versions were used for earlier runs.

The second command checks the source checksum and headline values **in the stored CSV files**, then checks that the completed manifest matches the current scripts, requirements, installed versions, and listed outputs. It does not execute the analyses. Running the checker alone is not a fresh reproduction. The manifest records one execution and does not establish scientific correctness or independent replication. Without `--check-manifest`, the checker validates only the source checksum and selected stored values.

The scripts use fixed seeds, but image rendering and minor floating-point details may vary across platforms. The numerical runner excludes the full-network layout, Cytoscape media, report, and slides; these have separate build steps. See `cytoscape/README.md` for the additional steps to recreate the Cytoscape view. The LaTeX report is kept outside GitHub for now.

## Learn the calculations before running the full analysis

The notebooks include small, invented teaching examples as well as the measured Bitcoin OTC results. Notebook 02 constructs a graph and calculates degree, density, transitivity, and a path in executable cells. Notebook 03 constructs an eligible recipient set before one rating and calculates its observed/expected ratio. Notebook 04 shows how tenure/activity matching changes that set and verifies that a rewire keeps every node's degree. The examples are labelled separately from source observations; their numbers are not report results.
