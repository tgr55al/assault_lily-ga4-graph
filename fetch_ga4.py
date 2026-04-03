import os
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
)

# GA4 のプロパティ ID
PROPERTY_ID = "530080930"
DAYS_BACK = 30                               # 過去何日分取得するか

def main():
    # Secretsを環境変数から直接読み込み（JSONが壊れない）
    info = json.loads(os.environ["GA4_SERVICE_KEY"])

    # 認証情報を作成
    credentials = service_account.Credentials.from_service_account_info(info)
    client = BetaAnalyticsDataClient(credentials=credentials)

    # 過去30日分の日付範囲を作成
    end_date = datetime.now().date().strftime("%Y-%m-%d")
    start_date = (datetime.now().date() - timedelta(days=DAYS_BACK - 1)).strftime("%Y-%m-%d")
    
    # GA4 API リクエスト（dictではなく正しい型を使う）
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )

    response = client.run_report(request)

    # 結果を CSV に保存
    with open("ga4_result.csv", "w", encoding="utf-8") as f:
        f.write("country,activeUsers\n")
        for row in response.rows:
            country = row.dimension_values[0].value
            users = row.metric_values[0].value
            f.write(f"{country},{users}\n")

    print("GA4 data saved to ga4_result.csv")

if __name__ == "__main__":
    main()
