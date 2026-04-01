import csv
import os
import json

def main():
    os.makedirs("output", exist_ok=True)

    # GA4結果読み込み
    with open("ga4_result.csv", "r", encoding="utf-8") as f:
        ga4_data = list(csv.DictReader(f))

    # coords.csv読み込み（自動取得済み）
    coords = {}
    if os.path.exists("coords.csv"):
        with open("coords.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                coords[row["country"]] = (float(row["lat"]), float(row["lon"]))

    # GeoJSON作成
    features = []
    kml_points = []
    for row in ga4_data:
        country = row["country"]
        value = int(row["activeUsers"])
        if country not in coords:
            continue
        lat, lon = coords[country]

        # GeoJSON用
        features.append({
            "type": "Feature",
            "properties": {"name": country, "value": value},
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        })

        # KML用（従来通り）
        placemark = f"""
            <Placemark>
                <name>{country}</name>
                <value>{value}</value>
                <Point>
                    <coordinates>{lon},{lat},0</coordinates>
                </Point>
            </Placemark>
        """
        kml_points.append(placemark)

    # GeoJSON保存
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    with open("output/ga4_map.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    # KML保存（従来通り）
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>GA4 Active Users Map</name>
        {''.join(kml_points)}
    </Document>
</kml>"""
    with open("output/ga4_map.kml", "w", encoding="utf-8") as f:
        f.write(kml_content)

    print(f"✅ GeoJSON + KML生成完了！ {len(features)}件")

if __name__ == "__main__":
    main()
