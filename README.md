# The Bitcoin OTC Trust Network: Structure and Rating Patterns

How are trust ratings organized among Bitcoin OTC users, how well do standard network models reproduce the observed structure, and how did incoming positive ratings become concentrated over time?

## Data

We study the [SNAP Bitcoin OTC trust network](https://snap.stanford.edu/data/soc-sign-bitcoinotc.html). Each record gives a rater, a rated user, a score from -10 to +10, and a Unix timestamp. The observed data contain 35,592 ratings among 5,881 users from November 2010 to January 2016. Ratings represent users' opinions; they are not verified transactions or fraud outcomes.

Download `soc-sign-bitcoinotc.csv.gz` from SNAP and place it in `data/`. The expected SHA-256 is `6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373`.

## Approach

We define positive ratings as directed edges from rater to rated user, analyse the network's structure and communities, and compare its undirected positive projection with matched random and Barabási–Albert networks. We also compare random node removal with removal of the highest-degree users. The focused investigation tests changes in incoming-rating concentration over time and compares later target choices with a uniform eligible-target benchmark. [Cytoscape](cytoscape/README.md) provides a signed, directed subnetwork figure. Methods and assumptions are detailed in [PLAN.md](PLAN.md).

The [reconstruction guide](REPRODUCIBILITY.md) traces a source rating through user IDs, filtering, directed edge construction, graph projection, and analysis.

The [code walkthrough](CODE_WALKTHROUGH.md) explains each script and the harder target-choice calculation in plain language.

## Reproduce

Use Python 3.12. Install the packages in `requirements.txt`, download the source file as described above, and run the notebooks in `notebooks/` from the repository root. The analysis package pins match the versions used for the recorded results. The [first notebook](notebooks/01_network_concepts_and_data.ipynb) explains the data and graph definitions and performs source checks.

Run `python scripts/structural_analysis.py`, `python scripts/temporal_analysis.py`, and `python scripts/node_removal.py`, then open the [structure and model notebook](notebooks/02_structure_and_models.ipynb) and [temporal notebook](notebooks/03_temporal_rating_accumulation.ipynb). Their tables and figures are in `outputs/structure/`, `outputs/temporal/`, and `outputs/robustness/`. Run `python scripts/export_cytoscape.py` to generate signed, directed GraphML files locally; the smaller view deliberately emphasizes highly rated users and is not a random sample. GraphML files are not distributed in the repository.

Run `python scripts/verify_reproduction.py` after the three analysis scripts. It checks the source SHA-256 and headline values against the reported results. The [Cytoscape guide](cytoscape/README.md) describes the manual import, style, and layout steps needed to recreate that figure. The LaTeX report is maintained locally and is not part of this repository yet.

On Linux or macOS, create the notebook environment with:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name bitcoin-otc-network-science --display-name "Python (Bitcoin OTC Network Science)"
.venv/bin/jupyter notebook
```

## Presentation

The [slides](presentation/bitcoin_otc_network_science.pptx) and [demo guide](presentation/DEMO.md) cover the analysis and code walkthrough.

## Team

[O-2wice](https://github.com/O-2wice), [shishi177-cpu](https://github.com/shishi177-cpu), and [Abdak-Yussuf](https://github.com/Abdak-Yussuf).

## AI-use disclosure

See [AI_DISCLOSURE.md](AI_DISCLOSURE.md) for the required account of assistance and verification.
