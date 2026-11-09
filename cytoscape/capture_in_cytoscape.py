"""Draw the strong-rating spotlight in Cytoscape and record it with CyAnimator.

Run with a freshly started Cytoscape 3.10 (CyREST on port 1234) and CyAnimator 2.2.1
installed, after `python scripts/export_cytoscape.py`. Restart Cytoscape before each run:
CyAnimator keeps the keyframes of earlier captures and has no command to clear them.
Cytoscape draws everything:

- two still images of the complete view (dark for slides and web, light for the report);
- one CyAnimator keyframe per year end from 2011 to 2015, plus a final complete view,
  recorded as PNG frames.

Raw exports go to outputs/cytoscape/captures/ (not tracked). Then run
`python cytoscape/compose_outputs.py` to add legends and build the figures and video.
"""
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://localhost:1234/v1'
GRAPH = ROOT / 'outputs/cytoscape/bitcoin_otc_spotlight.graphml'
OUT = ROOT / 'outputs/cytoscape/captures'
YEARS = [2011, 2012, 2013, 2014, 2015]
STEPS = 24          # CyAnimator frames between two keyframes
RESOLUTION = 400    # CyAnimator export size, in percent of the network view

RECORDINGS = 3     # CyAnimator sometimes mis-renders a frame; compose_outputs.py keeps the version two recordings agree on

DARK = {'background': '#0B1220', 'node': '#94A3B8', 'node_off': '#1E293B', 'hub': '#F5B841',
        'border': '#0B1220', 'label': '#F1F5F9', 'positive': '#2EC4B6', 'negative': '#F2617A',
        'positive_new': '#9BFFF2', 'negative_new': '#FFB8C6'}
LIGHT = {'background': '#FFFFFF', 'node': '#A3B1C2', 'hub': '#E59E1B', 'border': '#FFFFFF',
         'label': '#111827', 'positive': '#0E9F8E', 'negative': '#DC4363'}


def call(path, method='GET', data=None):
    payload = None if data is None else json.dumps(data).encode()
    request = Request(BASE + path, data=payload, method=method,
                      headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=120) as response:
        raw = response.read()
    result = json.loads(raw) if raw else None
    if isinstance(result, dict) and result.get('errors'):
        raise RuntimeError(result['errors'])
    return result


def save_png(network, view, path, height=2000):
    with urlopen(f'{BASE}/networks/{network}/views/{view}.png?h={height}', timeout=120) as response:
        path.write_bytes(response.read())


def add_style(style):
    if style['title'] in call('/styles'):
        call(f"/styles/{style['title'].replace(' ', '%20')}", 'DELETE')
    call('/styles', 'POST', style)


def apply_style(network, title):
    call('/commands/vizmap/apply', 'POST', {'network': f'SUID:{network}', 'styles': title})
    time.sleep(2)  # let the view finish redrawing before an export or capture


def discrete(column, prop, values):
    return {'mappingType': 'discrete', 'mappingColumn': column, 'mappingColumnType': 'String',
            'visualProperty': prop, 'map': [{'key': k, 'value': str(v)} for k, v in values.items()]}


def node_size_mappings(column_type):
    points = [{'value': 115, 'lesser': 30, 'equal': 30, 'greater': 30},
              {'value': 535, 'lesser': 70, 'equal': 70, 'greater': 70}]
    return [{'mappingType': 'continuous', 'mappingColumn': 'in_degree', 'mappingColumnType': column_type,
             'visualProperty': prop, 'points': points} for prop in ('NODE_SIZE', 'NODE_WIDTH', 'NODE_HEIGHT')]


def base_defaults(theme):
    return [
        {'visualProperty': 'NETWORK_BACKGROUND_PAINT', 'value': theme['background']},
        {'visualProperty': 'NODE_SHAPE', 'value': 'ELLIPSE'},
        {'visualProperty': 'NODE_BORDER_PAINT', 'value': theme['border']},
        {'visualProperty': 'NODE_BORDER_WIDTH', 'value': 2.5},
        {'visualProperty': 'NODE_LABEL_COLOR', 'value': theme['label']},
        {'visualProperty': 'NODE_LABEL_FONT_SIZE', 'value': 26},
        {'visualProperty': 'NODE_LABEL_FONT_FACE', 'value': 'SansSerif.bold,bold,26'},
        {'visualProperty': 'NODE_LABEL_POSITION', 'value': 'S,N,c,0.00,4.00'},  # label just below the node
        {'visualProperty': 'EDGE_CURVED', 'value': True},
        {'visualProperty': 'EDGE_TARGET_ARROW_SHAPE', 'value': 'DELTA'},
        {'visualProperty': 'EDGE_TARGET_ARROW_SIZE', 'value': 7},
    ]


def complete_style(title, theme, degree_type, rating_type):
    """All 76 ratings: colour = sign, width = rating strength, size = ratings received."""
    return {'title': title,
            'defaults': base_defaults(theme) + [{'visualProperty': 'EDGE_TRANSPARENCY', 'value': 205}],
            'mappings': node_size_mappings(degree_type) + [
                discrete('hub', 'NODE_FILL_COLOR', {'yes': theme['hub'], 'no': theme['node']}),
                {'mappingType': 'passthrough', 'mappingColumn': 'label', 'mappingColumnType': 'String',
                 'visualProperty': 'NODE_LABEL'},
                discrete('sign', 'EDGE_STROKE_UNSELECTED_PAINT', {'positive': theme['positive'], 'negative': theme['negative']}),
                discrete('sign', 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', {'positive': theme['positive'], 'negative': theme['negative']}),
                {'mappingType': 'continuous', 'mappingColumn': 'abs_rating', 'mappingColumnType': rating_type,
                 'visualProperty': 'EDGE_WIDTH',
                 'points': [{'value': 5, 'lesser': 1.6, 'equal': 1.6, 'greater': 1.6},
                            {'value': 10, 'lesser': 4.2, 'equal': 4.2, 'greater': 4.2}]},
            ]}


def year_style(year, degree_type):
    """Ratings recorded by this year end. This year's new ratings are bright and thick,
    earlier ones are faded, later ones hidden. Users appear when they get their first rating."""
    t = DARK
    edge_colour = {'new_positive': t['positive_new'], 'new_negative': t['negative_new'],
                   'old_positive': t['positive'], 'old_negative': t['negative'], 'hidden': t['background']}
    return {'title': f'Spotlight {year}',
            'defaults': base_defaults(t),
            'mappings': node_size_mappings(degree_type) + [
                {'mappingType': 'passthrough', 'mappingColumn': 'label', 'mappingColumnType': 'String',
                 'visualProperty': 'NODE_LABEL'},
                discrete(f'node_{year}', 'NODE_FILL_COLOR',
                         {'hub_on': t['hub'], 'hub_off': t['hub'], 'on': t['node'], 'off': t['node_off']}),
                discrete(f'node_{year}', 'NODE_TRANSPARENCY', {'hub_on': 255, 'hub_off': 70, 'on': 255, 'off': 110}),
                discrete(f'node_{year}', 'NODE_LABEL_TRANSPARENCY', {'hub_on': 255, 'hub_off': 90, 'on': 255, 'off': 255}),
                discrete(f'edge_{year}', 'EDGE_STROKE_UNSELECTED_PAINT', edge_colour),
                discrete(f'edge_{year}', 'EDGE_TARGET_ARROW_UNSELECTED_PAINT', edge_colour),
                discrete(f'edge_{year}', 'EDGE_TRANSPARENCY',
                         {'new_positive': 255, 'new_negative': 255, 'old_positive': 150, 'old_negative': 170, 'hidden': 0}),
                discrete(f'edge_{year}', 'EDGE_WIDTH',
                         {'new_positive': 4.4, 'new_negative': 4.4, 'old_positive': 2.0, 'old_negative': 2.0, 'hidden': 0.5}),
            ]}


def build_elements(graph):
    """Nodes and edges with the columns the styles need."""
    edge_year = {(u, v): max(int(d['year']), YEARS[0]) for u, v, d in graph.edges(data=True)}  # 2010 counts as 2011
    first_year = {}
    for (u, v), year in edge_year.items():
        for user in (u, v):
            first_year[user] = min(first_year.get(user, 9999), year)

    nodes = []
    for user, attrs in graph.nodes(data=True):
        hub = bool(attrs.get('display_label'))
        data = {'id': user, 'name': user, 'label': attrs.get('display_label', ''),
                'in_degree': int(attrs['positive_in_degree']), 'hub': 'yes' if hub else 'no'}
        for year in YEARS:
            data[f'node_{year}'] = ('hub_' if hub else '') + ('on' if first_year[user] <= year else 'off')
        nodes.append({'data': data})

    edges = []
    for u, v, attrs in graph.edges(data=True):
        year = edge_year[(u, v)]
        data = {'source': u, 'target': v, 'rating': int(attrs['rating']),
                'abs_rating': abs(int(attrs['rating'])), 'sign': attrs['sign'], 'year': int(attrs['year'])}
        for keyframe in YEARS:
            if year > keyframe:
                data[f'edge_{keyframe}'] = 'hidden'
            elif year == keyframe:
                data[f'edge_{keyframe}'] = 'new_' + attrs['sign']
            else:
                data[f'edge_{keyframe}'] = 'old_' + attrs['sign']
        edges.append({'data': data})
    counts = [sum(year <= y for year in edge_year.values()) for y in YEARS]
    return nodes, edges, counts


def main():
    graph = nx.read_graphml(GRAPH)
    assert len(graph) == 22 and graph.number_of_edges() == 76

    run = OUT / time.strftime('run_%Y%m%d_%H%M%S')
    run.mkdir(parents=True)

    nodes, edges, counts = build_elements(graph)
    created = call('/networks?collection=Bitcoin%20OTC%20spotlight', 'POST',
                   {'data': {'name': 'Bitcoin OTC spotlight'}, 'elements': {'nodes': nodes, 'edges': edges}})
    network = created['networkSUID']
    view = call(f'/networks/{network}/views')[0]
    call('/commands/network/set%20current', 'POST', {'network': f'SUID:{network}'})
    time.sleep(1)

    # Fixed positions from a Kamada-Kawai layout (no randomness), drawn by Cytoscape.
    positions = nx.kamada_kawai_layout(graph.to_undirected())
    suid = {row['name']: row['SUID'] for row in call(f'/networks/{network}/tables/defaultnode/rows')}
    call(f'/networks/{network}/views/{view}/nodes', 'PUT', [
        {'SUID': suid[user], 'view': [{'visualProperty': 'NODE_X_LOCATION', 'value': 560 * x},
                                      {'visualProperty': 'NODE_Y_LOCATION', 'value': 430 * y}]}
        for user, (x, y) in positions.items()])

    columns = call(f'/networks/{network}/tables/defaultnode/columns')
    degree_type = next(c['type'] for c in columns if c['name'] == 'in_degree')
    columns = call(f'/networks/{network}/tables/defaultedge/columns')
    rating_type = next(c['type'] for c in columns if c['name'] == 'abs_rating')

    # Still images of the complete view.
    for name, theme in (('dark', DARK), ('light', LIGHT)):
        style = complete_style(f'Spotlight complete {name}', theme, degree_type, rating_type)
        add_style(style)
        apply_style(network, style['title'])
        call('/commands/view/fit%20content', 'POST', {'network': f'SUID:{network}'})
        time.sleep(2)
        save_png(network, view, run / f'complete_{name}.png', height=3000)
    # Keep copies of the static styles for opening the view by hand.
    for name, theme in (('', DARK), ('_light', LIGHT)):
        style = complete_style(f'Bitcoin OTC spotlight{name.replace("_", " ")}', theme, 'Integer', 'Integer')
        (ROOT / f'cytoscape/spotlight_style{name}.json').write_text(json.dumps(style, indent=2) + '\n')

    # CyAnimator keyframes: one per year end, then the complete view.
    keyframes = []
    for year in YEARS:
        style = year_style(year, degree_type)
        add_style(style)
        apply_style(network, style['title'])
        call('/commands/cyanimator/capture%20frame', 'POST', {'network': f'SUID:{network}', 'interpolate': str(STEPS)})
        save_png(network, view, run / f'keyframe_{year}.png', height=1200)
        keyframes.append({'keyframe': str(year), 'ratings_shown': counts[YEARS.index(year)], 'style': style['title']})
        print(keyframes[-1], flush=True)
    apply_style(network, 'Spotlight complete dark')
    call('/commands/cyanimator/capture%20frame', 'POST', {'network': f'SUID:{network}', 'interpolate': str(STEPS)})
    keyframes.append({'keyframe': 'complete', 'ratings_shown': 76, 'style': 'Spotlight complete dark'})

    expected = STEPS * (len(keyframes) - 1) + 1
    for number in range(RECORDINGS):
        folder = run / f'recording_{number + 1}'
        folder.mkdir()
        start = time.time()
        call('/commands/cyanimator/record', 'POST', {'outputDir': str(folder), 'resolution': str(RESOLUTION)})
        last = folder / f'Frame_{expected - 1:03d}.png'
        deadline = time.monotonic() + 600
        while not last.exists() or last.stat().st_mtime < start:
            if time.monotonic() > deadline:
                raise TimeoutError(f'CyAnimator did not finish its {expected}-frame export')
            time.sleep(1)
        time.sleep(3)  # the last file may still be being written
        assert len(list(folder.glob('Frame_*.png'))) == expected
        print('Recorded', folder.name, flush=True)

    (run / 'capture.json').write_text(json.dumps({
        'cytoscape': call('/version'), 'cyanimator': '2.2.1', 'network_suid': network,
        'layout': 'networkx kamada_kawai_layout, x scaled by 560 and y by 430, set as Cytoscape node positions',
        'keyframes': keyframes, 'steps_between_keyframes': STEPS, 'resolution_percent': RESOLUTION,
        'frames_per_recording': expected, 'recordings': RECORDINGS}, indent=2) + '\n')
    (OUT / 'latest.json').write_text(json.dumps({'run': run.name}) + '\n')
    print('Saved', run, flush=True)


if __name__ == '__main__':
    main()
