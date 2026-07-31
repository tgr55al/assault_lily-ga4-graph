import json
import os
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from ga4.date_utils import get_today, get_yesterday

PROPERTY_ID = "530080930"

# 閲覧者数として集計しない管理系・機能系URL（前方一致で判定）
EXCLUDE_PREFIXES = [
    "/assault_lily/tag/",
    "/assault_lily/upload/",
    "/assault_lily/search/",
    "/assault_lily/renamex/",
    "/assault_lily/popular_list",
    "/assault_lily/pedit/",
    "/assault_lily/page_operate_history/",
    "/assault_lily/page_comment/",
    "/assault_lily/new",
    "/assault_lily/forum",
    "/assault_lily/editx/",
    "/assault_lily/editxx/",
    "/assault_lily/diffx/",
    "/assault_lily/copy2/",
    "/assault_lily/chmod/",
    "/assault_lily/contact",
    "/assault_lily/contributor",
    "/assault_lily/child/",
    "/assault_lily/backupx/",
    "/assault_lily/attach_backup/",
    "/assault_lily/chkind/"
]
# 末尾スラッシュの有無に関わらず判定できるよう、正規化しておく
_EXCLUDE_PREFIXES_NORMALIZED = [p.rstrip("/") for p in EXCLUDE_PREFIXES]


def is_excluded(path: str) -> bool:
    """
    集計対象外の管理系・機能系URLかどうかを判定する。
    完全一致、または「/prefix/」配下（サブパス）にも一致する。
    """
    for prefix in _EXCLUDE_PREFIXES_NORMALIZED:
        if path == prefix or path.startswith(prefix + "/"):
            return True
    return False


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
    print("::group::ページ別閲覧者数の差分更新")

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
            if is_excluded(path):
                continue
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