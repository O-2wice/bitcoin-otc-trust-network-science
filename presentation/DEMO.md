# Presentation and code demonstration

The talk uses 15 slides in about 13 minutes, followed by a 2-minute code demonstration, inside the 15-minute limit. Slide 16 lists sources for questions. Every team member should be able to explain the methods, the results and their limits.

The speaker script for each slide is in the PowerPoint notes (18-point text) and in `presentation/SPEAKER_NOTES.md`. Both files stay local with the slides.

| Slides | Topic | Time |
| --- | --- | ---: |
| 1–3 | Question, data, and how a rating becomes a link | 2 min |
| 4–5 | Basic statistics and communities | 1.75 min |
| 6–8 | ER, BA and rewired networks; heavy tail; degree correlations | 2.75 min |
| 9 | CyAnimator video | 0.75 min |
| 10–12 | Concentration over time; who receives the next rating; the fair comparison | 3.5 min |
| 13 | Robustness: random failures and targeted attacks | 0.75 min |
| 14–15 | Checks, limits and findings | 1.5 min |
| 16 | Sources and reproduction (backup) | For questions |

## The video (slide 9)

In slideshow mode, click the video to play it. It runs for about 21 seconds: one state per year end from 2011 to 2015 (5, 16, 54, 73 and 76 strong ratings), then all ratings together. New ratings in a year are bright, earlier ones fade, and users light up with their first strong rating. The users were chosen using all years, so the video shows when their ratings appeared, not how the whole network grew. If the presentation app cannot play the embedded movie, open `presentation/bitcoin_otc_spotlight_timeline.mp4` instead. Test playback on the presentation computer beforehand.

## Live demo

Prepare these in advance, with the data file in `data/` and the project environment active:

1. `notebooks/01_network_concepts_and_data.ipynb`: show one rating record and how it becomes a directed link.
2. `notebooks/02_structure_and_models.ipynb`: run the five-user example that computes degree, density and transitivity by hand and compares them with NetworkX.
3. `notebooks/03_temporal_rating_accumulation.ipynb`: run the worked example that builds the candidate set before one rating and gives the observed/expected ratio of 3.
4. Run `python scripts/verify_reproduction.py --check-manifest`. It checks the data file, the stored headline results and the recorded run; it does not rerun the analyses.

For questions, notebook 04 compares recipients with users of similar tenure and activity (12.70 falls to 1.65), notebook 05 works through the course formulas, the tail fit, the internal-link exponent and the critical threshold, and notebook 06 explains the degree correlations.

If asked to change code, use a temporary copy or branch. For example, change `MODEL_REPLICATES` or `SEED` in `scripts/structural_analysis.py`, rerun it, and explain which results change and why. A changed script or output invalidates the stored manifest until the full runner is rerun.
