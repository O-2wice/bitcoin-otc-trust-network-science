"""Build the website's charts, network data and media from the stored results.

Run from the project folder after scripts/reproduce.py and scripts/full_network_layout.py:
    python docs/make_figures.py
Everything is read from outputs/ (and the data file for link years); no new analysis.
Writes to docs/assets/: SVG charts (PNG copies for the slides), network.json for the
scrolling animation, and web-sized copies of the Cytoscape video and figures.
"""
import json
from pathlib import Path
import random
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import NullFormatter
import networkx as nx
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'assets'
INK, MUTED, GRID = '#1A1A1A', '#6B6B66', '#E6E3DD'
BLUE, BRICK, GREY, LIGHT = '#24507A', '#C1442E', '#9A958C', '#D9D5CC'

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    'font.family': 'Lato' if 'Lato' in fonts else 'DejaVu Sans',
    'font.size': 12, 'text.color': INK, 'axes.labelcolor': MUTED, 'axes.edgecolor': '#BDB8AE',
    'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
    'svg.fonttype': 'path',  # text as outlines, so the charts look the same in every browser
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
                    100 * yearly.loc[years, 'equal_volume_share_high'], color=GREY, alpha=0.18, lw=0)
    lines = [(100 * cumulative.loc[years, 'top_1_percent_incoming_share'], BLUE, 'All ratings so far', 0),
             (100 * yearly.loc[years, 'top_1_percent_share'], BRICK, 'New ratings that year', 7),
             (100 * yearly.loc[years, 'equal_volume_share_mean'], GREY, 'Same, at equal volume', -8)]
    for values, colour, label, shift in lines:
        ax.plot(years, values, color=colour, lw=2.4, marker='o', ms=4.5)
        ax.annotate(label, (2015, values.iloc[-1]), xytext=(10, shift), textcoords='offset points',
                    va='center', color=colour, fontsize=11.5, fontweight='bold')
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
    ax.fill_between(table.degree, table.knn_rewired_p2_5, table.knn_rewired_p97_5, color=GREY, alpha=0.25, lw=0)
    ax.plot(table.degree, table.knn_rewired_mean, color=MUTED, lw=1.8, label=f'Degree-preserving rewires (r = {summary.r_rewired_mean:.3f})')
    ax.scatter(shown.degree, shown.knn_observed, s=16, color=BRICK, zorder=3, label=f'Observed network (r = {summary.r_observed:.3f})')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xticks([1, 10, 100, 1000], ['1', '10', '100', '1000'])
    ax.set_yticks([20, 40, 60, 100, 200], ['20', '40', '60', '100', '200'])
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel('Degree k')
    ax.set_ylabel('Average degree of neighbours')
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
    colours = [GREY, GREY, BLUE, BLUE, BLUE]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    positions = list(range(len(rows)))[::-1]
    ax.barh(positions, values, color=colours, height=0.6)
    for y, value in zip(positions, values):
        ax.text(value + 0.3, y, f'{value:.2f}×', va='center', fontsize=11.5, fontweight='bold', color=INK)
    ax.set_yticks(positions, [label for _, label in rows])
    ax.axvline(1, color=BRICK, lw=1.2, ls=(0, (3, 3)))
    ax.text(1.2, len(rows) - 0.45, 'chance', color=BRICK, fontsize=10)
    ax.set_xlabel('How often users with 32+ earlier ratings were chosen, relative to the comparison group')
    ax.grid(axis='y', visible=False)
    ax.tick_params(axis='y', length=0, labelcolor=INK)
    save(fig, 'attachment')


def robustness():
    curves = pd.read_csv(ROOT / 'outputs/theory/percolation_curves.csv')
    thresholds = pd.read_csv(ROOT / 'outputs/theory/percolation_thresholds.csv').set_index('network')
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for network, strategy, colour, style, label in [
            ('ER', 'random', GREY, ':', 'ER, random failures'),
            ('ER', 'highest_degree_first', GREY, '--', 'ER, targeted attack'),
            ('Observed', 'random', BLUE, '-', 'Observed, random failures'),
            ('Observed', 'highest_degree_first', BRICK, '-', 'Observed, targeted attack')]:
        part = curves[(curves.network == network) & (curves.strategy == strategy)]
        ax.plot(part.fraction_removed, part.largest_component_share, color=colour, ls=style,
                lw=2.4 if network == 'Observed' else 1.5, label=label)
    fc = thresholds.loc['Observed', 'molloy_reed_threshold']
    ax.axvline(fc, color=BLUE, lw=1, ls=(0, (2, 3)))
    ax.text(fc - 0.01, 0.9, f'critical threshold {fc:.3f}', ha='right', color=BLUE, fontsize=10.5)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel('Fraction of users removed')
    ax.set_ylabel('Share of users in the largest component')
    ax.legend(frameon=False, fontsize=10.5, loc='upper right', bbox_to_anchor=(0.93, 0.82))
    save(fig, 'robustness')


def community_layout(graph, community):
    """Spring layout of the largest component in which links inside a Louvain community pull
    harder (weight 1) than links between communities (weight 0.06), so communities form clusters.
    A drawing aid only. It takes about six minutes, so the result is saved in docs/ and reused."""
    saved = ROOT / 'docs' / 'layout_positions.csv'
    if not saved.exists():
        main = graph.subgraph(max(nx.connected_components(graph), key=len)).copy()
        for u, v in main.edges():
            main[u][v]['w'] = 1.0 if community[u] == community[v] else 0.06
        start = pd.read_csv(ROOT / 'outputs/structure/full_positive_network_layout_positions.csv').set_index('node')
        pos = nx.spring_layout(main, pos={v: (start.x[v], start.y[v]) for v in main}, weight='w',
                               iterations=120, seed=2026, k=0.6 / len(main) ** 0.5)
        pd.DataFrame([(v, x, y) for v, (x, y) in pos.items()], columns=['node', 'x', 'y']) \
            .sort_values('node').to_csv(saved, index=False, float_format='%.6f')
    pos = pd.read_csv(saved).set_index('node')
    # Pull far-out points inwards (r -> R tanh(r/R)) so a few distant users do not shrink the picture.
    x, y = pos.x - pos.x.median(), pos.y - pos.y.median()
    r = (x ** 2 + y ** 2) ** 0.5
    reach = r.quantile(0.97)
    scale = (reach * np.tanh(r / reach) / r).fillna(1.0)
    return pd.DataFrame({'x': x * scale, 'y': y * scale})


def network_data():
    """Positions, degrees, communities and link years for the scrolling network animation."""
    ratings = pd.read_csv(ROOT / 'data/soc-sign-bitcoinotc.csv.gz', header=None, names=['source', 'target', 'rating', 'time'])
    positive = ratings[ratings.rating > 0]
    when = pd.to_datetime(positive.time, unit='s', utc=True)
    year = when.dt.year + when.dt.day_of_year / 366  # e.g. 2013.5 is mid-2013
    first = {}
    for u, v, t in zip(positive.source, positive.target, year):
        key = (min(u, v), max(u, v))
        first[key] = min(first.get(key, 9999), t)

    graph = nx.Graph()
    graph.add_nodes_from(set(ratings.source) | set(ratings.target))
    graph.add_edges_from(first)
    degree = dict(graph.degree())
    in_degree = positive.groupby('target').size()

    communities = pd.read_csv(ROOT / 'outputs/structure/communities.csv').set_index('node')
    largest_groups = list(communities.drop_duplicates('community').sort_values('community_size', ascending=False).community[:5])
    main = community_layout(graph, communities.community)

    # The two removal scenarios at 15%, with the same rules as the analysis.
    ranked = sorted(graph, key=lambda v: (-degree[v], v))
    attacked = set(ranked[:round(0.15 * len(graph))])
    randomly = set(random.Random(2026).sample(sorted(graph), round(0.15 * len(graph))))

    def survivors(removed):
        rest = graph.subgraph(set(graph) - removed)
        return max(nx.connected_components(rest), key=len)

    attack_lcc, random_lcc = survivors(attacked), survivors(randomly)

    nodes = list(main.index)
    index = {v: i for i, v in enumerate(nodes)}
    xs, ys = main.x, main.y
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    span = max(x1 - x0, y1 - y0)
    node_year = {v: 9999.0 for v in nodes}
    edges = {'s': [], 't': [], 'y': []}
    for (u, v), t in sorted(first.items(), key=lambda item: item[1]):
        if u in index and v in index:
            edges['s'].append(index[u]); edges['t'].append(index[v]); edges['y'].append(round(t, 3))
            node_year[u] = min(node_year[u], t); node_year[v] = min(node_year[v], t)

    def state(v, removed, lcc):
        return 0 if v in removed else (2 if v in lcc else 1)  # 0 removed, 1 cut off, 2 still connected

    hubs = [int(v) for v, _ in sorted(in_degree.items(), key=lambda item: (-item[1], item[0]))[:5]]  # ties: lower ID, as in Cytoscape
    data = {
        'nodes': {
            'id': [int(v) for v in nodes],
            'x': [round(10000 * (xs[v] - x0) / span) for v in nodes],
            'y': [round(10000 * (ys[v] - y0) / span) for v in nodes],
            'k': [degree[v] for v in nodes],
            'g': [largest_groups.index(communities.community[v]) if communities.community[v] in largest_groups else -1 for v in nodes],
            't': [round(node_year[v], 3) for v in nodes],
            'attack': [state(v, attacked, attack_lcc) for v in nodes],
            'random': [state(v, randomly, random_lcc) for v in nodes],
        },
        'edges': edges,
        'hubs': [index[v] for v in hubs if v in index],
        'aspect': round((x1 - x0) / (y1 - y0), 4),
        'note': 'Largest connected component of the undirected network of positive ratings; positions from a '
                'community-weighted spring layout (docs/layout_positions.csv); t = year of first positive rating.',
    }
    (OUT / 'network.json').write_text(json.dumps(data, separators=(',', ':')))
    hub = data['hubs'][0]
    neighbours = [degree[v] for v in graph[nodes[hub]]]
    print(f'network.json: {len(nodes)} users, {len(edges["s"])} links; '
          f'attack keeps {len(attack_lcc) / len(graph):.3f}, random keeps {len(random_lcc) / len(graph):.3f}; '
          f'user {nodes[hub]} has {len(neighbours)} neighbours, {sum(k <= 3 for k in neighbours) / len(neighbours):.0%} with 3 or fewer links')


def media():
    """Web-sized copies of the Cytoscape video and figures and an analysis figure."""
    shutil.copyfile(ROOT / 'outputs/cytoscape/bitcoin_otc_spotlight_timeline.mp4', OUT / 'timeline.mp4')
    for source, name, width in [('outputs/cytoscape/bitcoin_otc_spotlight_timeline_poster.png', 'timeline-poster.jpg', 1600),
                                ('outputs/cytoscape/bitcoin_otc_spotlight_light.png', 'cytoscape-light.jpg', 1600),
                                ('outputs/theory/degree_ccdf_fits.png', 'degree-ccdf.jpg', 1800)]:
        image = Image.open(ROOT / source).convert('RGB')
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
        image.save(OUT / name, quality=88, optimize=True, progressive=True)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for old in ('network.jpg',):
        (OUT / old).unlink(missing_ok=True)
    concentration()
    knn()
    attachment()
    robustness()
    network_data()
    media()
    print('Wrote charts, network data and media to', OUT.relative_to(ROOT))
