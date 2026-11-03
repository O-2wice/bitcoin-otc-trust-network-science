"""Encode the five verified year-end Cytoscape frames as a short MP4."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "outputs/cytoscape/animation_frames"
OUT = ROOT / "outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4"
YEARS = (2011, 2012, 2013, 2014, 2015)


def main():
    playlist = FRAMES / "timeline.txt"
    lines = []
    for year in YEARS:
        frame = FRAMES / f"composed_{year}.png"
        if not frame.exists():
            raise FileNotFoundError(frame)
        lines.extend((f"file '{frame}'", "duration 1.6"))
    lines.append(f"file '{FRAMES / 'composed_2015.png'}'")
    playlist.write_text("\n".join(lines) + "\n")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(playlist), "-vf", "scale=1280:-2,format=yuv420p",
        "-r", "24", "-c:v", "libx264", "-movflags", "+faststart", str(OUT),
    ], check=True)
    print(OUT)


if __name__ == "__main__":
    main()
