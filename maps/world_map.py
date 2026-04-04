import csv
from utils.translation_utils import load_translation_map, to_japanese
from utils.coords_utils import load_coords, save_coords, fill_missing_coords
from utils.geojson_utils import build_features, write_geojson


CONFIG = {
    "input_csv": "ga4Data/ga4_result.csv",
    "translation_csv": "master/country_map.csv",
    "coords_csv": "master/coords.csv",
    "geojson_out": "geojson/ga4_map.geojson",
    "key_field": "country",
    "value_field": "activeUsers",
    "query_suffix": "",        # 国名そのまま
    "label": "国",
}


def main():
    print("🌍 GA4 世界プロポーショナルサークル地図生成開始")

    # 翻訳表
    country_map = load_translation_map(CONFIG["translation_csv"])
    to_ja = lambda name: to_japanese(name, country_map)

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
    print(f"📊 {CONFIG['input_csv']} から {len(rows)}件の国データを読み込み")

    # 座標補完
    keys = [row[CONFIG["key_field"]] for row in rows]
    fill_missing_coords(keys, coords, CONFIG["query_suffix"], CONFIG["label"])

    # 座標キャッシュ更新
    save_coords(CONFIG["coords_csv"], CONFIG["key_field"], coords)
    print(f"✅ {CONFIG['coords_csv']} 更新完了（合計 {len(coords)}件）")

    # GeoJSON
    features = build_features(
        rows,
        key_field=CONFIG["key_field"],
        value_field=CONFIG["value_field"],
        coords=coords,
        to_japanese_func=to_ja,
    )

    write_geojson(CONFIG["geojson_out"], features)

    print(f"🎉 完了！ {len(features)}件の GeoJSON")
    print(f"   → {CONFIG['geojson_out']}")


if __name__ == "__main__":
    main()
