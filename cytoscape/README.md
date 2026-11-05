# Cytoscape spotlight and timeline

The report figure is `outputs/cytoscape/bitcoin_otc_spotlight.png`. It is built from an actual Cytoscape 3.10.4 export and a labelled legend. We selected the top 25 users by positive in-degree in the **full dataset**, kept only ratings with absolute score at least 5 among them, then omitted three users isolated by that edge filter. The resulting view has 22 users and 76 directed edges. This selected view is deliberately easier to read; it does not represent the whole network.

To recreate it:

1. Download the original SNAP file as described in the project README and run `python scripts/export_cytoscape.py`.
2. Open Cytoscape and import `outputs/cytoscape/bitcoin_otc_spotlight.graphml` as a network.
3. Load `cytoscape/spotlight_style.json` as a visual style. The dark Bitcoin-inspired theme uses teal for positive edges, coral for negative edges, and amber for users with more positive ratings received. Node size and amber fill both encode positive in-degree in the **full data**; arrows show rating direction. Only the five highest-ranked users have labels.
4. Apply Cytoscape's force-directed layout and export a PNG to `outputs/cytoscape/bitcoin_otc_spotlight_raw.png`. Run `python cytoscape/compose_spotlight.py` to add the legend without redrawing the network. Its crop was set for the original export; inspect the rebuilt image and adjust the crop if the exported canvas or layout changes.

The [short MP4](../outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4) shows when these selected users' strong rating edges were recorded by each year end from 2011 to 2015. The node set and layout are held fixed. Because users were selected using the full period, the video is an illustration of edge timing, **not** an unbiased sample of historical network growth.

## CyAnimator's role

**Slide 7 contains the actual CyAnimator animation.** It connects five year-end states, making recorded link accumulation visible with account positions fixed. The annual states contain 5, 16, 54, 73, and 76 strong directed ratings. The next slides supply whole-population measurements; this spotlight is selected using the full record.

CyAnimator 2.2.1 in Cytoscape 3.10.4 exported 97 frames. The MP4 uses 93 of those network drawings. The first interpolated frame after each keyframe briefly flashed the final style; those four renderer glitches (indices 1, 25, 49 and 73) were omitted. Cropping, year labels, and encoding follow the app export. [Frame and movie hashes](../outputs/cytoscape/cyanimator_provenance.json) record the provenance. Intermediate frames are visual interpolation, not additional timestamped observations. See [Morris et al. (2015)](https://doi.org/10.12688/f1000research.6852.2) for the method.

To rebuild, keep Cytoscape running with CyREST at `http://localhost:1234/v1` and install CyAnimator 2.2.1. Also install the external `ffmpeg` executable with H.264 (`libx264`) support; it is not a Python requirement. The recorder creates a fresh collection and explicitly selects its current view, avoiding retained frames and capture of another network. Distinct year styles use a text year attribute for edge visibility. The layout is calculated once and then held fixed.

From the project root, using the project Python environment:

```bash
python scripts/export_cytoscape.py
python cytoscape/record_verified_animation.py
python cytoscape/compose_cyanimator_video.py
```

Raw exports stay locally under `outputs/cytoscape/cyanimator_verified/`; `latest_capture.json` identifies the current run. Inspect exported frames 0, 24, 48, 72 and 96, not only the source view images. They should show the stated counts and fixed positions. The composition script uses one fixed crop, labels annual states and transitions, and writes both MP4 copies. Layouts may differ between Cytoscape runs. Replacing an MP4 file does not update the movie already embedded inside an existing PPTX. The earlier `record_timeline.py`, `compose_timeline.py`, and `make_timeline_video.py` document the previous fallback workflow.

The full signed GraphML, spotlight GraphML, and Cytoscape session are kept locally because they include source ratings. The repository tracks the generators, styles, final figure, and MP4.

The working session is saved locally as `outputs/cytoscape/bitcoin_otc_cyanimator_verified.cys`. Its final network is named **Bitcoin OTC - VERIFIED CyAnimator 2011-2015**. Open that session and select that network to inspect its captured frames in CyAnimator.
