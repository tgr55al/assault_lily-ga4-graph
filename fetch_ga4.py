from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
import json

# GA4 のプロパティ ID（例：123456789）
PROPERTY_ID = "530080930"

def main():
    # サービスアカウントキーを読み込み
    with open("service_account.json", "r") as f:
        info = json.load(f)

    client = BetaAnalyticsDataClient.from_service_account_info(info)

    # GA4 API のリクエスト
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[{"name": "country"}],
        metrics=[{"name": "activeUsers"}],
        date_ranges=[{"start_date": "7daysAgo", "end_date": "today"}],
    )

    response = client.run_report(request)

    # 結果を CSV に保存（後で KML 生成に使う）
    with open("ga4_result.csv", "w", encoding="utf-8") as f:
        f.write("country,activeUsers\n")
        for row in response.rows:
            f.write(f"{row.dimension_values[0].value},{row.metric_values[0].value}\n")

    print("GA4 data saved to ga4_result.csv")

if __name__ == "__main__":
    main()
