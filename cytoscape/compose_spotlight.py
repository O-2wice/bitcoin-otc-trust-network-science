"""Place the Cytoscape export beside a readable legend; do not redraw edges."""

from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "outputs/cytoscape/bitcoin_otc_spotlight_raw.png"
OUT = ROOT / "outputs/cytoscape/bitcoin_otc_spotlight.png"


def main():
    image = mpimg.imread(RAW)
    # The CyREST export includes empty canvas and Cytoscape overlay icons to
    # the right. This crop keeps the entire network drawn by Cytoscape.
    network = image[:525, :425]
    fig = plt.figure(figsize=(12, 6.7), facecolor="#0D1420")
    ax = fig.add_axes((0.035, 0.08, 0.43, 0.80))
    ax.imshow(network)
    ax.set_axis_off()
    fig.text(0.53, 0.89, "BITCOIN OTC  /  TRUST RATINGS", color="#E9B44C", fontsize=13, weight="bold")
    fig.text(0.53, 0.81, "Strong ratings among", color="#F8F4E8", fontsize=23, weight="bold")
    fig.text(0.53, 0.75, "prominent users", color="#F8F4E8", fontsize=23, weight="bold")
    fig.text(0.53, 0.65, "22 users  |  76 directed ratings", color="#D9E8EC", fontsize=14)
    fig.text(0.53, 0.56, "●  Positive rating (+5 to +10)", color="#49D6C5", fontsize=14)
    fig.text(0.53, 0.50, "●  Negative rating (−5 to −10)", color="#F26B7E", fontsize=14)
    fig.text(0.53, 0.40, "Gold and larger nodes = more positive ratings received", color="#E9B44C", fontsize=11.5)
    fig.text(0.53, 0.34, "Arrow = rater → recipient", color="#D9E8EC", fontsize=12)
    fig.text(0.53, 0.22, "Selected from the top 25 recipients in the full data;\n3 have no strong ties within this view.",
             color="#AFC6CE", fontsize=11, linespacing=1.6)
    fig.text(0.53, 0.11, "A focused view of the 5,881-user network.", color="#AFC6CE", fontsize=11)
    fig.savefig(OUT, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


if __name__ == "__main__":
    main()
