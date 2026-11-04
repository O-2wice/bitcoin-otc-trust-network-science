# Presentation and code demonstration

The 14 main slides are designed for about 11–13 minutes, followed by a short live code demonstration. Slide 15 holds references for questions. Every team member should be ready to explain the methods and limitations.

Each slide has speaker notes with a reading script. Open the Notes pane in PowerPoint or Impress, or use Presenter View during the slideshow, to read them while presenting.

| Slides | Topic | Time |
| --- | --- | ---: |
| 1–2 | Question, system, and source | 1 min |
| 3–4 | Nodes, edges, projections, and class measures | 2 min |
| 5 | ER, BA, and clustering | 1 min |
| 6–7 | Full network and embedded Cytoscape timeline | 1.5 min |
| 8 | Random and targeted node removal | 1 min |
| 9–11 | Concentration, uniform benchmark, and matching | 3 min |
| 12–13 | Changing shape, sensitivity, and limits | 1.5 min |
| 14 | Conclusion and demo transition | 0.5 min |
| 15 | Sources and reproduction (backup) | For questions |

## Live demo

1. Open `notebooks/01_network_concepts_and_data.ipynb` and show the source checksum, row count, and graph definition.
2. Open `notebooks/02_structure_and_models.ipynb` and explain why the ER/BA comparison uses an undirected projection and why the BA edge count differs.
3. Open `notebooks/03_temporal_rating_accumulation.ipynb` and show the prior-degree target-choice table.
4. Open `notebooks/04_flagship_checks.ipynb`. Explain why the 32+ ratio falls from 12.70 to 1.65 after matching by observed tenure and recent rating activity. Show why rewiring with fixed degrees is a stronger clustering comparison than ER alone, then show the cumulative structural evolution figure. Run `python scripts/verify_reproduction.py` to check the source and recorded outputs; the full rewiring analysis need not be rerun live.
5. Show `outputs/robustness/node_removal.png` and explain why removing prominent users splits the projected graph more than removing randomly selected users. Run `python scripts/node_removal.py` if asked to demonstrate the intervention.
6. Slide 7 contains the timeline video. In slideshow mode, select it to play. It follows prominent users chosen using the full data; the edges appear by recorded year, so it is an illustrative timeline rather than a whole-network evolution estimate. The separate `presentation/bitcoin_otc_spotlight_timeline.mp4` is a backup if a presentation app cannot play the embedded video.
7. If asked to change code, change `MODEL_REPLICATES` or `SEED` in `scripts/structural_analysis.py`, or the positive-rating threshold in `scripts/temporal_analysis.py`, rerun, and explain which results changed and why. Restore the committed version afterward.

Prepare the local SNAP data file and Python environment before the presentation. The dataset and Cytoscape GraphML are generated locally from the source link in the README.
