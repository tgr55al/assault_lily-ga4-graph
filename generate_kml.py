import csv

# 国名 → 緯度経度の簡易マップ（必要に応じて追加可能）
COUNTRY_COORDS = {
    "Japan": (36.2048, 138.2529),
    "United States": (37.0902, -95.7129),
    "India": (20.5937, 78.9629),
    "Germany": (51.1657, 10.4515),
    "France": (46.2276, 2.2137),
    "United Kingdom": (55.3781, -3.4360),
    "Canada": (56.1304, -106.3468),
    "Australia": (-25.2744, 133.7751),
    "Brazil": (-14.2350, -51.9253),
    "Indonesia": (-0.7893, 113.9213),
    # 必要に応じて追加
}

def main():
    os.makedirs("output", exist_ok=True)

    kml_points = []

    # GA4 の結果を読み込む
    with open("ga4_result.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row["country"]
            users = row["activeUsers"]

            if country not in COUNTRY_COORDS:
                print(f"Skip: {country} (座標未登録)")
                continue

            lat, lon = COUNTRY_COORDS[country]

            # KML の Placemark を作成
            placemark = f"""
            <Placemark>
                <name>{country} ({users})</name>
                <Point>
                    <coordinates>{lon},{lat},0</coordinates>
                </Point>
            </Placemark>
            """
            kml_points.append(placemark)

    # KML 全体を生成
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <name>GA4 Active Users Map</name>
        {''.join(kml_points)}
    </Document>
    </kml>
    """

    # ファイルに保存
    with open("ga4_map.kml", "w", encoding="utf-8") as f:
        f.write(kml_content)

    print("KML saved to ga4_map.kml")

if __name__ == "__main__":
    main()
