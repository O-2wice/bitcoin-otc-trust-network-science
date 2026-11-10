# Cytoscape figure and CyAnimator video

The spotlight shows the **25 users with the most positive ratings received** in the full data and the **strong ratings** (score ±5 or more) among them. Three of the 25 have no such rating with the others, so the view has **22 users and 76 directed ratings**. It is chosen to be readable; it is not a representative sample of the 5,881-user network.

| Output | Use |
| --- | --- |
| `outputs/cytoscape/bitcoin_otc_spotlight.png` | Dark figure for slides and the website |
| `outputs/cytoscape/bitcoin_otc_spotlight_light.png` | Light figure for the report (Fig. 3) |
| `outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4` | CyAnimator video, 1920×1080, about 21 s |
| `outputs/cytoscape/bitcoin_otc_spotlight_timeline_poster.png` | Still of the last frame, used as the video poster |
| `outputs/cytoscape/cyanimator_provenance.json` | Keyframes, chosen frames, omitted frames and file hashes |

## How to read it

- **Colour of a line**: teal for a positive rating, coral for a negative one.
- **Width of a line**: rating strength, from ±5 (thin) to ±10 (thick).
- **Arrow**: from the rater to the rated user.
- **Node size**: positive ratings received in the full data. The five users with the most are amber and labelled with their ID.

In the video, each year-end state shows the ratings recorded so far. Ratings that are new in that year are bright and thick, earlier ones are faded, and users stay dim until their first strong rating. The views at 2011, 2012, 2013, 2014 and 2015 show 5, 16, 54, 73 and 76 ratings; the last state shows all of them in the normal style. Users were chosen using all years, so the video shows when their ratings appeared, not how the whole network grew. The frames between year ends are CyAnimator interpolation, not extra observations.

## Rebuild

You need Cytoscape 3.10 with the CyAnimator 2.2.1 app and the `ffmpeg` program (with H.264 support). From the project folder, using the project Python environment:

```bash
python scripts/export_cytoscape.py          # writes the GraphML files (kept local)
# start Cytoscape and wait until it has finished loading
python cytoscape/capture_in_cytoscape.py    # Cytoscape draws the stills and records the animation
python cytoscape/compose_outputs.py         # adds legends, picks clean frames, writes the video
```

`capture_in_cytoscape.py` places the users with a Kamada–Kawai layout (no randomness), so every run has the same positions, and saves its raw exports in `outputs/cytoscape/captures/` (not tracked). **Restart Cytoscape before each run**: CyAnimator keeps the keyframes of earlier captures and has no command to clear them.

CyAnimator occasionally mis-renders single frames, most often the first frame after a keyframe. The capture script therefore records the animation three times. `compose_outputs.py` keeps, for each frame, the recording closest to the median of the three, and then drops any frame that still differs from both of its neighbours while the neighbours agree with each other. The omitted frames are listed in the provenance file; the keyframes are always kept.

`spotlight_style.json` (dark) and `spotlight_style_light.json` are the Cytoscape styles of the complete view, for opening the GraphML file by hand.
