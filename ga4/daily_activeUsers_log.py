import csv
import os
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from ga4.date_utils import get_today, get_yesterday

PROPERTY_ID = "530080930"

def update_daily_activeUsers_log(client):
    print("::group::日次ログ更新")

    # 出力先フォルダ
    os.makedirs("ga4Data", exist_ok=True)
    daily_file = "ga4Data/daily_activeUsers.csv"

    today = get_today()
    yesterday = get_yesterday()

    # 今日
    request_today = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=today, end_date=today)],
    )
    response_today = client.run_report(request_today)
    today_total = sum(int(r.metric_values[0].value) for r in response_today.rows)

    # 昨日
    request_yesterday = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=yesterday, end_date=yesterday)],
    )
    response_yesterday = client.run_report(request_yesterday)
    yesterday_total = sum(int(r.metric_values[0].value) for r in response_yesterday.rows)

    # CSV 更新
    daily_activeUsers = {}

    if os.path.exists(daily_file):
        with open(daily_file, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                daily_activeUsers[row["date"]] = int(row["total_active_users"])

    daily_activeUsers[today] = today_total
    daily_activeUsers[yesterday] = yesterday_total

    with open(daily_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "total_active_users"])
        writer.writeheader()
        for d in sorted(daily_activeUsers.keys()):
            writer.writerow({"date": d, "total_active_users": daily_activeUsers[d]})

    print(f"📈 daily_activeUsers.csv を更新 → {daily_file}")
    print("::endgroup::")
