# Project plan: evolution of the Bitcoin OTC trust network

## Scope and research question

**Main question:** How are Bitcoin OTC trust ratings organized, how well do standard network models reproduce the observed structure, and how did incoming positive ratings become concentrated over time?

**Focused phenomenon (brief part D):** temporal accumulation of incoming positive ratings. This is a team working choice based on the dataset's timestamps, not a compulsory topic in the brief. A separate node-removal experiment probes connectivity sensitivity.

**Unit of observation:** a timestamped directed rating from source to target. Primary graph: positive ratings (`rating > 0`); retain negative ratings for descriptive and sensitivity analyses. Directed in-degree is the number of distinct positive raters a user received. Rating magnitude is a separate attribute, not silently converted to edge multiplicity.

## Analysis sequence

1. **Audit the source.** Record checksum, row counts, node counts, date range, unique pairs, missing values, self-ratings, positive/negative balance, and yearly activity. Check the SNAP documentation. Avoid interpreting a rating as a transaction or proven trustworthiness.
2. **Define graphs.** Build the full directed signed graph, the primary positive directed graph, and a clearly labelled undirected positive projection only where a method requires it. State whether negative-only users remain as isolates.
3. **Describe structure.** Degree distributions and mean degree; density; clustering; component sizes; shortest paths and diameter on a specified component; selected centralities; detected communities. Explain each projection and the consequences of disconnectedness.
4. **Compare models.** Use matched Erdos--Renyi and Barabasi--Albert baselines, then a degree-preserving rewire of the positive projection. Repeat with fixed seeds and report variability. Compare degree heterogeneity, clustering, path lengths, and component structure. Model similarity is not evidence of a causal mechanism.
5. **Investigate one focused phenomenon.** Use year-end cumulative positive-rating snapshots for concentration and network shape. Compare event-level target choices with both uniform eligible-target and observed-tenure/recent-activity-matched benchmarks. Repeat concentration using ratings at least +5. Interpret this as observed rating accumulation, not causal preferential attachment.
6. **Sensitivity and intervention.** Repeat concentration with the +5 positive-edge definition. Compare random node removal with removal of the highest-degree users on the positive projection. Keep variation from random baselines and note observational limits.
7. **Visuals.** Export a documented high-in-degree induced subnetwork to Cytoscape. Generate statistical charts in Python. Preserve source data, generation code, and Cytoscape session/style locally.
8. **Write and defend.** Fill the LaTeX report from verified outputs, cite dataset and methods, prepare a 10--15 minute presentation, and practise explaining definitions, choices, results, and limitations.

## Assignment mapping

| Requirement | Planned evidence |
| --- | --- |
| A: construction and processing | Source audit, graph definitions, cleaning log, Cytoscape subnetwork figure |
| B: structure and communities | Metrics table, distribution figures, component-aware path metrics, community analysis |
| C: two models/concepts | Matched ER and BA comparisons with repeated seeds and limitations |
| D: one focused investigation | Temporal rating concentration and event-level target-choice comparison |
| E: critical reflection | Sensitivity, observation limits, finite-size/model limits, real-world interpretation |
| Deliverables | One GitHub repo, 10--15 page PDF report, notebook/code, figures, AI disclosure, presentation/demo |

## Report target (10--15 pages total)

| Section | Working page budget |
| --- | ---: |
| Title, abstract, introduction/question | 1--2 |
| Data, network definition, preprocessing | 2 |
| Methods and reference models | 2--3 |
| Structural results and figures | 2--3 |
| Focused phenomenon study | 2--3 |
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
