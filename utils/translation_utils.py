import csv

def load_translation_map(path: str) -> dict:
    """英語→日本語の変換表を読み込む"""
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mapping[row["english"]] = row["japanese"]
    return mapping


def to_japanese(name: str, mapping: dict) -> str:
    """英語名を日本語に変換（未登録はそのまま）"""
    return mapping.get(name, name)
