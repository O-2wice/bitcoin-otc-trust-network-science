# Cytoscape spotlight and timeline

The report figure is `outputs/cytoscape/bitcoin_otc_spotlight.png`. It is built from an actual Cytoscape 3.10.4 export and a labelled legend. We selected the top 25 users by positive in-degree in the **full dataset**, kept only ratings with absolute score at least 5 among them, then omitted three users isolated by that edge filter. The resulting view has 22 users and 76 directed edges. This selected view is deliberately easier to read; it does not represent the whole network.

To recreate it:

1. Download the original SNAP file as described in the project README and run `python scripts/export_cytoscape.py`.
2. Open Cytoscape and import `outputs/cytoscape/bitcoin_otc_spotlight.graphml` as a network.
3. Load `cytoscape/spotlight_style.json` as a visual style. The dark Bitcoin-inspired theme uses teal for positive edges, coral for negative edges, and amber for users with more positive ratings received. Node size and amber fill both encode positive in-degree in the **full data**; arrows show rating direction. Only the five highest-ranked users have labels.
4. Apply Cytoscape's force-directed layout and export a PNG to `outputs/cytoscape/bitcoin_otc_spotlight_raw.png`. Run `python cytoscape/compose_spotlight.py` to add the legend without redrawing the network. Its crop was set for the original export; inspect the rebuilt image and adjust the crop if the exported canvas or layout changes.

The [short MP4](../outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4) shows when these selected users' strong rating edges were recorded by each year end from 2011 to 2015. The node set and layout are held fixed. Because users were selected using the full period, the video is an illustration of edge timing, **not** an unbiased sample of historical network growth.

CyAnimator 2.2.1 was installed and tested in Cytoscape 3.10.4. It successfully produced 17 recorded frames, but those recorded frames did not preserve the year-specific edge opacity settings. The delivered timeline therefore uses five verified Cytoscape year exports, labelled by `cytoscape/compose_timeline.py` and encoded by `cytoscape/make_timeline_video.py`; it is **not** described as a CyAnimator movie. `cytoscape/record_timeline.py` documents the CyAnimator test and creates the year exports. The frames and live session are kept locally.

To rebuild the timeline, keep Cytoscape running with CyREST available at `http://localhost:1234/v1` and install CyAnimator 2.2.1. The recorder imports the spotlight itself, applies the saved style, lays out the network once, and exports `keyframe_2011.png` through `keyframe_2015.png` into `outputs/cytoscape/animation_frames/`. It also repeats the CyAnimator test; the movie is encoded from the five year exports. Install the external `ffmpeg` executable with H.264 (`libx264`) encoding support; it is not a Python requirement.

From the project root, using the project Python environment:

```bash
python scripts/export_cytoscape.py
python cytoscape/record_timeline.py
python cytoscape/compose_timeline.py
python cytoscape/make_timeline_video.py
```

Inspect all five raw and composed frames before encoding: 5, 16, 54, 73, and 76 edges should be visible respectively, and the node positions should stay fixed. `compose_timeline.py` uses a crop fitted to the original CyREST export; adjust it if a new Cytoscape canvas changes the framing. The layout can differ between Cytoscape runs. To update the separate video backup bundled beside the slides, copy the resulting MP4 to `presentation/bitcoin_otc_spotlight_timeline.mp4`; updating that file alone does not replace the video already embedded inside the PPTX.

The full signed GraphML, spotlight GraphML, and Cytoscape session are kept locally because they include source ratings. The repository tracks the generators, styles, final figure, and MP4.
