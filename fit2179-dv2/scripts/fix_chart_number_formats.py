import json
import glob
import os
from pathlib import Path

CHARTS = Path(__file__).resolve().parent.parent / "charts"


def fix_formats(obj):
    if isinstance(obj, dict):
        fmt = obj.get("format")
        if fmt == ",":
            obj["format"] = ",d"
        if fmt == ",d" and obj.get("title") == "Persons (thousands)":
            obj["format"] = ",.0f"
        for value in obj.values():
            fix_formats(value)
    elif isinstance(obj, list):
        for item in obj:
            fix_formats(item)


for path in sorted(CHARTS.glob("*.json")):
    spec = json.loads(path.read_text(encoding="utf-8"))
    config = spec.setdefault("config", {})
    config["axisQuantitative"] = {"format": ",d"}
    legend = config.setdefault("legend", {})
    legend["format"] = ",d"
    fix_formats(spec)
    path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated {path.name}")
