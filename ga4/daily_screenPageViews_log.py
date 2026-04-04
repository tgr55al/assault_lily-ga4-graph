import csv
import os
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from ga4.date_utils import get_today, get_yesterday

PROPERTY_ID = "530080930"

def update_daily_screenPageViews_log(client):
    print("::group::日次ログ更新")

    # 出力先フォルダ
    os.makedirs("ga4Data", exist_ok=True)
    daily_file = "ga4Data/daily_screenPageViews.csv"

    today = get_today()
    yesterday = get_yesterday()

    # 今日
    request_today = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=today, end_date=today)],
    )
    response_today = client.run_report(request_today)
    today_total = sum(int(r.metric_values[0].value) for r in response_today.rows)

    # 昨日
    request_yesterday = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=yesterday, end_date=yesterday)],
    )
    response_yesterday = client.run_report(request_yesterday)
    yesterday_total = sum(int(r.metric_values[0].value) for r in response_yesterday.rows)

    # CSV 更新
    daily_screenPageViews = {}

    if os.path.exists(daily_file):
        with open(daily_file, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                daily_screenPageViews[row["date"]] = int(row["total_screen_page_views"])

    daily_screenPageViews[today] = today_total
    daily_screenPageViews[yesterday] = yesterday_total

    with open(daily_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "total_screen_page_views"])
        writer.writeheader()
        for d in sorted(daily_screenPageViews.keys()):
            writer.writerow({"date": d, "total_screen_page_views": daily_screenPageViews[d]})

    print(f"📈 daily_screenPageViews.csv を更新 → {daily_file}")
    print("::endgroup::")
