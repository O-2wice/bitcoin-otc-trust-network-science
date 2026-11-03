"""Add year labels to verified Cytoscape year-end exports."""

from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "outputs/cytoscape/animation_frames"
COUNTS = {2011: 5, 2012: 16, 2013: 54, 2014: 73, 2015: 76}


def main():
    for year, count in COUNTS.items():
        exported = mpimg.imread(FRAMES / f"keyframe_{year}.png")
        network = exported[:550, 185:670]
        fig = plt.figure(figsize=(12, 6.75), facecolor="#0B1423")
        ax = fig.add_axes((0.025, 0.07, 0.44, 0.85))
        ax.imshow(network)
        ax.set_axis_off()
        fig.text(0.53, 0.85, "BITCOIN OTC", color="#F8F4E8", fontsize=23, weight="bold")
        fig.text(0.53, 0.76, "STRONG RATINGS BY YEAR", color="#F8F4E8", fontsize=18, weight="bold")
        fig.text(0.53, 0.55, str(year), color="#58DDD0", fontsize=70, weight="bold")
        fig.text(0.53, 0.42, f"{count} / 76 edges recorded", color="#D9E8EC", fontsize=22)
        fig.text(0.53, 0.31, "●  positive", color="#58DDD0", fontsize=15)
        fig.text(0.70, 0.31, "●  negative", color="#FF6B87", fontsize=15)
        fig.text(0.53, 0.16,
                 "Fixed users selected using the full 2010–2016 data.\nOnly their ratings recorded by this year are shown.",
                 color="#AFC6CE", fontsize=12, linespacing=1.6)
        fig.savefig(FRAMES / f"composed_{year}.png", dpi=120,
                    facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)


if __name__ == "__main__":
    main()
