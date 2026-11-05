"""Capture year-specific styles so CyAnimator replay retains edge visibility.

Requires running Cytoscape/CyREST and CyAnimator. It imports a separate network,
keeps its layout fixed, captures five keyframes, and exports CyAnimator frames.
"""
import copy
import json
from pathlib import Path
import time
from urllib.error import HTTPError
from urllib.request import urlopen
import networkx as nx
from record_timeline import call, BASE, ROOT, NETWORK_FILE, STYLE_FILE, YEARS

OUT = ROOT / 'outputs/cytoscape/cyanimator_verified'

def main():
    OUT.mkdir(exist_ok=True)
    source = nx.read_graphml(NETWORK_FILE)
    assert len(source) == 22 and source.number_of_edges() == 76
    # A fresh CyJS network avoids GraphML group nodes created by repeated imports.
    payload = {'data': {'name': 'Bitcoin OTC verified CyAnimator timeline'}, 'elements': {
        'nodes': [{'data': {'id': str(v), 'name': str(v), **attrs}} for v, attrs in source.nodes(data=True)],
        'edges': [{'data': {'source': str(u), 'target': str(v), **attrs,
                            'year_key': str(int(attrs['year']))}}
                  for u, v, attrs in source.edges(data=True)]}}
    imported = call(f'/networks?collection=Bitcoin%20OTC%20animation%20{time.time_ns()}', 'POST', payload)
    print('Created network:', imported, flush=True)
    network = imported['networkSUID']
    run_dir = OUT / f'network_{network}'
    run_dir.mkdir(exist_ok=True)
    views = call(f'/networks/{network}/views')
    view = views[0]
    # CyAnimator captures the application's current view, even when a network
    # argument names a different frame manager. Select this network explicitly.
    call('/commands/network/set%20current', 'POST', {'network': f"SUID:{network}"})
    time.sleep(1)
    node_columns = call(f'/networks/{network}/tables/defaultnode/columns')
    node_type = next(x['type'] for x in node_columns if x['name'] == 'positive_in_degree')
    edge_ids = call(f'/networks/{network}/edges')
    years = {edge_id: call(f'/networks/{network}/edges/{edge_id}')['data']['year'] for edge_id in edge_ids}
    call('/commands/layout/force-directed', 'POST', {'network': f"SUID:{network}"})
    time.sleep(.5)
    capture_log = []
    for year in YEARS:
        style = copy.deepcopy(json.loads(STYLE_FILE.read_text()))
        style['defaults'].extend([{'visualProperty':'EDGE_VISIBLE', 'value':True},
                                  {'visualProperty':'NODE_VISIBLE', 'value':True}])
        style['title'] = f'Bitcoin OTC CyAnimator {network} year {year}'
        for mapping in style['mappings']:
            if mapping['mappingColumn'] == 'positive_in_degree':
                mapping['mappingColumnType'] = node_type
        size_mapping = next(m for m in style['mappings'] if m['visualProperty'] == 'NODE_SIZE')
        for dimension in ['NODE_WIDTH', 'NODE_HEIGHT']:
            dimension_mapping = copy.deepcopy(size_mapping)
            dimension_mapping['visualProperty'] = dimension
            style['mappings'].append(dimension_mapping)
        style['mappings'].append({
            'mappingType': 'discrete', 'mappingColumn': 'year_key',
            'mappingColumnType': 'String', 'visualProperty': 'EDGE_TRANSPARENCY',
            'map': [{'key': str(int(y)), 'value': str(190 if y <= year else 0)}
                    for y in sorted(set(years.values()))],
        })
        # A distinct style object for each captured year also survives replay.
        try:
            call('/styles', 'POST', style)
        except HTTPError as error:
            print('Style creation failed:', error.read().decode(), flush=True)
            raise
        call('/commands/vizmap/apply', 'POST', {'network': f"SUID:{network}", 'styles': style['title']})
        if year == YEARS[0]:
            call('/commands/view/fit%20content', 'POST', {'network': f"SUID:{network}"})
            time.sleep(.5)
            call('/commands/vizmap/apply', 'POST', {'network': f"SUID:{network}", 'styles': style['title']})
        # Let the Swing view finish applying the style before capture.
        time.sleep(.5)
        response = call('/commands/cyanimator/capture%20frame', 'POST',
                        {'network': f"SUID:{network}", 'interpolate': '24'})
        with urlopen(BASE + f'/networks/{network}/views/{view}.png', timeout=45) as response_image:
            (run_dir / f'keyframe_{year}.png').write_bytes(response_image.read())
        capture_log.append({'year': year, 'visible_edges': sum(y <= year for y in years.values()),
                            'style': style['title'], 'capture_response': response})
        print(year, capture_log[-1], flush=True)
    frames = call('/commands/cyanimator/list%20frames', 'POST', {'network': f"SUID:{network}"})
    print('Captured frames:', frames, flush=True)
    start = time.time()
    result = call('/commands/cyanimator/record', 'POST', {'outputDir': str(run_dir), 'resolution': '100'})
    # This app exports 24 interpolated steps per interval: 4*24 + 1 frames.
    last_frame = run_dir / 'Frame_096.png'
    deadline = time.monotonic() + 60
    while not last_frame.exists() or last_frame.stat().st_mtime < start:
        if time.monotonic() > deadline:
            raise TimeoutError('CyAnimator did not finish its 97-frame export')
        time.sleep(.5)
    assert len(list(run_dir.glob('Frame_*.png'))) == 97
    (run_dir / 'capture_manifest.json').write_text(json.dumps({
        'network_suid': network, 'view_suid': view, 'keyframes': capture_log,
        'record_response': result, 'note': 'Inspect recorded frames, not only these source keyframes.'
    }, indent=2) + '\n')
    (OUT / 'latest_capture.json').write_text(json.dumps({'directory': run_dir.name}) + '\n')
    print('Record response:', result, flush=True)

if __name__ == '__main__':
    main()
