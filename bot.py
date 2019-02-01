import logging
from enum import Enum

import pandas as pd
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater

updater = Updater(token='783418650:AAGAuqiOzVC3FMFsous2Hs_a9DU8AUdy_rQ')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

print("Please wait, preparing the data...\n")
df = pd.read_csv('divar.csv')
print("Data is ready!\n")


class CurrentState(Enum):
    MAIN_MENU = 0
    CAT1 = 1
    CAT2 = 2
    CAT3 = 3


def get_all_options(df, column):
    all_options = [opt for opt in list(df[column].unique()) if opt is not None]
    return all_options


def make_str_from(options):
    message = ""
    ii = 0
    for option in options:
        message = message + str(ii) + " : " + option + "\n"
        ii += 1
    return message


def read_user_choice(all_options):
    while True:
        try:
            idx = int(input("Please choose one option: "))
            if idx in range(len(all_options)):
                return idx
            else:
                print("Wrong! please type the index.")
        except:
            print("Wrong! please type the index.")


"""
while True:
    print("Which category do you want to search in?")

    all_options = get_all_options(df, 'cat1')
    print_all_options(all_options)
    idx = read_user_choice(all_options)
    print(idx)

    for option in all_options:
        print(option)
        all_cat2 = list(df[df['cat1'] == option]['cat2'].unique())

        for cat2 in all_cat2:
            print(option)
            print(cat2)
            list(df[(df['cat1'] == option) & (df['cat2'] == cat2)]['cat3'].unique())
            print()
"""


def start(bot, update):
    logging.log(level=0, msg=str(update))
    print(update)
    message = "Which category do you want to search?\n" + make_str_from(get_all_options(df, 'cat1'))
    bot.send_message(chat_id=update.message.chat_id, text=message)


def handle_text(bot, update):
    pass


current_state = CurrentState(CurrentState.MAIN_MENU)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

dispatcher.add_handler(MessageHandler(Filters.text, handle_text))

updater.start_polling()
