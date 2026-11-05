# The Bitcoin OTC Trust Network: Structure and Rating Patterns

How did positive ratings become concentrated among Bitcoin OTC users, and how sensitive is the apparent advantage of already highly rated users to the comparison benchmark?

The full write-up is the [LaTeX report](overleaf/README.md).

## Data

We study the [SNAP Bitcoin OTC trust network](https://snap.stanford.edu/data/soc-sign-bitcoinotc.html). Each record gives a rater, a rated user, a score from -10 to +10, and a Unix timestamp. The observed data contain 35,592 ratings among 5,881 users from November 2010 to January 2016. Ratings represent users' opinions; they are not verified transactions or fraud outcomes.

Download [`soc-sign-bitcoinotc.csv.gz`](https://snap.stanford.edu/data/soc-sign-bitcoinotc.csv.gz) from SNAP and place it in `data/`. The file is not stored in this repository. The expected SHA-256 is `6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373`.

SNAP asks users of this dataset to cite: S. Kumar, F. Spezzano, V.S. Subrahmanian, C. Faloutsos. *Edge Weight Prediction in Weighted Signed Networks.* IEEE International Conference on Data Mining (ICDM), 2016.

## Approach

Nodes are user accounts. In the **directed network of positive ratings**, an arrow runs from rater to recipient: there are 32,029 such arrows. For the **undirected network**, we ignore arrow direction and combine reciprocal positive ratings into one link, giving 18,591 links. Both retain all 5,881 observed accounts. In-degree counts positive ratings received; out-degree counts positive ratings given.

We define positive ratings as directed edges from rater to recipient, analyse the network's structure and communities, and compare an undirected network with random, Barabási–Albert, and degree-preserving rewired networks. The temporal investigation distinguishes ratings accumulated so far, ratings issued within each year, and a fixed cohort of users. It then compares recipient choices with uniform and tenure/activity-matched benchmarks. Random and targeted node removal provide a separate connectivity experiment. A theory comparison sets the results beside formula predictions, fits the degree tail, estimates an attachment exponent, and tests the Molloy–Reed percolation threshold. [Cytoscape and CyAnimator](cytoscape/README.md) supply a signed network spotlight and an animation connecting five annual snapshots of its recorded ratings.

## Main findings

These are descriptive findings, not evidence of a causal preference or current trust.

- **Structure.** The undirected network is sparse (mean degree 6.32) and hub-dominated (largest degree 788). In the largest component, the diameter is 14 and the exact mean distance is 3.76 hops. Average local clustering is 0.155, about 2.5 times the degree-preserving rewires. Louvain modularity of 0.504 is clearly above the ER, BA, and rewired values (0.33–0.39), though the membership of individual groups changes with the seed.
- **Models.** ER and BA simulations match their own formulas, but neither matches the network. The degree tail fits γ = 2.09 (bootstrap interval 1.91–2.24), yet a pure power law is rejected in favour of lognormal or cut-off tails, so the network is heavy-tailed rather than strictly scale-free. BA's growth rule also fails: 70.5% of links join two existing users. An internal-link extension predicts γ = 2.17 and moves heterogeneity and assortativity toward the data, but it understates the largest hub and community structure.
- **Accumulated ratings.** The top 1% share rises from 15.5% in 2011 to 23.5% in 2015, and also rises within a fixed 2011 cohort.
- **New yearly ratings.** The raw top 1% share falls from 21.0% in 2013 to 11.3% in 2015, but the top group shrinks from 25 users to 4 and ratings fall from 11,138 to 929. With every year redrawn to 743 ratings, the share is 12.1% in 2013 and 10.0% in 2015, with overlapping ranges, and the share of a fixed four recipients rises from 7.8% to 11.6%. Most of the apparent fall is a volume effect.
- **Recipient choice.** Under uniform choice, attachment is close to linear (α = 1.07) and the 32+ prior-rating group has an observed/expected ratio of 12.70. Matching on observed tenure and recent activity gives 1.65 (α = 0.68). Recent activity does most of this: tenure alone raises the ratio to 18.46, while activity alone gives 1.71. Activity includes ratings received, which overlap with prior degree, but counting only ratings given still gives 1.44. About half of eligible events (49.5%) return an earlier rating, with a median delay of 3.7 minutes.
- **Robustness.** The Molloy–Reed threshold is 0.986, and the largest component falls below 1% of users after 93% random removal. Removing the top 15% by degree collapses it. After removing 5% of users, it holds 87.6% of original users under random removal and 45.6% under targeted removal.

## What the findings imply

Reputation is concentrated and stays concentrated: by 2015, 56 accounts held 23.5% of positive ratings. Ratings do not visibly expire in this record and new ratings fell sharply after 2013, so a large accumulated score may increasingly describe past standing. The trust record depends on few accounts, so losing or compromising prominent accounts would disconnect far more of it than the same number of random departures. A rating count is not a count of independent endorsements, since about half of eligible ratings return an earlier one, usually within minutes. Recent participation may also matter more for attracting ratings than an established reputation alone, though the data cannot separate it from unobserved trading volume.

## Limitations and further work

Ratings are opinions, not verified trades or fraud outcomes. The file has no registration dates, exposure, trade volume, or rating changes, and anonymous IDs may not match people one to one. Tenure and activity groups are coarse, and formula values are large-network approximations.

Further work could fit a joint choice model of degree, recency, and reciprocity and test it out of sample; add fitness and aging terms; use time-respecting null models; analyse signed triads with the negative ratings; recompute degree during targeted removal; apply consensus clustering; and link accounts to external fraud labels.

## Guides

The [reconstruction guide](REPRODUCIBILITY.md) traces a source rating through user IDs, filtering, directed edge construction, conversion to an undirected network, and analysis.

The [code walkthrough](CODE_WALKTHROUGH.md) explains each script and the harder target-choice calculation in plain language.

View the [positive-network overview](outputs/structure/full_positive_network_force.png), [annual versus cumulative comparison](outputs/sensitivity/annual_vs_cumulative_concentration.png), [community profiles](outputs/sensitivity/community_link_profiles.png), [Cytoscape spotlight](outputs/cytoscape/bitcoin_otc_spotlight.png), and [rating timeline](outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4). The seeded spring overview separates the main component from smaller pieces and the 308 users isolated by positive filtering. The Cytoscape view and video show a selected set of prominent users; whole-network findings come from the numerical analyses.

## Project structure

```text
data/              Download instructions; the SNAP source file is not stored in Git
overleaf/          LaTeX report source, bibliography, template, and figures
scripts/           Analysis scripts, the seven-script runner, and the checker
notebooks/         Data audit, structure and models, temporal analysis, follow-up checks, theory comparison
outputs/
  structure/       Network metrics, centrality, communities, full-network drawings
  temporal/        Year-end concentration and the uniform target-choice comparison
  flagship/        Matched target choice, degree-preserving rewires, structural evolution
  sensitivity/     Annual-only, equal-volume, fixed-cohort, community-profile, and stability checks
  robustness/      Random and targeted node removal
  theory/          Formula comparisons, tail fits, attachment benchmarks, percolation, exact centrality
  cytoscape/       Spotlight figure, timeline video, and their provenance record
  reproduction/    Run manifest and script logs
cytoscape/         Cytoscape styles and the scripts that build the figure and video
presentation/      Demo guide and backup copy of the timeline video
PLAN.md            Project plan and how it maps to the assignment
REPRODUCIBILITY.md How a source rating becomes a graph, and how to recreate the outputs
CODE_WALKTHROUGH.md Plain-language explanation of each script
AI_DISCLOSURE.md   AI tools used and how their output was checked
```

## Reproduce

Use Python 3.12. Install the packages in `requirements.txt`, download the source file as described above, and run the notebooks in `notebooks/` from the repository root. The current environment was tested with Python 3.12.13; package versions and execution details are recorded in `outputs/reproduction/run_manifest.json`. The [first notebook](notebooks/01_network_concepts_and_data.ipynb) explains the data and graph definitions and performs source checks.

Run `python scripts/reproduce.py` to execute the seven numerical analyses in order (about 25 minutes on a laptop), then `python scripts/verify_reproduction.py --check-manifest` to validate the stored headline values and the recorded script, environment, and output hashes. The manifest check needs exactly Python 3.12.13 and the pinned packages, because it compares them with the recorded run. The manifest covers the current numerical run; the network layout, Cytoscape media, report, and slides have separate build steps.

The [structure notebook](notebooks/02_structure_and_models.ipynb), [temporal notebook](notebooks/03_temporal_rating_accumulation.ipynb), [follow-up checks notebook](notebooks/04_flagship_checks.ipynb), and [theory notebook](notebooks/05_theory_comparison.ipynb) contain small worked calculations as well as the recorded results. Numerical outputs are in `outputs/structure/`, `outputs/temporal/`, `outputs/robustness/`, `outputs/flagship/`, `outputs/sensitivity/`, and `outputs/theory/`. Run `python scripts/full_network_force.py` after the structural script to regenerate the seeded network layout; coordinates and layout parameters are saved alongside its figure. Run `python scripts/export_cytoscape.py` to generate signed, directed GraphML files locally. GraphML files are not distributed in the repository.

The checker validates the source, stored headline results, and optionally the execution manifest; it does not independently establish scientific correctness. The [Cytoscape guide](cytoscape/README.md) describes the manual import, style, and layout steps for the spotlight and movie.

On Linux or macOS, create the notebook environment with:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name bitcoin-otc-network-science --display-name "Python (Bitcoin OTC Network Science)"
.venv/bin/jupyter notebook
```

On Windows, use:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m ipykernel install --prefix .venv --name bitcoin-otc-network-science --display-name "Python (Bitcoin OTC Network Science)"
.venv\Scripts\python -m notebook
```

Starting Jupyter through `python -m` also works where Windows Application Control blocks the `jupyter.exe` launcher.

## Presentation

The [demo guide](presentation/DEMO.md) covers the analysis, code walkthrough, and Cytoscape animation.

The [Overleaf source ZIP](overleaf/bitcoin_otc_report_overleaf.zip) contains the LaTeX report, bibliography, template files, and figures. See the [import instructions](overleaf/README.md).

## Team

Ouko Oyombe ([O-2wice](https://github.com/O-2wice)), Sheillah Khaluvitsi ([shishi177-cpu](https://github.com/shishi177-cpu)), and Abdihakim Yussuf ([Abdak-Yussuf](https://github.com/Abdak-Yussuf)).

## AI-use disclosure

See [AI_DISCLOSURE.md](AI_DISCLOSURE.md) for the required account of assistance and verification.
