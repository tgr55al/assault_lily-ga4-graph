import sys
from pathlib import Path

from ga4.ga4_client import create_client
from ga4.country_report import fetch_country_30days
from ga4.region_japan import fetch_region_japan
from ga4.daily_activeUsers_log import update_daily_activeUsers_log
from ga4.daily_screenPageViews_log import update_daily_screenPageViews_log

from maps.world_map import main as world_map_main
from maps.japan_map import main as japan_map_main


def main():
    print("🚀 GA4 データ処理開始")

    client = create_client()

    fetch_country_30days(client)
    fetch_region_japan(client)
    update_daily_activeUsers_log(client)
    update_daily_screenPageViews_log(client)

    print("✅ GA4 データ処理完了")

    print("🌍 世界地図生成開始")
    world_map_main()

    print("🗾 日本地図生成開始")
    japan_map_main()

    print("🎉 全処理完了！")


if __name__ == "__main__":
    main()
