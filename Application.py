from Channel import Channel
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import sys
from pytz import utc

sys.path.append("../")

sched = BackgroundScheduler(timezone=utc)  # Scheduler object
sched.start()

channel = Channel()
sched = BackgroundScheduler(daemon=True)
sched.add_job(channel.telegram_send_advice, 'interval', minutes=62)
sched.add_job(channel.telegram_send_poll, 'interval', minutes=249)
sched.add_job(channel.telegram_send_image, 'interval', minutes=85)
sched.add_job(channel.telegram_send_statistics_summary, 'interval', minutes=720)
sched.add_job(channel.telegram_send_statistics_by_countries, 'interval', minutes=1440)
sched.start()

app = Flask(__name__)

if __name__ == "__main__":
    app.run()
