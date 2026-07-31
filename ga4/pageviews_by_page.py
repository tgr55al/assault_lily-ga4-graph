import json
import os
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from ga4.date_utils import get_today, get_yesterday

PROPERTY_ID = "530080930"


def normalize_path(raw_path: str) -> str:
    """
    GA4のpagePathからクエリパラメータ等を除去し、
    atwikiのページパス（例: /pages/12.html）と一致する形式に正規化する。
    """
    if raw_path is None:
        return ""
    path = raw_path.split("?", 1)[0]  # クエリパラメータを除去
    path = path.split("#", 1)[0]      # フラグメントを除去
    if len(path) > 1:
        path = path.rstrip("/")
    return path or "/"


def update_pageviews_by_page(client):
    """
    今日・昨日分の「ページ別 screenPageViews」を取得し、
    ga4Data/pageviews_by_page.json を差分更新する。

    JSON構造:
    {
      "/pages/12.html": {"2026-07-16": 120, "2026-07-17": 45},
      "/pages/13.html": {"2026-07-16": 30,  "2026-07-17": 10},
      ...
    }
    """
    print("::group::ページ別閲覧数の差分更新")

    os.makedirs("ga4Data", exist_ok=True)
    json_path = "ga4Data/pageviews_by_page.json"

    today = get_today()
    yesterday = get_yesterday()

    # 既存データ読み込み（なければ空の辞書から開始）
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            pageviews = json.load(f)
    else:
        pageviews = {}

    for target_date in (yesterday, today):
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date=target_date, end_date=target_date)],
            limit=100000,
        )
        response = client.run_report(request)

        # 同じ日付・同じ正規化パスが複数行になるケース（クエリ違い等）があるため加算する
        day_totals = {}
        for row in response.rows:
            raw_path = row.dimension_values[0].value
            path = normalize_path(raw_path)
            views = int(row.metric_values[0].value)
            day_totals[path] = day_totals.get(path, 0) + views

        for path, views in day_totals.items():
            pageviews.setdefault(path, {})[target_date] = views

    # 日付順・パス順に整形して保存
    ordered = {
        path: dict(sorted(dates.items()))
        for path, dates in sorted(pageviews.items())
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)

    print(f"📄 pageviews_by_page.json を更新 → {json_path}（{len(ordered)}ページ分）")
    print("::endgroup::")
