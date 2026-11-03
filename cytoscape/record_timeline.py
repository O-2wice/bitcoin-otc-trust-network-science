"""Record cumulative strong-rating edges with CyAnimator in a running Cytoscape.

Run after export_cytoscape.py and after installing the CyAnimator app.
The top-user cohort is fixed using the full dataset; this is a visual example,
not an unbiased historical sample of the whole network.
"""

import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
BASE = "http://localhost:1234/v1"
NETWORK_FILE = ROOT / "outputs/cytoscape/bitcoin_otc_spotlight.graphml"
STYLE_FILE = ROOT / "cytoscape/spotlight_style.json"
FRAMES = ROOT / "outputs/cytoscape/animation_frames"
YEARS = (2011, 2012, 2013, 2014, 2015)


def call(path, method="GET", data=None):
    payload = None if data is None else json.dumps(data).encode()
    req = Request(BASE + path, data=payload, method=method,
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=45) as response:
        raw = response.read()
    result = json.loads(raw) if raw else None
    if isinstance(result, dict) and result.get("errors"):
        raise RuntimeError(result["errors"])
    return result


def main():
    FRAMES.mkdir(parents=True, exist_ok=True)
    style = json.loads(STYLE_FILE.read_text())
    if style["title"] not in call("/styles"):
        call("/styles", "POST", style)
    imported = call("/commands/network/import%20file", "POST", {"file": str(NETWORK_FILE)})
    network = imported["data"]["networks"][0]
    view = imported["data"]["views"][0]
    call("/commands/vizmap/apply", "POST", {"network": str(network), "styles": style["title"]})
    call("/commands/layout/force-directed", "POST", {"network": str(network)})

    edge_ids = call(f"/networks/{network}/edges")
    years = {edge_id: call(f"/networks/{network}/edges/{edge_id}")["data"]["year"]
             for edge_id in edge_ids}
    for year in YEARS:
        properties = [
            {"SUID": edge_id, "view": [{"visualProperty": "EDGE_TRANSPARENCY",
                                      "value": 180 if edge_year <= year else 0}]}
            for edge_id, edge_year in years.items()
        ]
        call(f"/networks/{network}/views/{view}/edges?bypass=true", "PUT", properties)
        call("/commands/cyanimator/capture%20frame", "POST", {"network": str(network)})
        request = Request(BASE + f"/networks/{network}/views/{view}.png")
        with urlopen(request, timeout=45) as response:
            (FRAMES / f"keyframe_{year}.png").write_bytes(response.read())
        print(year, sum(y <= year for y in years.values()), "visible edges")
    call("/commands/cyanimator/record", "POST", {"outputDir": str(FRAMES)})
    print("CyAnimator frames saved to", FRAMES)


if __name__ == "__main__":
    main()
