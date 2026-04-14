import json
from pathlib import Path

def build_features(rows, key_field: str, value_field: str, coords: dict, to_japanese_func):
    """GeoJSON Feature を構築"""
    features = []

    for row in rows:
        key = row[key_field]
        value = int(row[value_field])

        if key not in coords:
            print(f"  ❌ Skip: {key}（座標なし）")
            continue

        lat, lon = coords[key]
        name_ja = to_japanese_func(key)

        # GeoJSON
        features.append({
            "type": "Feature",
            "properties": {"name": f"{name_ja} ({key})", "value": value},
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
        })

    return features


def write_geojson(path: str, features) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    geojson = {"type": "FeatureCollection", "features": features}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
