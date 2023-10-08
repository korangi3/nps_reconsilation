from datetime import datetime, timedelta



today_date = str(datetime.today() - timedelta(days=1)).split()[0]
today_date = today_date.replace("-", "_")
print(today_date)