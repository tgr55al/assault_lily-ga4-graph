import json


def build_features(rows, key_field: str, value_field: str, coords: dict, to_japanese_func):
    """GeoJSON Feature と KML Placemark を構築"""
    features = []
    placemarks = []

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
            "properties": {"name": name_ja, "value": value},
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
        })

        # KML
        placemark = f"""
            <Placemark>
                <name>{name_ja}</name>
                <value>{value}</value>
                <Point>
                    <coordinates>{lon},{lat},0</coordinates>
                </Point>
            </Placemark>
        """
        placemarks.append(placemark)

    return features, placemarks


def write_geojson(path: str, features) -> None:
    geojson = {"type": "FeatureCollection", "features": features}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)


def write_kml(path: str, placemarks, title: str) -> None:
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>{title}</name>
        {''.join(placemarks)}
    </Document>
</kml>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(kml_content)
