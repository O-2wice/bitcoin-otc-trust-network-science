"""Draw the website charts from the stored results (no new analysis).

Run from the project folder after scripts/reproduce.py: python docs/make_figures.py
Writes SVG files for the website and PNG copies for the slides to docs/assets/.
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import NullFormatter
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'assets'
INK, MUTED, GRID = '#0F172A', '#64748B', '#E2E8F0'
TEAL, AMBER, CORAL, SLATE = '#0E9F8E', '#E59E1B', '#DC4363', '#94A3B8'

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    'font.family': 'Inter' if 'Inter' in fonts else 'DejaVu Sans',
    'font.size': 12, 'text.color': INK, 'axes.labelcolor': MUTED, 'axes.edgecolor': GRID,
    'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8, 'svg.fonttype': 'none',
})


def save(fig, name):
    fig.savefig(OUT / f'{name}.svg', bbox_inches='tight', transparent=True)
    fig.savefig(OUT / f'{name}.png', bbox_inches='tight', dpi=220, facecolor='white')
    plt.close(fig)


def concentration():
    cumulative = pd.read_csv(ROOT / 'outputs/temporal/annual_snapshots.csv').set_index('year_end')
    yearly = pd.read_csv(ROOT / 'outputs/sensitivity/annual_equal_volume_check.csv').set_index('year')
    years = list(range(2011, 2016))
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.fill_between(years, 100 * yearly.loc[years, 'equal_volume_share_low'],
                    100 * yearly.loc[years, 'equal_volume_share_high'], color=SLATE, alpha=0.18, lw=0)
    lines = [(100 * cumulative.loc[years, 'top_1_percent_incoming_share'], TEAL, 'All ratings so far', 0),
             (100 * yearly.loc[years, 'top_1_percent_share'], AMBER, 'New ratings that year', 7),
             (100 * yearly.loc[years, 'equal_volume_share_mean'], SLATE, 'Same, at equal volume', -8)]
    for values, colour, label, shift in lines:
        ax.plot(years, values, color=colour, lw=2.6, marker='o', ms=5)
        ax.annotate(label, (2015, values.iloc[-1]), xytext=(10, shift), textcoords='offset points',
                    va='center', color=colour, fontsize=11.5, fontweight='semibold')
    ax.set_xticks(years)
    ax.set_ylim(0, 27)
    ax.set_ylabel('Share of positive ratings held by the top 1%')
    ax.yaxis.set_major_formatter(lambda v, _: f'{v:.0f}%')
    ax.grid(axis='x', visible=False)
    save(fig, 'concentration')


def knn():
    table = pd.read_csv(ROOT / 'outputs/correlations/knn_by_degree.csv')
    summary = pd.read_csv(ROOT / 'outputs/correlations/correlation_summary.csv').iloc[0]
    shown = table[table.users_with_degree >= 2]
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.fill_between(table.degree, table.knn_rewired_p2_5, table.knn_rewired_p97_5, color=SLATE, alpha=0.25, lw=0)
    ax.plot(table.degree, table.knn_rewired_mean, color=MUTED, lw=1.8, label=f'Degree-preserving rewires (r = {summary.r_rewired_mean:.3f})')
    ax.scatter(shown.degree, shown.knn_observed, s=16, color=TEAL, zorder=3, label=f'Observed network (r = {summary.r_observed:.3f})')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xticks([1, 10, 100, 1000], ['1', '10', '100', '1000'])
    ax.set_yticks([20, 40, 60, 100, 200], ['20', '40', '60', '100', '200'])
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel('Degree k')
    ax.set_ylabel('Average degree of neighbours, $k_{nn}(k)$')
    ax.legend(frameon=False, loc='lower left', fontsize=10.5)
    one = table.iloc[0]
    ax.annotate(f'Users with one link: neighbours have\n{one.knn_observed:.0f} links on average ({one.knn_rewired_mean:.0f} after rewiring)',
                (1, one.knn_observed), xytext=(18, -4), textcoords='offset points', fontsize=10.5, color=INK, va='top')
    save(fig, 'knn')


def attachment():
    table = pd.read_csv(ROOT / 'outputs/theory/attachment_benchmarks.csv').set_index('benchmark')
    rows = [('Uniform', 'All possible recipients'), ('Tenure only', 'Same tenure'),
            ('Activity only', 'Same recent activity'), ('Tenure and activity', 'Same tenure and activity'),
            ('Tenure and ratings given', 'Same tenure, ratings given')]
    values = [table.loc[key, 'ratio_32+'] for key, _ in rows]
    colours = [SLATE, SLATE, TEAL, TEAL, TEAL]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    positions = range(len(rows))[::-1]
    ax.barh(list(positions), values, color=colours, height=0.6)
    for y, value in zip(positions, values):
        ax.text(value + 0.3, y, f'{value:.2f}×', va='center', fontsize=11.5, fontweight='semibold', color=INK)
    ax.set_yticks(list(positions), [label for _, label in rows])
    ax.axvline(1, color=CORAL, lw=1.2, ls=(0, (3, 3)))
    ax.text(1.2, len(rows) - 0.45, 'chance', color=CORAL, fontsize=10)
    ax.set_xlabel('How often users with 32+ earlier ratings were chosen, relative to the comparison group')
    ax.grid(axis='y', visible=False)
    ax.tick_params(axis='y', length=0, labelcolor=INK)
    save(fig, 'attachment')


def robustness():
    curves = pd.read_csv(ROOT / 'outputs/theory/percolation_curves.csv')
    thresholds = pd.read_csv(ROOT / 'outputs/theory/percolation_thresholds.csv').set_index('network')
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for network, strategy, colour, style, label in [
            ('ER', 'random', SLATE, ':', 'ER, random failures'),
            ('ER', 'highest_degree_first', SLATE, '--', 'ER, targeted attack'),
            ('Observed', 'random', TEAL, '-', 'Observed, random failures'),
            ('Observed', 'highest_degree_first', CORAL, '-', 'Observed, targeted attack')]:
        part = curves[(curves.network == network) & (curves.strategy == strategy)]
        ax.plot(part.fraction_removed, part.largest_component_share, color=colour, ls=style,
                lw=2.6 if network == 'Observed' else 1.6, label=label)
    fc = thresholds.loc['Observed', 'molloy_reed_threshold']
    ax.axvline(fc, color=TEAL, lw=1, ls=(0, (2, 3)))
    ax.text(fc - 0.01, 0.9, f'$f_c$ = {fc:.3f}', ha='right', color=TEAL, fontsize=10.5)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel('Fraction of users removed')
    ax.set_ylabel('Share of users in the largest component')
    ax.legend(frameon=False, fontsize=10.5, loc='upper right', bbox_to_anchor=(0.93, 0.82))
    save(fig, 'robustness')


def media():
    """Web-sized copies of the video, its poster and two analysis figures."""
    from PIL import Image
    import shutil
    shutil.copyfile(ROOT / 'outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4', OUT / 'timeline.mp4')
    for source, name, width in [('outputs/cytoscape/bitcoin_otc_spotlight_timeline_poster.png', 'timeline-poster.jpg', 1600),
                                ('outputs/structure/full_positive_network_layout.png', 'network.jpg', 1600),
                                ('outputs/theory/degree_ccdf_fits.png', 'degree-ccdf.jpg', 1800)]:
        image = Image.open(ROOT / source).convert('RGB')
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
        image.save(OUT / name, quality=88, optimize=True, progressive=True)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    concentration()
    knn()
    attachment()
    robustness()
    media()
    print('Wrote charts and media to', OUT.relative_to(ROOT))
