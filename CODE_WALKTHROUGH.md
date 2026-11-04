# Explain the code in plain language

Start with one rule: a row `6,2,4,time` means **user 6 gave user 2 a positive rating of 4**. The graph has a user at each end and an arrow from 6 to 2. The code does not treat that row as a verified trade.

## The five main scripts

| Script | Question | What it does | Main output |
| --- | --- | --- | --- |
| `scripts/structural_analysis.py` | What does the network look like? | Keeps positive ratings, counts links and communities, measures paths, then builds ER and BA comparison graphs. | `outputs/structure/network_metrics.csv` and figures |
| `scripts/temporal_analysis.py` | How did recorded ratings build up? | Takes cumulative year-end snapshots, measures how concentrated incoming ratings became, and compares each later target with a simple equal-chance benchmark. | `outputs/temporal/annual_snapshots.csv` and target-choice tables |
| `scripts/node_removal.py` | What if some users disappear from the graph? | Removes users randomly or in order of their original degree, then measures how many users remain in the largest connected group. | `outputs/robustness/node_removal_summary.csv` and figure |
| `scripts/flagship_checks.py` | Do hubs stand out after accounting for opportunity, and how does structure change? | Compares recipients with others of similar observed tenure and recent activity, rewires links while keeping degrees fixed, and measures three year-end structural properties. | `outputs/flagship/` tables and figures |
| `scripts/verify_reproduction.py` | Do the stored outputs match the headline results? | Checks the source checksum and selected numbers in existing CSVs. It does not rerun the scripts or check output freshness. | A `PASS` message or an error |

`scripts/temporal_sensitivity.py` separates new yearly ratings from accumulated ratings and follows a fixed 2011 cohort. `scripts/community_profiles.py` describes internal and boundary links in the five largest Louvain groups. `scripts/reproduce.py` runs all six numerical analyses in order and records their execution details and output hashes. Use `python scripts/verify_reproduction.py --check-manifest` afterward to check that those recorded files, scripts, and package versions still match.

`scripts/export_cytoscape.py` is a separate visual export. It saves GraphML for Cytoscape; it does not calculate the report's statistics.
`scripts/full_network_force.py` draws the positive projection with a fixed-seed spring layout. It shows the largest component and separates the other small components and isolated users so they remain visible. The saved coordinates make the chosen layout inspectable. Proximity on the page is a layout result; it does not measure geography or time. The earlier `scripts/full_network_overview.py` produces a degree-ranked shell view as an alternative.

## Follow one calculation

```python
positive = ratings[ratings.rating > 0]
```

This keeps rows with favorable scores. A `+4` and a `+9` each make **one** positive link. The directed graph stores `rating`, `weight` (the same original score), and `time_unix`. The main structural results count links rather than adding score values.

```python
incoming = positive.groupby("target").size()
```

This counts how many positive ratings each user **received**. It answers who attracted favorable ratings. Counting by `source` would answer the different question of who **gave** ratings.

For a year-end snapshot, the code keeps ratings recorded by that year, counts incoming ratings for every user seen in the snapshot, and asks what share went to the top 1% of users. Old ratings remain in the cumulative history; the file does not say whether they were still active opinions.

## The hardest part: target-choice benchmark

Before each new positive rating, the code looks at users already seen in earlier positive ratings. It removes the rater and anyone that rater has already rated positively. These are the **eligible targets** for that event. If the actual target has never appeared before, that event is outside this comparison.

The benchmark asks: **if every eligible target had the same chance, how many ratings should go to users with 0, 1, 2–3, ..., or 32+ previous incoming ratings?** The code adds those expected chances over events and divides the actual count by the expected count. A ratio above 1 means that degree group was selected more often than this simple benchmark predicts. The follow-up comparison limits possible recipients to users with similar **observed tenure** and **recent rating activity**. The 32+ ratio falls from 12.70 to 1.65. The file still lacks true account tenure, visibility, and trade data, so neither ratio proves that popularity caused the choice.

## What distance means

The reported shortest-path distance is the number of links, or **hops**. A path of three projected links has distance 3. The code does not turn rating scores into distances, and such a path is not evidence that trust or money traveled between those users.

## A short way to present the workflow

> We downloaded one timestamped rating file and verified its checksum. Each user ID became a node; each rating became a directed, signed edge. For the main analysis we kept positive ratings, and for ER and BA comparisons we made an undirected positive projection. We measured its structure, watched cumulative positive ratings grow by year, and tested how its connectivity changed when users were removed. We fixed random seeds and provide a checker for the headline results.

The [reconstruction guide](REPRODUCIBILITY.md) gives the exact graph rules. To learn the calculations, run the invented examples in notebooks 02–04: build a five-user graph, calculate its measures, list eligible recipients before a rating, and match those recipients by observed tenure and activity. Those teaching examples are separate from the Bitcoin OTC measurements. The notebooks also display the full analysis outputs. Run commands are in the [README](README.md).
