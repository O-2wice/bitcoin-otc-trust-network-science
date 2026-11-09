"""Turn the Cytoscape exports into the final figures and the CyAnimator video.

Run after capture_in_cytoscape.py; Cytoscape does not need to be open. The network is
never redrawn here: this script crops Cytoscape's own images, chooses clean CyAnimator
frames, adds titles and legends, and encodes the video with ffmpeg.

Writes to outputs/cytoscape/:
  bitcoin_otc_spotlight.png                dark figure (slides and website)
  bitcoin_otc_spotlight_light.png          light figure (report)
  bitcoin_otc_spotlight_timeline.mp4       CyAnimator video, plus a copy in presentation/
  bitcoin_otc_spotlight_timeline_poster.png
  cyanimator_provenance.json
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / 'outputs/cytoscape/captures'
OUT = ROOT / 'outputs/cytoscape'
STEPS = 24
STATES = ['2011', '2012', '2013', '2014', '2015', 'complete']
SHOWN = [5, 16, 54, 73, 76, 76]
NEW = [5, 11, 38, 19, 3]
NEW_NEGATIVE = [0, 0, 5, 6, 0]
HOLD = {0: 2.4, 1: 2.2, 2: 2.8, 3: 2.4, 4: 2.0, 5: 4.0}  # seconds on each keyframe

BG, TEXT, MUTED, FAINT = '#0B1220', '#F1F5F9', '#94A3B8', '#64748B'
AMBER, SLATE, TEAL, TEAL_NEW, CORAL = '#F5B841', '#94A3B8', '#2EC4B6', '#9BFFF2', '#F2617A'
LIGHT = {'bg': '#FFFFFF', 'text': '#111827', 'muted': '#4B5563', 'teal': '#0E9F8E',
         'coral': '#DC4363', 'amber': '#E59E1B', 'slate': '#A3B1C2'}
FOOTER = 'Drawn in Cytoscape 3.10 and animated with CyAnimator 2.2.1  ·  22 of 5,881 users  ·  ratings of ±5 or more'


def font(weight, size, display=False):
    """Inter if it is installed, otherwise DejaVu Sans (bundled with matplotlib)."""
    name = ('InterDisplay-' if display else 'Inter-') + weight + '.otf'
    for folder in ('/usr/share/fonts/opentype/inter', str(Path.home() / '.local/share/fonts'), 'C:/Windows/Fonts'):
        if (Path(folder) / name).exists():
            return ImageFont.truetype(str(Path(folder) / name), size)
    bold = weight in ('Bold', 'SemiBold')
    return ImageFont.truetype(font_manager.findfont(f'DejaVu Sans:{"bold" if bold else "normal"}'), size)


def content_box(images, background, margin):
    """Smallest box holding every non-background pixel of the given images."""
    mask = None
    for image in images:
        pixels = np.asarray(image.convert('RGB'), dtype=float) / 255
        bg = np.array(Image.new('RGB', (1, 1), background).getpixel((0, 0))) / 255
        here = np.abs(pixels - bg).max(axis=2) > 0.04
        mask = here if mask is None else mask | here
    ys, xs = np.nonzero(mask)
    w, h = images[0].size
    return (max(xs.min() - margin, 0), max(ys.min() - margin, 0),
            min(xs.max() + margin, w), min(ys.max() + margin, h))


def paste_fit(canvas, image, box):
    """Scale the image to fit inside box (left, top, right, bottom), centred."""
    left, top, right, bottom = box
    scale = min((right - left) / image.width, (bottom - top) / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    canvas.paste(resized, (left + (right - left - resized.width) // 2, top + (bottom - top - resized.height) // 2))


def spaced(draw, xy, text, fnt, fill, spacing):
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=fnt, fill=fill)
        x += draw.textlength(char, font=fnt) + spacing


def legend_row(draw, x, y, kind, label, fnt, colour_text, colours):
    if kind == 'dot':
        draw.ellipse((x + 6, y + 4, x + 30, y + 28), fill=colours)
    else:
        width, colour = colours
        draw.line((x, y + 16, x + 40, y + 16), fill=colour, width=width)
    draw.text((x + 58, y), label, font=fnt, fill=colour_text)


# ------------------------------------------------------------------ frames

def choose_frames(run):
    """For each frame index, keep the recording closest to the median of all recordings,
    then drop frames that still flash (differ from both neighbours, which agree)."""
    recordings = sorted(p for p in run.glob('recording_*') if p.is_dir())
    names = sorted(p.name for p in recordings[0].glob('Frame_*.png'))
    small = lambda p: np.asarray(Image.open(p).convert('RGB').resize((320, 196)), dtype=float) / 255
    chosen, thumbs = [], []
    for name in names:
        versions = [small(r / name) for r in recordings]
        median = np.median(versions, axis=0)
        best = int(np.argmin([np.abs(v - median).mean() for v in versions]))
        chosen.append(recordings[best] / name)
        thumbs.append(versions[best])

    def diff(a, b):
        return float(np.abs(thumbs[a] - thumbs[b]).mean())

    keyframes = set(range(0, len(names), STEPS))
    dropped = set()
    for i in range(1, len(names) - 1):
        if i in keyframes:
            continue
        before = i - 1
        while before in dropped:
            before -= 1
        spike, base = min(diff(before, i), diff(i, i + 1)), diff(before, i + 1)
        red = ((thumbs[i][..., 0] > .7) & (thumbs[i][..., 1] < .15) & (thumbs[i][..., 2] < .15)).mean()
        if (spike > 3 * max(base, 1e-4) and spike > 0.002) or red > 0.002:
            dropped.add(i)
    return chosen, sorted(dropped), [r.name for r in recordings]


def video_frame(network, index, crop):
    key, step = divmod(index, STEPS)
    progress = key + step / STEPS
    state = min(key + (1 if step >= STEPS // 2 else 0), 5)  # the text switches half-way through a fade

    canvas = Image.new('RGB', (1920, 1080), BG)
    paste_fit(canvas, network.crop(crop), (40, 40, 1190, 1000))
    draw = ImageDraw.Draw(canvas)
    x = 1250
    spaced(draw, (x, 92), 'BITCOIN OTC  ·  WEB OF TRUST', font('SemiBold', 21), AMBER, 2)
    draw.multiline_text((x, 132), 'How strong ratings among the\nmost-rated users built up',
                        font=font('Bold', 38), fill=TEXT, spacing=12)

    if state < 5:
        draw.text((x - 6, 262), STATES[state], font=font('Bold', 150, display=True), fill=TEAL_NEW)
        draw.text((x, 448), f'{SHOWN[state]} of 76 strong ratings', font=font('Medium', 34), fill=TEXT)
        line = f'{NEW[state]} recorded by the end of 2011' if state == 0 else f'+{NEW[state]} new in {STATES[state]}'
        draw.text((x, 500), line, font=font('Medium', 27), fill=TEAL_NEW)
        if NEW_NEGATIVE[state]:
            offset = draw.textlength(line, font=font('Medium', 27))
            draw.text((x + offset, 500), f'  ·  {NEW_NEGATIVE[state]} negative', font=font('Medium', 27), fill=CORAL)
    else:
        draw.text((x - 4, 290), 'All years', font=font('Bold', 112, display=True), fill=TEAL_NEW)
        draw.text((x, 448), '76 strong ratings, 2010–2015', font=font('Medium', 34), fill=TEXT)
        draw.text((x, 500), 'Edge width shows rating strength', font=font('Medium', 27), fill=MUTED)

    # Progress strip, 2011 to 2015
    left, right, y = x + 8, x + 548, 606
    xs = [left + i * (right - left) / 4 for i in range(5)]
    filled = left + min(progress, 4) * (right - left) / 4
    draw.line((left, y, right, y), fill='#273449', width=4)
    draw.line((left, y, filled, y), fill=TEAL, width=4)
    for i, tick in enumerate(xs):
        done = progress >= i - 1e-9
        draw.ellipse((tick - 8, y - 8, tick + 8, y + 8), fill=TEAL_NEW if done else BG,
                     outline=TEAL_NEW if done else '#3B4A63', width=3)
        label = STATES[i]
        current = state == i
        fnt = font('SemiBold' if current else 'Medium', 19)
        draw.text((tick - draw.textlength(label, font=fnt) / 2, y + 18), label, font=fnt,
                  fill=TEXT if current else FAINT)

    small = font('Regular', 24)
    rows = ([('line', 'New in this year', (7, TEAL_NEW)), ('line', 'Recorded earlier', (3, '#1F7F78'))]
            if state < 5 else [('line', 'Positive rating', (5, TEAL))])
    rows += [('line', 'Negative rating', (4, CORAL)), ('dot', 'Five most-rated users', AMBER),
             ('dot', 'Other users  ·  size = ratings received', SLATE)]
    for i, (kind, label, colours) in enumerate(rows):
        legend_row(draw, x, 700 + i * 50, kind, label, small, MUTED if i else TEXT, colours)
    draw.text((52, 1028), FOOTER, font=font('Regular', 18), fill=FAINT)
    return canvas


def build_video(chosen, dropped, crop):
    frames_dir = CAPTURES / 'composed'
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir()
    entries = []
    for index, path in enumerate(chosen):
        if index in dropped:
            entries[-1][1] += 1 / STEPS  # keep the timing of a dropped frame on the previous frame
            continue
        out = frames_dir / f'frame_{index:03d}.png'
        video_frame(Image.open(path).convert('RGB'), index, crop).save(out)
        key, step = divmod(index, STEPS)
        entries.append([out, HOLD[key] if step == 0 else 1 / STEPS])
    listing = frames_dir / 'playlist.txt'
    lines = []
    for out, seconds in entries:
        lines += [f"file '{out}'", f'duration {seconds:.6f}']
    lines.append(f"file '{entries[-1][0]}'")
    listing.write_text('\n'.join(lines) + '\n')
    movie = OUT / 'bitcoin_otc_spotlight_timeline.mp4'
    total = sum(seconds for _, seconds in entries)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-vf', 'fps=24,format=yuv420p', '-t', f'{total:.3f}', '-c:v', 'libx264', '-preset', 'slow',
                    '-crf', '18', '-movflags', '+faststart', str(movie)], check=True)
    shutil.copyfile(movie, ROOT / 'presentation/bitcoin_otc_spotlight_timeline.mp4')
    shutil.copyfile(entries[-1][0], OUT / 'bitcoin_otc_spotlight_timeline_poster.png')
    return movie, total


# ------------------------------------------------------------------ stills

def dark_figure(image):
    canvas = Image.new('RGB', (1920, 1080), BG)
    paste_fit(canvas, image.crop(content_box([image], BG, 40)), (40, 40, 1190, 1000))
    draw = ImageDraw.Draw(canvas)
    x = 1250
    spaced(draw, (x, 92), 'BITCOIN OTC  ·  WEB OF TRUST', font('SemiBold', 21), AMBER, 2)
    draw.multiline_text((x, 132), 'Strong ratings among the\nmost-rated users',
                        font=font('Bold', 44), fill=TEXT, spacing=12)
    draw.text((x, 270), '22 users  ·  76 strong ratings  ·  2010–2015', font=font('Medium', 27), fill=MUTED)
    rows = [('line', 'Positive rating (+5 to +10)', (5, TEAL)), ('line', 'Negative rating (−5 to −10)', (5, CORAL)),
            ('line', 'Thicker line = stronger rating', (8, '#4B5B73')), ('dot', 'Five most-rated users', AMBER),
            ('dot', 'Other users  ·  size = ratings received', SLATE)]
    for i, (kind, label, colours) in enumerate(rows):
        legend_row(draw, x, 380 + i * 56, kind, label, font('Regular', 26), TEXT if i < 2 else MUTED, colours)
    draw.text((x, 690), 'Arrows point from the rater to the rated user.', font=font('Regular', 24), fill=MUTED)
    draw.multiline_text((x, 760), 'The 25 users with the most positive ratings\nreceived; three have no strong rating with\nthe others and are not shown.',
                        font=font('Regular', 22), fill=FAINT, spacing=9)
    draw.text((52, 1028), 'Drawn in Cytoscape 3.10  ·  22 of 5,881 users  ·  ratings of ±5 or more',
              font=font('Regular', 18), fill=FAINT)
    canvas.save(OUT / 'bitcoin_otc_spotlight.png')


def light_figure(image):
    """Report figure: network plus a compact legend, large enough to read in print."""
    network = image.crop(content_box([image], LIGHT['bg'], 30))
    height = 1500
    width = round(network.width * (height - 80) / network.height)
    legend_x = 60 + width + 140
    canvas = Image.new('RGB', (legend_x + 1250, height), LIGHT['bg'])
    paste_fit(canvas, network, (40, 40, 40 + width, height - 40))
    draw = ImageDraw.Draw(canvas)
    fnt = font('Regular', 62)
    rows = [('line', 'Positive rating (+5 to +10)', (9, LIGHT['teal'])),
            ('line', 'Negative rating (−5 to −10)', (9, LIGHT['coral'])),
            ('line', 'Thicker = stronger rating', (16, '#9AA5B4')),
            ('dot', 'Five most-rated users', LIGHT['amber']),
            ('dot', 'Size = ratings received', LIGHT['slate'])]
    top = (height - len(rows) * 150) // 2
    for i, (kind, label, colours) in enumerate(rows):
        y = top + i * 150
        if kind == 'dot':
            draw.ellipse((legend_x + 10, y + 12, legend_x + 66, y + 68), fill=colours)
        else:
            draw.line((legend_x, y + 40, legend_x + 90, y + 40), fill=colours[1], width=colours[0])
        draw.text((legend_x + 130, y), label, font=fnt, fill=LIGHT['text'])
    canvas.save(OUT / 'bitcoin_otc_spotlight_light.png')
    return canvas.size


def main():
    run = CAPTURES / json.loads((CAPTURES / 'latest.json').read_text())['run']
    capture = json.loads((run / 'capture.json').read_text())

    dark_figure(Image.open(run / 'complete_dark.png').convert('RGB'))
    light_size = light_figure(Image.open(run / 'complete_light.png').convert('RGB'))

    chosen, dropped, recordings = choose_frames(run)
    first, last = Image.open(chosen[0]).convert('RGB'), Image.open(chosen[-1]).convert('RGB')
    crop = content_box([first, last], BG, 40)
    movie, seconds = build_video(chosen, dropped, crop)

    (OUT / 'cyanimator_provenance.json').write_text(json.dumps({
        'view': 'Top 25 users by positive ratings received in the full data; ratings of absolute score 5 or more '
                'among them; 3 users without such a rating omitted (22 users, 76 directed ratings)',
        'cytoscape': capture['cytoscape'], 'cyanimator': capture['cyanimator'], 'layout': capture['layout'],
        'keyframes': capture['keyframes'], 'steps_between_keyframes': STEPS,
        'recordings': recordings,
        'frame_choice': 'for every frame index, the recording closest to the pixel median of all recordings',
        'omitted_frames': dropped,
        'omitted_reason': 'CyAnimator render glitches: the frame differs from both neighbours, which agree',
        'frames_used': len(chosen) - len(dropped), 'video_seconds': round(seconds, 2),
        'frame_sha256': {path.parent.name + '/' + path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                         for i, path in enumerate(chosen) if i not in dropped},
        'movie_sha256': hashlib.sha256(movie.read_bytes()).hexdigest(),
        'light_figure_size': light_size,
        'note': 'Users were chosen using all years, so this is an illustration of when their ratings appeared, '
                'not a sample of network growth. Frames between year ends are CyAnimator interpolation.',
    }, indent=2) + '\n')
    print('dropped frames:', dropped, '| video seconds:', round(seconds, 1), '| light figure:', light_size)


if __name__ == '__main__':
    main()
