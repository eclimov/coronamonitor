from src.Channel import Channel
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
import sys
from pytz import utc
import env

sys.path.append("../")

channel = Channel(chat_id=env.TELEGRAM_CHANNEL_CHAT_ID, bot_token=env.TELEGRAM_BOT_TOKEN)
channelDebug = Channel(chat_id=env.TELEGRAM_DEBUG_CHAT_ID, bot_token=env.TELEGRAM_BOT_TOKEN)

# https://medium.com/better-programming/introduction-to-apscheduler-86337f3bb4a6
sched = BackgroundScheduler(daemon=True, timezone=utc)  # Scheduler object


# https://api.telegram.org/bot<Bot_token>/getUpdates to get private chat id
# https://stackoverflow.com/questions/41664810/how-can-i-send-a-message-to-someone-with-my-telegram-bot-using-their-username
def listener_scheduler_error(event: JobExecutionEvent):
    channelDebug.telegram_send_text(f'ERROR\n{str(event.exception)}\n{event.traceback}')


sched.add_job(channel.telegram_send_statistics_by_countries, 'cron', hour='17', minute='55')
sched.add_job(channel.telegram_send_statistics_summary, 'cron', hour='10', minute='35')
sched.add_job(channel.telegram_send_image, 'cron', hour='8', minute='32')
# sched.add_job(channel.telegram_send_advice, 'cron', hour='10,17', minute='1')
# sched.add_job(channel.telegram_send_poll, 'cron', hour='15', minute='25')

sched.add_listener(listener_scheduler_error, EVENT_JOB_ERROR)
sched.start()

app = Flask(__name__)

if __name__ == "__main__":
    app.run()
