from src.Channel import Channel
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import sys
from pytz import utc

sys.path.append("../")

channel = Channel()
# https://medium.com/better-programming/introduction-to-apscheduler-86337f3bb4a6
sched = BackgroundScheduler(daemon=True, timezone=utc)  # Scheduler object

sched.add_job(channel.telegram_send_advice, 'cron', hour='5-20/5', minute='1')
sched.add_job(channel.telegram_send_image, 'cron', hour='6-21/6', minute='32')
sched.add_job(channel.telegram_send_poll, 'cron', hour='16', minute='25')
sched.add_job(channel.telegram_send_statistics_summary, 'cron', hour='12', minute='35')
sched.add_job(channel.telegram_send_statistics_by_countries, 'cron', hour='6,20', minute='57')
sched.start()

app = Flask(__name__)

if __name__ == "__main__":
    app.run()
