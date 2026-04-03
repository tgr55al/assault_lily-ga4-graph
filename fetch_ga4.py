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

    # -----------------------------
    # ① 過去30日間の国別データを取得
    # -----------------------------
    end_date = datetime.now().date().strftime("%Y-%m-%d")
    start_date = (datetime.now().date() - timedelta(days=DAYS_BACK - 1)).strftime("%Y-%m-%d")
    
    # GA4 API リクエスト（dictではなく正しい型を使う）
    response_30days = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )

    response = client.run_report(response_30days)

    # 結果を CSV に保存
    with open("ga4_result.csv", "w", encoding="utf-8") as f:
        f.write("country,activeUsers\n")
        for row in response.rows:
            country = row.dimension_values[0].value
            users = row.metric_values[0].value
            f.write(f"{country},{users}\n")

    print("📊 過去30日間の国別データ → ga4_result.csv に保存")

    # -----------------------------
    # ② 今日のアクティブユーザー数だけを取得
    # -----------------------------
    today_str = datetime.now().date().strftime("%Y-%m-%d")

    request_today = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=today_str, end_date=today_str)],
    )

    response_today = client.run_report(request_today)

    today_total = sum(int(row.metric_values[0].value) for row in response_today.rows)

    print(f"📅 今日 {today_str} のアクティブユーザー数：{today_total}")

    # -----------------------------
    # ③ daily_data.csv に保存（今日の値だけ）
    # -----------------------------
    daily_file = "daily_data.csv"
    daily_data = {}

    # 既存データ読み込み
    if os.path.exists(daily_file):
        with open(daily_file, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                daily_data[row["date"]] = int(row["total_active_users"])

    # 今日の値を更新
    daily_data[today_str] = today_total

    # 日付順に書き直し
    with open(daily_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "total_active_users"])
        writer.writeheader()
        for d in sorted(daily_data.keys()):
            writer.writerow({"date": d, "total_active_users": daily_data[d]})

    print("📈 daily_data.csv を更新（今日の値を保存）")

if __name__ == "__main__":
    main()
