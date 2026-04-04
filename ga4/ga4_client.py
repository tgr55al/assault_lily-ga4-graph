import os
import json
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient

def create_client():
    info = json.loads(os.environ["GA4_SERVICE_KEY"])
    credentials = service_account.Credentials.from_service_account_info(info)
    return BetaAnalyticsDataClient(credentials=credentials)
