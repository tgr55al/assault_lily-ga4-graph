import csv
import os
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from ga4.date_utils import get_date_range

PROPERTY_ID = "530080930"

def fetch_country_30days(client, days=30):
    print("::group::国別30日集計")

    # 出力先フォルダ
    os.makedirs("master", exist_ok=True)
    output_path = "master/country_map.csv"

    start_date, end_date = get_date_range(days)

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )

    response = client.run_report(request)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("country,activeUsers\n")
        for row in response.rows:
            country = row.dimension_values[0].value
            users = row.metric_values[0].value
            f.write(f"{country},{users}\n")

    print(f"📊 国別30日データ → {output_path} に保存")
    print("::endgroup::")
