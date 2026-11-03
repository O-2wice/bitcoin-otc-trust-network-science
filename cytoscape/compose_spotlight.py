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
    network = image[:600, 175:700]
    fig = plt.figure(figsize=(12, 6.7), facecolor="#0B1423")
    ax = fig.add_axes((0.025, 0.04, 0.48, 0.86))
    ax.imshow(network)
    ax.set_axis_off()
    fig.text(0.54, 0.88, "STRONG RATINGS", color="#F8F4E8", fontsize=24, weight="bold")
    fig.text(0.54, 0.82, "AMONG PROMINENT USERS", color="#F8F4E8", fontsize=18, weight="bold")
    fig.text(0.54, 0.72, "22 users  |  76 directed ratings", color="#D9E8EC", fontsize=15)
    fig.text(0.54, 0.62, "●  Positive rating (+5 to +10)", color="#58DDD0", fontsize=15)
    fig.text(0.54, 0.56, "●  Negative rating (−5 to −10)", color="#FF6B87", fontsize=15)
    fig.text(0.54, 0.45, "Larger node = more positive ratings received", color="#D9E8EC", fontsize=13)
    fig.text(0.54, 0.39, "Arrow = rater → recipient", color="#D9E8EC", fontsize=13)
    fig.text(0.54, 0.24, "Selected from the top 25 recipients in the full data;\n3 have no strong ties within this view.",
             color="#AFC6CE", fontsize=11, linespacing=1.6)
    fig.text(0.54, 0.13, "A focused view, not a sample of all 5,881 users.", color="#AFC6CE", fontsize=11)
    fig.savefig(OUT, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


if __name__ == "__main__":
    main()
