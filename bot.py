import pandas as pd
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater


def get_possible_columns_for_question():
    return {'cat1', 'cat2', 'cat3', 'city', 'brand', 'type', 'year'}


def get_column_name(column):
    name_dict = {'cat1': 'Category',
                 'cat2': 'First SubCategory',
                 'cat3': 'Second SubCategory',
                 'city': 'City',
                 'brand': 'Brand Name',
                 'type': 'Clothing Type',
                 'year': 'Year',
                 'price': 'Price Range'}

    if column in name_dict:
        return name_dict[column]
    return column


def get_all_options(df, conditions, column):
    all_options = [opt for opt in list(df[prepare_conditions(df, conditions)][column].unique()) if opt is not None and not pd.isna(opt)]
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


def prepare_conditions(df, conditions):
    if len(conditions) == 0:
        return df['id'] > 0

    result = df['id'] > 0
    for column, value in conditions:
        result = result & (df[column] == value)
    return result


def get_next_column(df, conditions):
    for column in get_possible_columns_for_question():
        print("get_next_column", column)
        if column not in [x for x, y in conditions]:
            if len(get_all_options(df, conditions, column)) > 0:
                return column

    return None


def get_conditions_str(conditions):
    if len(conditions) == 0:
        return ""

    res = "Current choice:\n"
    for column, value in conditions:
        res = res + "    " + get_column_name(column) + " -> " + value + "\n"

    res = res + "\n"

    return res


def start(bot, update):
    global current_column, conditions, level_dict

    do_log(update)

    current_column = 'cat1'
    level_dict = dict()
    conditions = []

    options = get_all_options(df, conditions, 'cat1')
    level_dict['cat1'] = options
    message = "In which category do you want to search?\n" + make_str_from(options)
    bot.send_message(chat_id=update.message.chat_id, text=message)


def generate_price_groups(prices):
    prices = set(prices)

    prices.remove(-1)

    min_price = min(prices)
    max_price = max(prices)

    step = (max_price - min_price) // 5
    step = step + step % 1000
    result = []

    current = min_price

    while current < max_price:
        print(current)
        result.append((current, current + step))
        current += step

    return result


def generate_prices_str(price_options):
    result = ""
    ii = 0
    # todo, convert 1000 to 1,000
    for from_price, to_price in price_options:
        result = result + "{} : from {} to {}\n".format(ii, from_price, to_price)
        ii += 1
    return result


def handle_price(bot, update, conditions):
    global price_options, current_column

    print("handle_price")

    if current_column is 'price':
        pass
    else:
        message = get_conditions_str(conditions)
        current_column = 'price'
        options = get_all_options(df, conditions, current_column)
        message = message + "There are {} products with these criteria".format(len(options)) + "\n"
        price_options = generate_price_groups(options)
        message = message + "Choose price range?\n" + generate_prices_str(price_options)
        bot.send_message(chat_id=update.message.chat_id, text=message)


def handle_text(bot, update):
    global current_column, conditions, level_dict

    print("aa CurrentState ->", current_column)
    print("aa Conditions ->", conditions)

    idx = int(update.message.text)

    if current_column is 'price':
        handle_price(bot, update, conditions)

    else:
        conditions.append((current_column, level_dict[current_column][idx]))
        next_column = get_next_column(df, conditions)

        print("nowww next_column", next_column)

        if next_column is not None and current_column is not 'price':
            current_column = next_column
            options = get_all_options(df, conditions, current_column)
            level_dict[current_column] = options
            message = get_conditions_str(conditions) + "Choose one?\n" + make_str_from(options)
            bot.send_message(chat_id=update.message.chat_id, text=message)
        else:
            print("only price remains")
            # next_column = 'price'
            # options = get_all_options(df, conditions, next_column)
            # print("only price remains " + str(len(options)))

            handle_price(bot, update, conditions)

    print("bb CurrentState ->", current_column)
    print("bb Conditions ->", conditions)


updater = Updater(token='783418650:AAGAuqiOzVC3FMFsous2Hs_a9DU8AUdy_rQ')
dispatcher = updater.dispatcher

print("Please wait, preparing the data...\n")
df = pd.read_csv('divar.csv')
print(df.columns)
print("Data is ready!\n")

current_column = 'cat1'
level_dict = dict()
conditions = []
price_options = []

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

dispatcher.add_handler(MessageHandler(Filters.text, handle_text))

updater.start_polling()
