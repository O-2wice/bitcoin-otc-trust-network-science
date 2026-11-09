"""Label and encode the frames exported by CyAnimator, without redrawing links."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW_BASE = ROOT / 'outputs/cytoscape/cyanimator_verified'
RAW = RAW_BASE / json.loads((RAW_BASE / 'latest_capture.json').read_text())['directory']
COMPOSED = RAW / 'composed'
MOVIE = ROOT / 'outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4'
COUNTS = [5, 16, 54, 73, 76]
BACKGROUND = '#0D1420'

def main():
    frames = sorted(RAW.glob('Frame_*.png'))
    assert len(frames) == 97, f'Expected 97 CyAnimator frames, found {len(frames)}'
    COMPOSED.mkdir(exist_ok=True)
    # One fixed crop from the union of the first and last frame keeps node
    # positions and magnification unchanged throughout the movie.
    ends = [mpimg.imread(frames[i])[:, :, :3] for i in (0, -1)]
    mask = np.zeros(ends[0].shape[:2], dtype=bool)
    background = np.array([13, 20, 32])/255
    for picture in ends:
        mask |= np.max(np.abs(picture - background), axis=2) > .06
    yy, xx = np.nonzero(mask)
    x0, x1 = max(0, xx.min()-18), min(mask.shape[1], xx.max()+19)
    y0, y1 = max(0, yy.min()-18), min(mask.shape[0], yy.max()+19)
    playlist = []
    for index, path in enumerate(frames):
        key = min(index // 24, 4)
        exact = index % 24 == 0
        year = 2011 + key
        label = str(year) if exact else f'{year} → {year+1}'
        count = f'{COUNTS[key]} / 76 ratings' if exact else f'{COUNTS[key]} → {COUNTS[key+1]} ratings'
        fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BACKGROUND)
        ax = fig.add_axes((.02, .07, .50, .85))
        ax.imshow(mpimg.imread(path)[y0:y1, x0:x1])
        ax.set_axis_off()
        for y, text, color, size, weight in [
            (.88, 'CYANIMATOR / RATINGS BY YEAR END', '#F8F4E8', 17, 'bold'),
            (.68, label, '#49D6C5', 52 if exact else 38, 'bold'),
            (.55, count, '#F8F4E8', 25, 'normal'),
            (.34, 'CyAnimator connects\nfive annual snapshots', '#E9B44C', 19, 'normal'),
            (.18, '22 fixed accounts, chosen using the full record.\nArrows run from rater to recipient.', '#AFC6CE', 15, 'normal')]:
            fig.text(.56, y, text, color=color, fontsize=size, weight=weight, linespacing=1.5)
        # Separate coloured samples keep the sign legend unambiguous.
        fig.text(.56, .44, '● positive', color='#49D6C5', fontsize=17)
        fig.text(.72, .44, '● negative', color='#F26B7E', fontsize=17)
        fig.text(.035, .025,
                 'Fades interpolate annual snapshots; intermediate frames are not additional time observations.',
                 color='#AFC6CE', fontsize=13)
        out = COMPOSED / f'frame_{index:03d}.png'
        fig.savefig(out, dpi=100, facecolor=BACKGROUND)
        if index == 96:
            fig.text(.56, .79, '▶  PLAY TIMELINE', fontsize=16, weight='bold', color='#F8F4E8',
                     bbox={'boxstyle':'round,pad=.55', 'facecolor':'#173946', 'edgecolor':'#49D6C5'})
            poster = ROOT / '.deck_build/timeline_frames/2015.png'
            poster.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(poster, dpi=100, facecolor=BACKGROUND)
        plt.close(fig)
        duration = 1.2 if index == 0 else 1.5 if index == 96 else .7 if exact else 1/24
        # The first interpolated image after each keyframe briefly flashes the
        # final style. Omit those four renderer glitches, keeping the keyframes.
        if index not in (1, 25, 49, 73):
            playlist.extend([f"file '{out}'", f'duration {duration:.8f}'])
    playlist.append(f"file '{COMPOSED / 'frame_096.png'}'")
    listing = COMPOSED / 'playlist.txt'
    listing.write_text('\n'.join(playlist) + '\n')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                    '-i', str(listing), '-vf', 'format=yuv420p', '-r', '24',
                    '-c:v', 'libx264', '-movflags', '+faststart', str(MOVIE)], check=True)
    shutil.copyfile(MOVIE, ROOT / 'presentation/bitcoin_otc_spotlight_timeline.mp4')
    manifest = {
        'source': 'SNAP Bitcoin OTC strong-rating spotlight, 22 accounts and 76 directed ratings',
        'cytoscape_version': '3.10.4', 'cyanimator_version': '2.2.1',
        'keyframe_years': list(range(2011, 2016)), 'keyframe_edge_counts': COUNTS,
        'cyanimator_exported_frames': len(frames), 'interpolated_steps_per_interval': 24,
        'omitted_render_glitch_frames': [1, 25, 49, 73], 'network_frames_used_in_video': 93,
        'network_drawings': 'Actual CyAnimator frame exports; cropping, captions and ffmpeg encoding follow export',
        'frame_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in frames},
        'movie_sha256': hashlib.sha256(MOVIE.read_bytes()).hexdigest(),
        'limit': 'Full-period selected cohort; fades illustrate transitions and are not extra observations.'
    }
    (ROOT / 'outputs/cytoscape/cyanimator_provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(MOVIE)

if __name__ == '__main__':
    main()
