# Presentation and code demonstration

Allow about 11–12 minutes for slides 1–14 and 2 minutes for the code demonstration, keeping the whole talk within 15 minutes. Slide 15 holds sources and method details for questions. Every team member should be ready to explain the methods and limitations.

Each slide has speaker notes with a reading script. Open the Notes pane in PowerPoint or Impress, or use Presenter View during the slideshow, to read them while presenting.

| Slides | Topic | Time |
| --- | --- | ---: |
| 1–2 | System and focused research question | 1 min |
| 3–4 | Worked graph construction and full-network overview | 1.5 min |
| 5–6 | ER/BA comparisons and degree-preserving rewiring | 1.5 min |
| 7 | Embedded Cytoscape timeline | 0.5 min |
| 8–9 | Annual versus accumulated ratings; structural evolution | 2 min |
| 10–11 | Uniform recipient choice, matching, and interpretation | 2 min |
| 12 | Random and targeted node removal | 0.75 min |
| 13 | Sensitivity and limits | 0.75 min |
| 14 | Conclusion and demo transition | 0.5 min |
| 15 | Sources and reproduction (backup) | For questions |

## Live demo

For a two-minute demonstration, prepare these cells in advance:

1. In `notebooks/02_structure_and_models.ipynb`, run the five-user teaching example. Identify one directed rating, its contribution to incoming degree, and the link after projection. The invented example is labelled separately from the Bitcoin observations.
2. In `notebooks/03_temporal_rating_accumulation.ipynb`, run the cell that reconstructs the 2015 cumulative and annual-only counts. Explain why the two time windows answer different questions.
3. Run `python scripts/verify_reproduction.py --check-manifest` in the project environment. Explain that this checks source and recorded-output consistency. The six analyses were run by `python scripts/reproduce.py`; the checker itself does not rerun them.

For questions, use notebook 04's executable matched-candidate and degree-preserving-rewire examples. Explain that the 32+ ratio changes from 12.70 under uniform choice to 1.65 after matching by observed tenure and recent rating activity. The matched analysis retains 99.48% of eligible events, so the two ratios use slightly different event sets. Neither establishes a causal preference for well-rated users.

Slide 7 contains the timeline video. In slideshow mode, select it to play. It follows prominent users chosen using the full data; the edges appear by recorded year, so it is an illustrative timeline rather than a whole-network evolution estimate. It was assembled from Cytoscape snapshot exports; it is not a successful CyAnimator export. The separate `presentation/bitcoin_otc_spotlight_timeline.mp4` is a backup if a presentation app cannot play the embedded video. Test playback in the actual presentation app before the talk.

If asked to change code, use a temporary copy or branch. Change `MODEL_REPLICATES` or `SEED` in `scripts/structural_analysis.py`, rerun, and explain which results changed and why. A changed script or output invalidates the stored manifest until the numerical runner is rerun. The full rewiring and removal analyses need not be rerun during the timed demonstration.

Prepare the local SNAP data file and Python environment before the presentation. The dataset and Cytoscape GraphML are generated locally from the source link in the README.
