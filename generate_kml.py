import csv
import os
import time
import urllib.request
import json
from urllib.parse import quote

def get_coordinates(country):
    """Nominatim APIで国名から緯度経度を取得（無料・自動）"""
    url = f"https://nominatim.openstreetmap.org/search?country={quote(country)}&format=json&limit=1"
    headers = {'User-Agent': 'AssaultLilyGA4Map/1.0 (contact: your-email@example.com)'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data and 'lat' in data[0] and 'lon' in data[0]:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"⚠️ 座標取得失敗: {country} ({e})")
    return None

def main():
    os.makedirs("output", exist_ok=True)
    coords_file = "coords.csv"
    coords = {}

    # 既存のcoords.csvを読み込み
    if os.path.exists(coords_file):
        with open(coords_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                coords[row["country"]] = (float(row["lat"]), float(row["lon"]))

    # GA4結果を読み込み、不足している国を検出
    missing = []
    with open("ga4_result.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ga4_data = list(reader)  # 後でKML生成に使う

    for row in ga4_data:
        country = row["country"]
        if country not in coords:
            missing.append(country)

    # 不足分を自動取得
    if missing:
        print(f"🔍 新しい国を{len(missing)}件自動取得中...")
        for country in missing:
            print(f"   → {country}")
            latlon = get_coordinates(country)
            if latlon:
                coords[country] = latlon
            time.sleep(1.2)  # Nominatimのレート制限を守る

    # coords.csvを最新版で上書き保存
    with open(coords_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["country", "lat", "lon"])
        writer.writeheader()
        for country in sorted(coords.keys()):
            lat, lon = coords[country]
            writer.writerow({"country": country, "lat": lat, "lon": lon})

    # KML生成（以前と同じ）
    kml_points = []
    for row in ga4_data:
        country = row["country"]
        users = int(row["activeUsers"])
        if country not in coords:
            print(f"Skip: {country} (座標取得失敗)")
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

    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>GA4 Active Users Map</name>
        {''.join(kml_points)}
    </Document>
</kml>"""

    with open("output/ga4_map.kml", "w", encoding="utf-8") as f:
        f.write(kml_content)

    print(f"✅ KML生成完了！ {len(kml_points)}件の国を保存しました（coords.csvも自動更新済み）")

if __name__ == "__main__":
    main()
