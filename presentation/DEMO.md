# Presentation and code demonstration

Nine slides are designed for about 12 minutes, followed by a short live code demonstration. Team members should divide the slides only after each person can explain every method and limitation.

| Slides | Topic | Time |
| --- | --- | ---: |
| 1–2 | Question, system, and source | 1.5 min |
| 3 | Directed signed graph and undirected projection | 1.5 min |
| 4 | ER and BA comparisons | 2 min |
| 5 | Cytoscape view and its selection bias | 1 min |
| 6–7 | Temporal concentration and target-choice benchmark | 3 min |
| 8 | Limitations | 1.5 min |
| 9 | Conclusion and demo transition | 1 min |

## Live demo

1. Open `notebooks/01_network_concepts_and_data.ipynb` and show the source checksum, row count, and graph definition.
2. Open `notebooks/02_structure_and_models.ipynb` and explain why the ER/BA comparison uses an undirected projection and why the BA edge count differs.
3. Open `notebooks/03_temporal_rating_accumulation.ipynb` and show the prior-degree target-choice table.
4. If asked to change code, change `MODEL_REPLICATES` or `SEED` in `scripts/structural_analysis.py`, or the positive-rating threshold in `scripts/temporal_analysis.py`, rerun, and explain which results changed and why. Restore the committed version afterward.

Prepare the local SNAP data file and Python environment before the presentation. The dataset and Cytoscape GraphML are generated locally from the source link in the README.
