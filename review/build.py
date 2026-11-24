"""Collect asset strips + stills into review/dist and inject the data into index.html."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from review.content import ASKS, FOOTER, GROUPS, LABELS, PHASES, SEASONS, SKIP, TIMELINE  # noqa: E402

OUT = ROOT / "assets" / "out"
DIST = ROOT / "review" / "dist"


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "sprites").mkdir(parents=True)
    (DIST / "stills").mkdir()
    assets = []
    for g in GROUPS:
        for js in sorted((OUT / g["key"]).glob("*.json")):
            m = json.loads(js.read_text())
            name = m["name"]
            if any(s in name for s in SKIP):
                continue
            # show one direction per sprite pair (the _R), except the hero bus which matters both ways
            if name.endswith("_L") and (OUT / g["key"] / f"{name[:-2]}_R.json").exists() and not name.startswith("bus_"):
                continue
            src = js.with_suffix(".png")
            dst = DIST / "sprites" / f"{g['key']}__{name}.png"
            shutil.copy(src, dst)
            assets.append({
                "group": g["key"], "name": name, "label": LABELS.get(name, ""),
                "frameW": m["frameW"], "frameH": m["frameH"], "frames": m["frames"],
                "fps": m.get("fps"), "states": m.get("states") or {}, "src": f"sprites/{dst.name}",
            })
    for s in SEASONS:
        shutil.copy(ROOT / "review" / "stills" / f"{s['key']}.png", DIST / "stills" / f"{s['key']}.png")
    data = {"seasons": SEASONS, "timeline": TIMELINE, "groups": GROUPS, "assets": assets, "phases": PHASES, "asks": ASKS, "footer": FOOTER}
    html = (ROOT / "review" / "index.html").read_text()
    inject = "<script>window.REVIEW_DATA = " + json.dumps(data, ensure_ascii=False) + ";</script>\n<script>\nconst D ="
    html = html.replace("<script>\nconst D =", inject, 1)
    (DIST / "index.html").write_text(html)
    print(f"{len(assets)} assets -> {DIST}")


if __name__ == "__main__":
    main()
