# The Bitcoin OTC Trust Network: Structure and Rating Patterns

How did positive ratings become concentrated among Bitcoin OTC users, and how sensitive is the apparent advantage of already highly rated users to the comparison benchmark?

## Data

We study the [SNAP Bitcoin OTC trust network](https://snap.stanford.edu/data/soc-sign-bitcoinotc.html). Each record gives a rater, a rated user, a score from -10 to +10, and a Unix timestamp. The observed data contain 35,592 ratings among 5,881 users from November 2010 to January 2016. Ratings represent users' opinions; they are not verified transactions or fraud outcomes.

Download `soc-sign-bitcoinotc.csv.gz` from SNAP and place it in `data/`. The expected SHA-256 is `6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373`.

## Approach

Nodes are user accounts. In the **directed network of positive ratings**, an arrow runs from rater to recipient: there are 32,029 such arrows. For the **undirected network**, we ignore arrow direction and combine reciprocal positive ratings into one link, giving 18,591 links. Both retain all 5,881 observed accounts. In-degree counts positive ratings received; out-degree counts positive ratings given.

We define positive ratings as directed edges from rater to recipient, analyse the network's structure and communities, and compare an undirected network with random, Barabási–Albert, and degree-preserving rewired networks. The temporal investigation distinguishes ratings accumulated so far, ratings issued within each year, and a fixed cohort of users. It then compares recipient choices with uniform and tenure/activity-matched benchmarks. Random and targeted node removal provide a separate connectivity experiment. [Cytoscape and CyAnimator](cytoscape/README.md) supply a signed network spotlight and an animation connecting five annual snapshots of its recorded ratings.

Accumulated incoming ratings become more unequal: the top 1% share rises from 15.5% in 2011 to 23.5% in 2015, and also rises within a fixed 2011 cohort. New yearly ratings differ: their top 1% share peaks at 21.0% in 2013 and falls to 11.3% in 2015 as volume declines. The 32+ prior-rating group has an observed/expected ratio of 12.70 under uniform choice, falling to 1.65 after matching by observed tenure and recent activity. These are descriptive findings, not evidence of a causal preference or current trust.

The [reconstruction guide](REPRODUCIBILITY.md) traces a source rating through user IDs, filtering, directed edge construction, conversion to an undirected network, and analysis.

The [code walkthrough](CODE_WALKTHROUGH.md) explains each script and the harder target-choice calculation in plain language.

View the [positive-network overview](outputs/structure/full_positive_network_force.png), [annual versus cumulative comparison](outputs/sensitivity/annual_vs_cumulative_concentration.png), [community profiles](outputs/sensitivity/community_link_profiles.png), [Cytoscape spotlight](outputs/cytoscape/bitcoin_otc_spotlight.png), and [rating timeline](outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4). The seeded spring overview separates the main component from smaller pieces and the 308 users isolated by positive filtering. The Cytoscape view and video show a selected set of prominent users; whole-network findings come from the numerical analyses.

## Reproduce

Use Python 3.12. Install the packages in `requirements.txt`, download the source file as described above, and run the notebooks in `notebooks/` from the repository root. The current environment was tested with Python 3.12.13; package versions and execution details are recorded in `outputs/reproduction/run_manifest.json`. The [first notebook](notebooks/01_network_concepts_and_data.ipynb) explains the data and graph definitions and performs source checks.

Run `python scripts/reproduce.py` to execute the six numerical analyses in order, then `python scripts/verify_reproduction.py --check-manifest` to validate the stored headline values and the recorded script, environment, and output hashes. The manifest covers the current numerical run; the network layout, Cytoscape media, report, and slides have separate build steps.

The [structure notebook](notebooks/02_structure_and_models.ipynb), [temporal notebook](notebooks/03_temporal_rating_accumulation.ipynb), and [follow-up checks notebook](notebooks/04_flagship_checks.ipynb) contain small worked calculations as well as the recorded results. Numerical outputs are in `outputs/structure/`, `outputs/temporal/`, `outputs/robustness/`, `outputs/flagship/`, and `outputs/sensitivity/`. Run `python scripts/full_network_force.py` after the structural script to regenerate the seeded network layout; coordinates and layout parameters are saved alongside its figure. Run `python scripts/export_cytoscape.py` to generate signed, directed GraphML files locally. GraphML files are not distributed in the repository.

The checker validates the source, stored headline results, and optionally the execution manifest; it does not independently establish scientific correctness. The [Cytoscape guide](cytoscape/README.md) describes the manual import, style, and layout steps for the spotlight and movie. The LaTeX report is maintained locally and is not part of this repository yet.

On Linux or macOS, create the notebook environment with:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name bitcoin-otc-network-science --display-name "Python (Bitcoin OTC Network Science)"
.venv/bin/jupyter notebook
```

## Presentation

The [slides](presentation/bitcoin_otc_network_science.pptx) and [demo guide](presentation/DEMO.md) cover the analysis and code walkthrough. Every slide has an 18-point reading script. The [reading notes in Markdown](presentation/SPEAKER_NOTES.md) contain the same script and are easy for the team to edit.

## Team

[O-2wice](https://github.com/O-2wice), [shishi177-cpu](https://github.com/shishi177-cpu), and [Abdak-Yussuf](https://github.com/Abdak-Yussuf).

## AI-use disclosure

See [AI_DISCLOSURE.md](AI_DISCLOSURE.md) for the required account of assistance and verification.
