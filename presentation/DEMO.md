# Presentation and code demonstration

The 13 main slides are designed for about 12–15 minutes, followed by a short live code demonstration. Slide 14 holds references for questions. Team members should divide the slides only after each person can explain every method and limitation.

| Slides | Topic | Time |
| --- | --- | ---: |
| 1–2 | Question, system, and source | 1.5 min |
| 3 | Directed signed graph and undirected projection | 1.5 min |
| 4 | ER, BA, and degree-preserving comparisons | 2 min |
| 5 | Full positive network overview | 0.5 min |
| 6 | Styled Cytoscape view, short timeline video, and selection bias | 1 min |
| 7–9 | Temporal concentration, uniform benchmark, and matched benchmark | 3 min |
| 10 | Changing clustering, reciprocity, and connectivity | 1 min |
| 11 | Interpretation and limits | 1 min |
| 12 | Random and targeted node removal | 1 min |
| 13 | Conclusion and demo transition | 0.5 min |
| 14 | Sources and reproduction (backup) | For questions |

## Live demo

1. Open `notebooks/01_network_concepts_and_data.ipynb` and show the source checksum, row count, and graph definition.
2. Open `notebooks/02_structure_and_models.ipynb` and explain why the ER/BA comparison uses an undirected projection and why the BA edge count differs.
3. Open `notebooks/03_temporal_rating_accumulation.ipynb` and show the prior-degree target-choice table.
4. Open `notebooks/04_flagship_checks.ipynb`. Explain why the 32+ ratio falls from 12.70 to 1.65 after matching by observed tenure and recent rating activity. Show why rewiring with fixed degrees is a stronger clustering comparison than ER alone, then show the cumulative structural evolution figure.
5. Show `outputs/robustness/node_removal.png` and explain why removing prominent users splits the projected graph more than removing randomly selected users. Run `python scripts/node_removal.py` if asked to demonstrate the intervention.
6. Play `outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4`. Explain that it follows a fixed set of prominent users chosen using the full data; the edges appear by recorded year, so it is an illustrative timeline rather than a whole-network evolution estimate.
7. If asked to change code, change `MODEL_REPLICATES` or `SEED` in `scripts/structural_analysis.py`, or the positive-rating threshold in `scripts/temporal_analysis.py`, rerun, and explain which results changed and why. Restore the committed version afterward.

Prepare the local SNAP data file and Python environment before the presentation. The dataset and Cytoscape GraphML are generated locally from the source link in the README.
