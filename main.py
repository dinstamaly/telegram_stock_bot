import requests
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, PicklePersistence,
    Job, JobQueue
)

from credentials import (
    STOCK, STOCK_API_KEY,
    STOCK_ENDPOINT, NEWS_API_KEY, COMPANY_NAME, NEWS_ENDPOINT,
    CHAT_ID, BOT_TOKEN
)


def send_notify(context: CallbackContext) -> None:
    stock_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": STOCK_API_KEY,
    }

    response = requests.get(STOCK_ENDPOINT, params=stock_params)
    data = response.json()["Time Series (Daily)"]
    data_list = [value for (key, value) in data.items()]
    yesterday_data = data_list[0]
    yesterday_closing_price = yesterday_data['4. close']
    print(yesterday_closing_price)

    day_before_yesterday_data = data_list[1]
    day_before_yesterday_closing_price = day_before_yesterday_data['4. close']
    print(day_before_yesterday_closing_price)

    difference = float(yesterday_closing_price) - \
                 float(day_before_yesterday_closing_price)

    up_down = None

    if difference > 0:
        up_down = "🔺"
    else:
        up_down = "🔻"

    print(difference)

    diff_percent = (difference / float(yesterday_closing_price)) * 100
    print(diff_percent)

    if abs(diff_percent) > 0.5:
        news_params = {
            "apiKey": NEWS_API_KEY,  # https://newsapi.org
            "qInTitle": COMPANY_NAME,
        }
        news_response = requests.get(NEWS_ENDPOINT, params=news_params)
        articles = news_response.json()["articles"]
        print(articles)
        three_articles = articles[:3]
        print(three_articles)

        formatted_articles = [
            f"{STOCK}: {up_down}{diff_percent}% " \
            f"\nHeadline: {article['title']}. \nBrief: {article['description']}"
            for article in three_articles
        ]

        for article in formatted_articles:
            context.bot.send_message(
                chat_id=CHAT_ID,
                text=article
            )


updater = Updater(
    BOT_TOKEN,
    persistence=PicklePersistence(filename='bot_data')
)
job_queue = JobQueue()
job_queue.set_dispatcher(updater.dispatcher)
job_queue.run_repeating(callback=send_notify, interval=60)
updater.start_polling()
job_queue.start()
updater.idle()
