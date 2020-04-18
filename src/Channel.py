import requests
import random
import json
from telegram.bot import Bot
from os import listdir
from os.path import isfile, join
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def format_statistics(today_cases, cases, deaths, recovered):
    return f'```\nСегодня:       {today_cases:,}\nВсего:         {cases:,}\nСмертей:       {deaths:,}\nВыздоровлений: {recovered:,}```'


class Channel:
    def __init__(self, chat_id, bot_token):
        self.__advices = [
            'Регулярно обрабатывайте руки спиртосодержащим средством или мойте их с мылом',
            'Держитесь от людей на расстоянии как минимум 1 метра, особенно если у них кашель, насморк и повышенная температура',
            'По возможности, не трогайте руками глаза, нос и рот',
            'При кашле и чихании прикрывайте рот и нос салфеткой или сгибом локтя; сразу выкидывайте салфетку в контейнер для мусора с крышкой и обрабатывайте руки спиртосодержащим антисептиком или мойте их водой с мылом',
            'При повышении температуры, появлении кашля и затруднении дыхания как можно быстрее обращайтесь за медицинской помощью',
            'Следите за новейшей информацией и выполняйте рекомендации медицинских специалистов',
            'Если вы испытываете чувство грусти, стресса, замешательства, страха или досады в кризисной ситуации — это нормально',
            'Если вам приходится оставаться дома, не забывайте о здоровом образе жизни: правильном питании, режиме сна, физических упражнениях и общении с близкими дома, либо по электронной почте или телефону с родственниками и друзьями',
            'Не курите и не употребляйте алкоголь или другие психоактивные вещества, чтобы подавить свои эмоции',
            'Если вас или членов вашей семьи беспокоят и тревожат репортажи в СМИ, уделяйте меньше времени их просмотру или прослушиванию'
        ]
        self.__chat_id = chat_id
        self.__bot = Bot(token=bot_token)

    def telegram_send_advice(self):
        result = self.__bot.send_message(
            chat_id=self.__chat_id,
            text=random.choice(self.__advices)
        )
        print(result)

    def telegram_send_text(self, text):
        result = self.__bot.send_message(
            chat_id=self.__chat_id,
            text=text
        )
        print(result)

    def telegram_send_image(self):
        images_path = 'assets'  # DO NOT CHANGE THIS PATH ON LINUX(PROD)
        images = [f for f in listdir(images_path) if isfile(join(images_path, f))]

        button_menu = build_menu(
            buttons=[
                InlineKeyboardButton(
                    'Источник',
                    url='https://www.who.int/ru/emergencies/diseases/novel-coronavirus-2019/advice-for-public'
                )
            ],
            n_cols=1
        )

        result = self.__bot.send_photo(
            chat_id=self.__chat_id,
            # caption='Совет',
            photo=open(f'{images_path}/{random.choice(images)}', 'rb'),
            reply_markup=InlineKeyboardMarkup(button_menu)
        )
        print(result)

    def telegram_send_statistics_summary(self):
        endpoint = 'https://corona.lmao.ninja/v2/all'
        r = requests.get(endpoint)
        if str(r.status_code) == '200':
            response = json.loads(r.content.decode("utf-8"))  # Decode byte literal and convert to Json object
            result = self.__bot.send_message(
                chat_id=self.__chat_id,
                parse_mode='Markdown',
                text='#StatsOverall\n' + format_statistics(response["todayCases"], response["cases"], response["deaths"], response["recovered"])
            )
            print(result)
        else:
            raise Exception(f'{endpoint} => code {r.status_code}')

    def telegram_send_statistics_by_countries(self):
        # TODO: use yestarday's data (https://corona.lmao.ninja/v2/countries/Moldova?yesterday=true) and compare 'todayCases' values
        endpoint = 'https://corona.lmao.ninja/v2/countries'
        r = requests.get(endpoint)
        if str(r.status_code) == '200':
            response_list = json.loads(r.content.decode("utf-8"))  # Decode byte literal and convert to Json object
            countries_data = [
                {'name': 'Молдова', 'data': next((item for item in response_list if item["country"] == "Moldova"), None)},
                {'name': 'Италия', 'data': next((item for item in response_list if item["country"] == "Italy"), None)},
                {'name': 'Украина', 'data': next((item for item in response_list if item["country"] == "Ukraine"), None)},
                {'name': 'Румыния', 'data': next((item for item in response_list if item["country"] == "Romania"), None)},
                {'name': 'Россия', 'data': next((item for item in response_list if item["country"] == "Russia"), None)}
            ]

            response_list_sorted_by_cases = sorted(response_list, key=lambda k: k['cases'])
            cases_country_least = response_list_sorted_by_cases[0]
            cases_country_most = response_list_sorted_by_cases[len(response_list_sorted_by_cases) - 1]

            countries_data_formatted_list = [f'*{country_data["name"]}*\n{format_statistics(country_data["data"]["todayCases"], country_data["data"]["cases"], country_data["data"]["deaths"], country_data["data"]["recovered"])}' for country_data in countries_data]
            countries_data_formatted_list.append(
                f'Минимум случаев: {cases_country_least["country"]} - {cases_country_least["cases"]}\nМаксимум случаев: {cases_country_most["country"]} - {cases_country_most["cases"]}'
            )
            result = self.__bot.send_message(
                chat_id=self.__chat_id,
                parse_mode='Markdown',
                text='#StatsByCountry\n' + '\n\n'.join(countries_data_formatted_list)
            )
            print(result)
        else:
            raise Exception(f'{endpoint} => code {r.status_code}')

    # TODO: def telegram_send_news(self):

    def telegram_send_poll(self):
        polls = [
            {
                'question': 'Ощущаете ли вы симптомы коронавируса?',
                'options': [
                    'Боль при глотании, чихании',
                    'Головная боль',
                    'Кашель',
                    'Повышение температуры',
                    'Озноб',
                    'Мышечная боль',
                    'Несколько из вышеперечисленных',
                    'Ни один из вышеперечисленных',
                ]
            },
            {
                'question': 'Есть ли среди ваших родственников люди недавно вернувшиеся из-за границы?',
                'options': [
                    'Да',
                    'Нет',
                    'Не знаю',
                ]
            },
            {
                'question': 'Есть ли среди ваших знакомых люди переболевшие коронавирусом?',
                'options': [
                    'Да',
                    'Нет',
                ]
            },
            {
                'question': 'Соблюдаете ли вы карантин?',
                'options': [
                    'Не работаю и не выхожу из дома без надобности',
                    'Работаю из дома',
                    'Хожу/езжу на работу, как и раньше, но соблюдаю осторожность',
                    'Веду прежний образ жизни и ни в чём себя не ограничиваю',
                ]
            },
        ]

        poll = random.choice(polls)
        result = self.__bot.send_poll(
            chat_id=self.__chat_id,
            question=poll['question'],
            options=poll['options']
        )
        print(result)
