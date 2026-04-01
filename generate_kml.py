import csv
import os
import time
import urllib.request
import json
from urllib.parse import quote

def get_coordinates(country):
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
    os.makedirs("output", exist_ok=True)
    coords_file = "coords.csv"
    coords = {}

    # 既存coords.csv読み込み
    if os.path.exists(coords_file):
        with open(coords_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                coords[row["country"]] = (float(row["lat"]), float(row["lon"]))
        print(f"✅ coords.csvから {len(coords)}件の国を読み込みました")

    # GA4結果を読み込み
    with open("ga4_result.csv", "r", encoding="utf-8") as f:
        ga4_data = list(csv.DictReader(f))
    print(f"📊 ga4_result.csv から {len(ga4_data)}件の国データを読み込みました")

    # 不足国を自動取得
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
            time.sleep(1.2)  # API制限を守る

    # coords.csvを最新化
    with open(coords_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["country", "lat", "lon"])
        writer.writeheader()
        for c in sorted(coords):
            lat, lon = coords[c]
            writer.writerow({"country": c, "lat": lat, "lon": lon})
    print(f"✅ coords.csvを更新しました（合計 {len(coords)}件）")

    # KML生成
    kml_points = []
    for row in ga4_data:
        country = row["country"]
        users = int(row["activeUsers"])
        if country not in coords:
            print(f"  ❌ Skip: {country}（座標なし）")
            continue
        lat, lon = coords[country]
        placemark = f"""
            <Placemark>
                <name>{country}</name>
                <value>{users}</value>
                <Point>
                    <coordinates>{lon},{lat},0</coordinates>
                </Point>
            </Placemark>
        """
        kml_points.append(placemark)

    print(f"📍 KMLに追加するPlacemark数: {len(kml_points)}件")

    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>GA4 Active Users Map</name>
        {''.join(kml_points)}
    </Document>
</kml>"""

    with open("output/ga4_map.kml", "w", encoding="utf-8") as f:
        f.write(kml_content)

    print(f"✅ KML生成完了！ output/ga4_map.kml に {len(kml_points)}件保存しました")

if __name__ == "__main__":
    main()
