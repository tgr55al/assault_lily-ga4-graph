"""
ページ別閲覧数の過去データを一括取得するための単独実行スクリプト。

通常は main.py の毎時cronから update_pageviews_by_page() が呼ばれるが、
初回導入時だけはこのスクリプトで過去分をまとめて埋める。

実行方法:
  GitHub Actionsの「Run workflow」から backfill: true を指定して手動実行する。
"""
from ga4.ga4_client import create_client
from ga4.pageviews_backfill import backfill_pageviews

if __name__ == "__main__":
    client = create_client()
    backfill_pageviews(client, days=420)
