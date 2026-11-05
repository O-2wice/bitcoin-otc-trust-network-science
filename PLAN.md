# Project plan: evolution of the Bitcoin OTC trust network

## Scope and research question

**Main question:** How did positive ratings become concentrated among Bitcoin OTC users, and how sensitive is the apparent advantage of already highly rated users to the comparison benchmark?

**Focused phenomenon (brief part D):** temporal accumulation of incoming positive ratings. This is a team working choice based on the dataset's timestamps, not a compulsory topic in the brief. A separate node-removal experiment probes connectivity sensitivity.

**Unit of observation:** a timestamped directed rating from source to target. Primary graph: positive ratings (`rating > 0`); retain negative ratings for the source audit and signed Cytoscape visualization. Directed in-degree is the number of distinct positive raters a user received. Rating magnitude is a separate attribute, not silently converted to edge multiplicity.

## Analysis sequence

1. **Audit the source.** Record checksum, row counts, node counts, date range, unique pairs, missing values, self-ratings, positive/negative balance, and yearly activity. Check the SNAP documentation. Avoid interpreting a rating as a transaction or proven trustworthiness.
2. **Define graphs.** Build the full directed signed graph, the primary positive directed graph, and a clearly labelled undirected network of positive ratings only where a method requires it. State whether negative-only users remain as isolates.
3. **Describe structure.** Degree distributions and mean degree; density; clustering; component sizes; shortest paths and diameter on a specified component; selected centralities; detected communities. Explain each choice of network representation and the consequences of disconnectedness.
4. **Compare models.** Match ER on users and links, use BA's nearest integer link parameter and state its 5.15% link mismatch, then rewire while preserving each degree in the undirected network. Repeat with fixed seeds and report variation. Explain that retaining accounts isolated by positive filtering affects component comparisons.
5. **Investigate one focused phenomenon.** Compare cumulative rating history, annual-only ratings, and a fixed 2011 cohort. The cumulative top 1% share rises, while annual concentration falls after 2013. Compare event-level recipient choices under uniform and observed-tenure/recent-activity-matched benchmarks. These are descriptive comparisons.
6. **Sensitivity and intervention.** Repeat concentration using ratings of at least +5. Compare random removal with removal of highest original-degree users. Interpret communities using their internal and boundary links; distinguish the 308 singleton groups from 33 non-singleton groups.
7. **Visuals.** Draw the full undirected network of positive ratings using a fixed-seed spring layout with disconnected pieces and isolates explicitly separated. Use the Cytoscape signed spotlight and embedded timeline to illustrate selected users, alongside whole-network numerical results.
8. **Write and defend.** Fill the LaTeX report from verified outputs, cite dataset and methods, prepare a 10--15 minute presentation, and practise explaining definitions, choices, results, and limitations.

## Assignment mapping

| Requirement | Planned evidence |
| --- | --- |
| A: construction and processing | Source audit, graph definitions, cleaning log, full-network overview, Cytoscape subnetwork figure |
| B: structure and communities | Metrics table, distribution figures, component-aware path metrics, community analysis |
| C: two models/concepts | ER and BA comparisons, degree-preserving randomization, repeated seeds and limitations |
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
