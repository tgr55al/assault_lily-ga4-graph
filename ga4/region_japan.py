import os
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from ga4.date_utils import get_date_range

PROPERTY_ID = "530080930"

def fetch_region_japan(client, days=30):
    print("::group::日本地域別集計")

    # 出力先フォルダ
    os.makedirs("ga4Data", exist_ok=True)
    output_path = "ga4Data/ga4_region_japan.csv"

    start_date, end_date = get_date_range(days)

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="country"),
            Dimension(name="region"),
        ],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )

    response = client.run_report(request)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("region,activeUsers\n")
        for row in response.rows:
            country = row.dimension_values[0].value
            # region を安全に取り出して前後空白を削除
            raw_region = row.dimension_values[1].value
            region = raw_region.strip() if raw_region is not None else ""

            users = row.metric_values[0].value

            # Japan かつ region が空文字でも (not set) でもない場合のみ書き出す
            if country == "Japan" and region not in ("", "(not set)"):
                f.write(f"{region},{users}\n")

    print(f"🗾 日本地域別データ → {output_path} に保存")
    print("::endgroup::")
