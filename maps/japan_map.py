import csv
from utils.translation_utils import load_translation_map, to_japanese
from utils.coords_utils import load_coords, save_coords, fill_missing_coords
from utils.geojson_kml_utils import build_features, write_geojson, write_kml


CONFIG = {
    "input_csv": "ga4Data/ga4_region_japan.csv",
    "translation_csv": "master/japan_map.csv",
    "coords_csv": "master/coords_japan.csv",
    "geojson_out": "geojson/ga4_map_japan.geojson",
    "key_field": "region",
    "value_field": "activeUsers",
    "query_suffix": ", Japan",   # 都道府県 + Japan
    "label": "都道府県",
    "kml_title": "GA4 Active Users Map (Japan)",
}


def main():
    print("🗾 GA4 日本プロポーショナルサークル地図生成開始")

    # 翻訳表
    region_map = load_translation_map(CONFIG["translation_csv"])
    to_ja = lambda name: to_japanese(name, region_map)

    # 座標キャッシュ
    coords = load_coords(CONFIG["coords_csv"], CONFIG["key_field"])
    if coords:
        print(f"✅ {CONFIG['coords_csv']} から {len(coords)}件読み込み")

    # GA4 データ
    with open(CONFIG["input_csv"], "r", encoding="utf-8") as f:
        rows = [
            row for row in csv.DictReader(f)
            if row[CONFIG["key_field"]] not in ("", "(not set)")
        ]
    print(f"📊 {CONFIG['input_csv']} から {len(rows)}件の都道府県データを読み込み")

    # 座標補完
    keys = [row[CONFIG["key_field"]] for row in rows]
    fill_missing_coords(keys, coords, CONFIG["query_suffix"], CONFIG["label"])

    # 座標キャッシュ更新
    save_coords(CONFIG["coords_csv"], CONFIG["key_field"], coords)
    print(f"✅ {CONFIG['coords_csv']} 更新完了（合計 {len(coords)}件）")

    # GeoJSON + KML
    features, placemarks = build_features(
        rows,
        key_field=CONFIG["key_field"],
        value_field=CONFIG["value_field"],
        coords=coords,
        to_japanese_func=to_ja,
    )

    write_geojson(CONFIG["geojson_out"], features)

    print(f"🎉 完了！ {len(features)}件の GeoJSON + KML を生成しました")
    print(f"   → {CONFIG['geojson_out']}")


if __name__ == "__main__":
    main()
