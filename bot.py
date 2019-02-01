from enum import Enum

import pandas as pd
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater


class CurrentState(Enum):
    CAT1 = 1
    CAT2 = 2
    CAT3 = 3


def get_all_options(df, column):
    all_options = [opt for opt in list(df[column].unique()) if opt is not None]
    return all_options


def make_str_from(options):
    options = [opt for opt in options if opt is not None and not pd.isna(opt)]

    print("make_str_from", options)
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


def do_log(update):
    logging = open("log_file.txt", "a")
    logging.write(str(update) + "\n")
    logging.close()


def start(bot, update):
    global current_state, cat1, conditions

    do_log(update)
    conditions = []
    cat1 = get_all_options(df, 'cat1')
    message = "Which category do you want to search?\n" + make_str_from(cat1)
    bot.send_message(chat_id=update.message.chat_id, text=message)

    current_state = CurrentState.CAT1


def prepare_conditions(df, conditions):
    if len(conditions) == 0:
        return df['id'] > 0

    result = df['id'] > 0
    for column, value in conditions:
        result = result & (df[column] == value)
    return result


def handle_text(bot, update):
    global current_state, cat1, cat2, cat3, conditions

    print("CurrentState ->", current_state)
    print("Conditions ->", conditions)

    if current_state == CurrentState.CAT1:
        idx = int(update.message.text)
        conditions.append(('cat1', cat1[idx]))
        cat2 = list(df[prepare_conditions(df, conditions)]['cat2'].unique())
        message = "Choose one?\n" + make_str_from(cat2)
        bot.send_message(chat_id=update.message.chat_id, text=message)

        current_state = CurrentState.CAT2

    elif current_state == CurrentState.CAT2:
        idx = int(update.message.text)
        conditions.append(('cat2', cat2[idx]))
        cat3 = list(df[prepare_conditions(df, conditions)]['cat3'].unique())
        message = "Choose one?\n" + make_str_from(cat3)
        bot.send_message(chat_id=update.message.chat_id, text=message)

        current_state = CurrentState.CAT3

    elif current_state == CurrentState.CAT3:

        idx = int(update.message.text)
        conditions.append(('cat3', cat3[idx]))
        message = "There are {} options".format(len(df[prepare_conditions(df, conditions)]))
        bot.send_message(chat_id=update.message.chat_id, text=message)

        print("Conditions ->", conditions)

    print("CurrentState ->", current_state)
    print("Conditions ->", conditions)


updater = Updater(token='783418650:AAGAuqiOzVC3FMFsous2Hs_a9DU8AUdy_rQ')
dispatcher = updater.dispatcher

print("Please wait, preparing the data...\n")
df = pd.read_csv('divar.csv')
print(df.columns)
print("Data is ready!\n")

current_state = CurrentState(CurrentState.CAT1)
cat1 = []
cat2 = []
cat3 = []
conditions = []

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

dispatcher.add_handler(MessageHandler(Filters.text, handle_text))

updater.start_polling()
