# Project plan: evolution of the Bitcoin OTC trust network

## Scope and research question

**Main question:** How did positive trust ratings accumulate in the Bitcoin OTC network, and did already highly rated users attract a disproportionate share of new positive ratings?

**Focused phenomenon (brief part D):** temporal network evolution. Hub-targeted robustness is a supporting analysis, contingent on the baseline results.

**Unit of observation:** a timestamped directed rating from source to target. Primary graph: positive ratings (`rating > 0`); retain negative ratings for descriptive and sensitivity analyses. Directed in-degree is the number of distinct positive raters a user received. Rating magnitude is a separate attribute, not silently converted to edge multiplicity.

## Analysis sequence

1. **Audit the source.** Record checksum, row counts, node counts, date range, unique pairs, missing values, self-ratings, positive/negative balance, and yearly activity. Check the SNAP documentation. Avoid interpreting a rating as a transaction or proven trustworthiness.
2. **Define graphs.** Build the full directed signed graph, the primary positive directed graph, and a clearly labelled undirected positive projection only where a method requires it. State whether negative-only users remain as isolates.
3. **Describe structure.** Degree distributions and mean degree; density; clustering; component sizes; shortest paths and diameter on a specified component; selected centralities; detected communities. Explain each projection and the consequences of disconnectedness.
4. **Compare models.** Use a matched Erdos--Renyi baseline and a Barabasi--Albert growth baseline on the positive projection. Match node count and approximate edge count, repeat with fixed seeds, and report variability. Compare degree heterogeneity, clustering, path lengths, and component structure. Model similarity is not evidence of a causal mechanism.
5. **Investigate evolution.** Use cumulative time snapshots and fixed-count event snapshots. Plot node/edge growth, concentration of positive in-degree (e.g., top-1% share and Gini), component size, and newcomer-to-incumbent links. Estimate whether pre-existing in-degree predicts receipt of the next positive rating, while accounting for changing network size and activity. Use a null model that preserves the relevant event sequence constraints. Partial first/last years must be identified.
6. **Sensitivity.** Repeat key findings at different snapshot widths and with alternate positive-edge definitions. Keep uncertainty from random baselines and note observational limits.
7. **Visuals.** Export documented representative subnetworks and a few cumulative snapshots to Cytoscape; use a fixed node set/layout for comparable panels. Generate statistical charts in Python. Preserve source data, generation code, and Cytoscape session/style.
8. **Write and defend.** Fill the LaTeX report from verified outputs, cite dataset and methods, prepare a 10--15 minute presentation, and practise explaining definitions, choices, results, and limitations.

## Assignment mapping

| Requirement | Planned evidence |
| --- | --- |
| A: construction and processing | Source audit, graph definitions, cleaning log, Cytoscape subnetwork figure |
| B: structure and communities | Metrics table, distribution figures, component-aware path metrics, community analysis |
| C: two models/concepts | Matched ER and BA comparisons with repeated seeds and limitations |
| D: one focused investigation | Temporal trust accumulation and hub-attraction analysis beyond simple yearly counts |
| E: critical reflection | Sensitivity, observation limits, finite-size/model limits, real-world interpretation |
| Deliverables | One GitHub repo, 10--15 page PDF report, notebook/code, figures, AI disclosure, presentation/demo |

## Report target (10--15 pages total)

| Section | Working page budget |
| --- | ---: |
| Title, abstract, introduction/question | 1--2 |
| Data, network definition, preprocessing | 2 |
| Methods and reference models | 2--3 |
| Structural results and figures | 2--3 |
| Focused evolution study | 2--3 |
| Discussion, limitations, conclusions, references | 2--3 |

This is a working allocation, not a promise of final pagination; the compiled PDF must be checked.

## Project logistics

- Team GitHub usernames: `O-2wice`, `shishi177-cpu`, and `Abdak-Yussuf` (invitations pending acceptance).
- Instructor GitHub username from brief: `sziklaye`.
- GitHub repository: [O-2wice/bitcoin-otc-trust-network-science](https://github.com/O-2wice/bitcoin-otc-trust-network-science), public as requested. Invitations sent to both teammates and the instructor; verify acceptance later. Keep the LaTeX report local for now, then add the final report to the repository before submission.
- Submission: **2026-11-26 23:59**.
- Presentation: register for **December 3 or 10, 2026**, then prepare 10--15 minutes plus a code demonstration.
- AI disclosure: document assistance and independent checks in the repository.

## Interpretation boundaries

The data show additions of ratings. They do not record link deletion, changes to an existing pair, transactions, fraud outcomes, or all non-rating platform users. A cumulative network is an observed rating history, not necessarily the currently active trust network at that date. Evolution of rating activity must not be confused with causal preferential attachment.
