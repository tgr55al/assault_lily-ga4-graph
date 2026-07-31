import json
import os
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from ga4.pageviews_by_page import normalize_path

PROPERTY_ID = "530080930"

# 1回のAPI呼び出しで取得する最大行数（GA4 Data APIの上限は1リクエスト最大100,000行）
PAGE_SIZE = 100000


def backfill_pageviews(client, days=420):
    """
    GA4の保持期間内（プロパティ設定にもよるが最大14ヶ月＝約420日）の
    「ページ×日付」ごとのscreenPageViewsをすべて取得し、
    ga4Data/pageviews_by_page.json を作り直す。

    ※ 通常運用（毎時cron）では使わない。
       初回導入時、またはGA4のデータ保持期間設定を変更した直後などに
       手動（workflow_dispatchのbackfill入力）で実行する。

    注意:
      GA4の「データ保持」設定（管理 > データ設定 > データ保持）が
      デフォルトの2ヶ月のままだと、過去2ヶ月分しか遡れない。
      できるだけ長期のグラフを出したいなら、事前に14ヶ月に変更しておくこと。
      （それでも「開設からの全期間」は取得不可。GA4はイベントデータの保持上限がある）
    """
    print(f"::group::ページ別閲覧数バックフィル（過去{days}日分）")

    os.makedirs("ga4Data", exist_ok=True)
    json_path = "ga4Data/pageviews_by_page.json"

    pageviews = {}
    offset = 0

    while True:
        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[Dimension(name="pagePath"), Dimension(name="date")],
            metrics=[Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
            limit=PAGE_SIZE,
            offset=offset,
        )
        response = client.run_report(request)

        for row in response.rows:
            raw_path = row.dimension_values[0].value
            raw_date = row.dimension_values[1].value  # 形式: YYYYMMDD
            path = normalize_path(raw_path)
            date = f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
            views = int(row.metric_values[0].value)

            pageviews.setdefault(path, {})
            pageviews[path][date] = pageviews[path].get(date, 0) + views

        fetched = len(response.rows)
        print(f"  取得 {offset + 1}〜{offset + fetched} 行目")

        if fetched < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    ordered = {
        path: dict(sorted(dates.items()))
        for path, dates in sorted(pageviews.items())
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)

    print(f"📄 バックフィル完了 → {json_path}（{len(ordered)}ページ分）")
    print("::endgroup::")
