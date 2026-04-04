from datetime import datetime, timedelta

def get_date_range(days):
    end = datetime.now().date()
    start = end - timedelta(days=days - 1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

def get_today():
    return datetime.now().date().strftime("%Y-%m-%d")

def get_yesterday():
    return (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
