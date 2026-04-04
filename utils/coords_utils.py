import csv
import os
import time
import json
import urllib.request
from urllib.parse import quote


def load_coords(path: str, key_name: str) -> dict:
    """座標キャッシュを読み込む"""
    coords = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                coords[row[key_name]] = (float(row["lat"]), float(row["lon"]))
    return coords


def save_coords(path: str, key_name: str, coords: dict) -> None:
    """座標キャッシュを保存する"""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[key_name, "lat", "lon"])
        writer.writeheader()
        for key in sorted(coords.keys()):
            lat, lon = coords[key]
            writer.writerow({key_name: key, "lat": lat, "lon": lon})


def _fetch_from_nominatim(query: str) -> tuple | None:
    """Nominatim API から緯度経度を取得"""
    url = f"https://nominatim.openstreetmap.org/search?q={quote(query)}&format=json&limit=1"
    headers = {"User-Agent": "AssaultLilyGA4Map/1.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"  ⚠️ APIエラー: {query} → {e}")
    return None


def fill_missing_coords(keys, coords: dict, query_suffix: str = "", label: str = "地点") -> None:
    """不足しているキーの座標を Nominatim で補完"""
    missing = [k for k in keys if k not in coords]
    if not missing:
        return

    print(f"🔍 新しい{label} {len(missing)}件を自動取得中...")
    for key in missing:
        query = f"{key}{query_suffix}"
        print(f"   → {query} ", end="")
        latlon = _fetch_from_nominatim(query)
        if latlon:
            coords[key] = latlon
            print("✅ 取得成功")
        else:
            print("❌ 取得失敗")
        time.sleep(1.2)
