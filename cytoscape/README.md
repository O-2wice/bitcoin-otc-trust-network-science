# Cytoscape network figure

The report figure is `outputs/cytoscape/bitcoin_otc_hub_view_cropped.png`. It was exported from Cytoscape 3.10.4. The view contains the 41 users with the highest positive in-degree and all signed directed ratings among them (772 edges). This deliberately emphasizes prominent users; it does not represent the whole network.

To recreate it:

1. Download the original SNAP file as described in the project README and run `python scripts/export_cytoscape.py`.
2. Open Cytoscape and import `outputs/cytoscape/bitcoin_otc_hub_induced.graphml` as a network.
3. Load `cytoscape/style.json` as a visual style. It maps positive edges to blue, negative edges to orange, and positive in-degree to node size. Arrowheads show the rater-to-recipient direction.
4. Apply a deterministic force-directed layout, fit the network to the view, and export a PNG. The delivered image was cropped to remove unused canvas and Cytoscape's overview icon; its network geometry and colors were not altered.

The full signed GraphML and the Cytoscape session are kept locally because they include source ratings. The repository tracks the generator, style, and final figure.
