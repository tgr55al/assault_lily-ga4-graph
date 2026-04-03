import os
import json
from datetime import datetime, timedelta, date
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
    # Secrets を環境変数から読み込み
    info = json.loads(os.environ["GA4_SERVICE_KEY"])

    # 認証情報を作成
    credentials = service_account.Credentials.from_service_account_info(info)
    client = BetaAnalyticsDataClient(credentials=credentials)

    # 過去30日分の日付範囲を作成
    end_date = datetime.now().date().strftime("%Y-%m-%d")
    start_date = (datetime.now().date() - timedelta(days=DAYS_BACK - 1)).strftime("%Y-%m-%d")

    # GA4 API リクエスト
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="country"),  # 国
            Dimension(name="region"),   # 地域（都道府県）
        ],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )

    response = client.run_report(request)

    # 日本の地域だけ CSV に保存
    with open("ga4_region_japan.csv", "w", encoding="utf-8") as f:
        f.write("region,activeUsers\n")
        for row in response.rows:
            country = row.dimension_values[0].value
            region = row.dimension_values[1].value
            users = row.metric_values[0].value

            # 日本だけに絞る
            if country == "Japan":
                f.write(f"{region},{users}\n")

    print("Japan region data saved to ga4_region_japan.csv")

if __name__ == "__main__":
    main()
