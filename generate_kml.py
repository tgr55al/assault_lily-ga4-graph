import csv
import os
import time
import urllib.request
import json
from urllib.parse import quote

def get_coordinates(country):
    """国名から緯度経度を自動取得（Nominatim API）"""
    url = f"https://nominatim.openstreetmap.org/search?country={quote(country)}&format=json&limit=1"
    headers = {'User-Agent': 'AssaultLilyGA4Map/1.0'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"  ⚠️ APIエラー: {country} → {e}")
    return None

def main():
    print("🚀 GA4プロポーショナルサークル地図生成開始")

    # 既存のcoords.csvを読み込み
    coords = {}
    if os.path.exists("coords.csv"):
        with open("coords.csv", "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                coords[row["country"]] = (float(row["lat"]), float(row["lon"]))
        print(f"✅ coords.csvから {len(coords)}件読み込み")

    # GA4結果を読み込み
    with open("ga4_result.csv", "r", encoding="utf-8") as f:
        ga4_data = list(csv.DictReader(f))
    print(f"📊 ga4_result.csvから {len(ga4_data)}件の国データを読み込み")

    # 不足している国の座標を自動取得
    missing = [row["country"] for row in ga4_data if row["country"] not in coords]
    if missing:
        print(f"🔍 新しい国 {len(missing)}件を自動取得中...")
        for country in missing:
            print(f"   → {country} ", end="")
            latlon = get_coordinates(country)
            if latlon:
                coords[country] = latlon
                print("✅ 取得成功")
            else:
                print("❌ 取得失敗")
            time.sleep(1.2)

    # coords.csvを最新化
    with open("coords.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["country", "lat", "lon"])
        writer.writeheader()
        for c in sorted(coords.keys()):
            lat, lon = coords[c]
            writer.writerow({"country": c, "lat": lat, "lon": lon})
    print(f"✅ coords.csv更新完了（合計 {len(coords)}件）")

    # GeoJSON + KML生成
    features = []
    kml_points = []
    for row in ga4_data:
        country = row["country"]
        value = int(row["activeUsers"])
        if country not in coords:
            print(f"  ❌ Skip: {country}（座標なし）")
            continue
        lat, lon = coords[country]

        # GeoJSON
        features.append({
            "type": "Feature",
            "properties": {"name": country, "value": value},
            "geometry": {"type": "Point", "coordinates": [lon, lat]}
        })

        # KML
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

    # ルート直下に保存（GitHub Pagesが確実に公開する場所）
    geojson = {"type": "FeatureCollection", "features": features}
    with open("ga4_map.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>GA4 Active Users Map</name>
        {''.join(kml_points)}
    </Document>
</kml>"""
    with open("ga4_map.kml", "w", encoding="utf-8") as f:
        f.write(kml_content)

    print(f"🎉 完了！ {len(features)}件のGeoJSON + KMLを生成しました")
    print("   → ga4_map.geojson（Leaflet用・ルート直下）")
    print("   → ga4_map.kml（従来用・ルート直下）")

if __name__ == "__main__":
    main()
