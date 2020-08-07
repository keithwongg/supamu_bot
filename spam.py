import logging
import json
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, Bot)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

SPECIFIC, CHECK, ITERATIONS, FINAL = range(4)

def start(update, context):
    # get username and unique chat id
    user_id = update.effective_user['username']
    chat_id = update.message.chat_id
    user_details = {user_id: chat_id}
    # check for matching instances, if not, add to data storage
    with open('users_chatid.json', 'r') as jf:
        user_database = json.load(jf)
        print(user_database)
        if user_id not in user_database[0]:
            print('new user not in database')
            user_database[0][user_id] = chat_id
            with open('users_chatid.json', 'w') as jf:
                json.dump(user_database, jf)

    reply_keyboard = [['Yes', 'No']]

    words = '''Welcome to スパム bot. 
Would you like to send a private message to a specific user?

Use /stop to stop at any point'''
    update.message.reply_text(words, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SPECIFIC

def specific_message(update, context):
    choice = update.message.text
    with open('spamm_data.json', 'r') as infile:
        spamm_data = json.load(infile)
        spamm_data[0]["specific_choice"] = choice
        with open('spamm_data.json', 'w') as outfile:
            json.dump(spamm_data, outfile)

    # tree direct to either YES or NO
    if choice == "Yes":
        update.message.reply_text('''Please enter a username with the @''', reply_markup=ForceReply())
        return CHECK
    elif choice == "/stop":
        update.message.reply_text('Bye! Spamm Request Cancelled. Use /start to start Supamu again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        update.message.reply_text('Please enter the message that you would like to send', reply_markup=ForceReply())
        return ITERATIONS

def check_user(update, context):
    username_entry = update.message.text
    recepient = username_entry[1:]
    if username_entry == '/stop':
        update.message.reply_text('Bye! Spamm Request Cancelled. Use /start to start Supamu again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    with open('users_chatid.json', 'r') as jf:
        user_database = json.load(jf)
    if recepient not in user_database[0]:
        update.message.reply_text('''User has not start the bot. 
Please get the user to start the bot on their end.''')
        return ConversationHandler.END
    else:
        recepient = user_database[0][recepient]
        with open('spamm_data.json', 'r') as infile:
            spamm_data = json.load(infile)
            spamm_data[0]["recepient"] = recepient
            with open('spamm_data.json', 'w') as outfile:
                json.dump(spamm_data, outfile)

        update.message.reply_text('Please enter the message that you would like to send', reply_markup=ForceReply())
        return ITERATIONS

# def send_user(bot, update):
#     text_to_send = update.message.text
#     if CHOICE == 'Yes':
#         bot.send_message(chat_id=RECEPIENT, text=text_to_send)
#     else:
#         update.message.reply_text(text_to_send)
    

def iterations(update, context):
    message = update.message.text
    if message == '/stop':
        update.message.reply_text('Bye! Spamm Request Cancelled. Use /start to start Supamu again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    with open('spamm_data.json', 'r') as infile:
        spamm_data = json.load(infile)
        spamm_data[0]["message"] = message
        with open('spamm_data.json', 'w') as outfile:
            json.dump(spamm_data, outfile)
    update.message.reply_text('Enter a spamm number between 1-100:', reply_markup=ForceReply())
    return FINAL

def final_spam(update, context):
    with open('spamm_data.json', 'r') as infile:
        spamm_data = json.load(infile)
    # need to add some condition where if it fails then say cancel or something
    spamm_times = update.message.text
    if spamm_times == '/stop':
        update.message.reply_text('Bye! Spamm Request Cancelled. Use /start to start Supamu again.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    try:
        if int(spamm_times) > 100 or int(spamm_times) < 1:
            update.message.reply_text('Please keep the number of iterations to within 0-100')
            return ConversationHandler.END
    except ValueError:
        update.message.reply_text('Number not entered. Please enter a number between 0-100.')
        return iterations(update, context)
    try:
        if spamm_data[0]["specific_choice"] == 'Yes':
            update.message.reply_text('Message Sending... Please wait')
            for i in range(int(spamm_times)):
                context.bot.send_message(chat_id=spamm_data[0]["recepient"], text=spamm_data[0]["message"])
            update.message.reply_text('Message Sent!')
        else:
            for i in range(int(spamm_times)):
                update.message.reply_text(spamm_data[0]["message"])
        return ConversationHandler.END
    except (ValueError):
        update.message.reply_text('Please enter a number')
        return ConversationHandler.END

def stop(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! Spamm Request Cancelled. Use /start to start Supamu again.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def help_info(update, context):
    help_text = '''Ever had an instance where your freinds are still sleeping or unresponsive to your texts ?!?!?!?
FRET NO MORE!!!!
Use this bot to spamm your friends or groups to get their attention.

HAPPY SUPAMU MA FRIEND
スパム(spam in japanese)

Creator: https://github.com/keithwongg
'''
    update.message.reply_text(help_text)
    return ConversationHandler.END

def main():
    key = open('apikey.txt', 'r')
    updater = Updater(key.read(), use_context=True)

    # Dispatcher to register handlers
    dp = updater.dispatcher
    
    convo_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start),
                        CommandHandler('help', help_info)],
        states = {
            SPECIFIC: [MessageHandler(Filters.text, specific_message),
                        CommandHandler('stop', stop)],
            CHECK: [MessageHandler(Filters.text, check_user),
                        CommandHandler('stop', stop)],
            ITERATIONS:[MessageHandler(Filters.text, iterations),
                        CommandHandler('stop', stop)],
            FINAL: [MessageHandler(Filters.text, final_spam),
                        CommandHandler('stop', stop)]
                  },
        fallbacks = [CommandHandler('stop', stop)]
    )

    dp.add_handler(convo_handler)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()