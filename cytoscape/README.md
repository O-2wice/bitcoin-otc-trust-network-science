# Cytoscape spotlight and timeline

The report figure is `outputs/cytoscape/bitcoin_otc_spotlight.png`. It is built from an actual Cytoscape 3.10.4 export and a labelled legend. We selected the top 25 users by positive in-degree in the **full dataset**, kept only ratings with absolute score at least 5 among them, then omitted three users isolated by that edge filter. The resulting view has 22 users and 76 directed edges. This selected view is deliberately easier to read; it does not represent the whole network.

To recreate it:

1. Download the original SNAP file as described in the project README and run `python scripts/export_cytoscape.py`.
2. Open Cytoscape and import `outputs/cytoscape/bitcoin_otc_spotlight.graphml` as a network.
3. Load `cytoscape/spotlight_style.json` as a visual style. It uses teal for positive edges, pink for negative edges, arrowheads for direction, and node size for positive in-degree in the **full data**. Only the five highest-ranked users have labels.
4. Apply Cytoscape's force-directed layout and export a PNG. `cytoscape/compose_spotlight.py` removes empty canvas and adds the legend without redrawing the network.

The [short MP4](../outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4) shows when these selected users' strong rating edges were recorded by each year end from 2011 to 2015. The node set and layout are held fixed. Because users were selected using the full period, the video is an illustration of edge timing, **not** an unbiased sample of historical network growth.

CyAnimator 2.2.1 was installed and tested in Cytoscape 3.10.4. It successfully produced 17 recorded frames, but those recorded frames did not preserve the year-specific edge opacity settings. The delivered timeline therefore uses five verified Cytoscape year exports, labelled by `cytoscape/compose_timeline.py` and encoded by `cytoscape/make_timeline_video.py`; it is **not** described as a CyAnimator movie. `cytoscape/record_timeline.py` documents the CyAnimator test and creates the year exports. The frames and live session are kept locally.

The full signed GraphML, spotlight GraphML, and Cytoscape session are kept locally because they include source ratings. The repository tracks the generators, styles, final figure, and MP4.
