# The Bitcoin OTC Trust Network: Structure and Rating Patterns

How are positive and negative trust ratings organized among Bitcoin OTC users, and how well do standard network models explain the observed structure?

## Data

We study the [SNAP Bitcoin OTC trust network](https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html). Each record gives a rater, a rated user, a score from -10 to +10, and a Unix timestamp. The observed data contain 35,592 ratings among 5,881 users from November 2010 to January 2016. Ratings represent users' opinions; they are not verified transactions or fraud outcomes.

Download `soc-sign-bitcoinotc.csv.gz` from SNAP and place it in `data/`. The expected SHA-256 is `6424ac981dad3a019f697fc1b9fcd85c19d8d9f039797758e9ffb6fea100c373`.

## Approach

We define positive ratings as directed edges from rater to rated user, analyse the network's structure and communities, and compare its undirected positive projection with matched random and Barabási–Albert networks. The deeper phenomenon is still to be selected. We will use Cytoscape for selected network figures and Python for reproducible measurements and plots. Methods and assumptions are detailed in [PLAN.md](PLAN.md).

## Reproduce

Use Python 3.12. Install the packages in `requirements.txt`, download the source file as described above, and run the notebooks in `notebooks/` from the repository root. The [first notebook](notebooks/01_network_concepts_and_data.ipynb) explains the data and graph definitions and performs source checks.

Run the structural analysis with `python scripts/structural_analysis.py`, then open [the structure and model notebook](notebooks/02_structure_and_models.ipynb). The generated tables and figure are in `outputs/structure/`.

On Linux or macOS, create the notebook environment with:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name bitcoin-otc-network-science --display-name "Python (Bitcoin OTC Network Science)"
.venv/bin/jupyter notebook
```

## Team

[O-2wice](https://github.com/O-2wice), [shishi177-cpu](https://github.com/shishi177-cpu), and [Abdak-Yussuf](https://github.com/Abdak-Yussuf).

## AI-use disclosure

See [AI_DISCLOSURE.md](AI_DISCLOSURE.md) for the required account of assistance and verification.
