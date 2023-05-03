import os

import telegram
import random
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, Filters, filters, CallbackContext, ConversationHandler
from dotenv import load_dotenv

import redis


NEW_QUESTION, USER_ANSWER = range(2)


def collect_questions(questions_file_path):
    with open(questions_file_path, 'r', encoding='KOI8-R') as file:
        file_content = file.read()
    splited_file = file_content.split('\n\n')[3:]
    questions_data = dict()
    question = ""
    for part in splited_file:
        sentence = (part.replace('\n', '', 1)).replace('\n', ' ')
        if sentence.startswith('Вопрос'):
            question = ' '.join(sentence.split(':')[1:])
        elif sentence.startswith('Ответ'):
            answer = str(' '.join(sentence.split(':')[1:])).split("(")[0].split(".")[0]
            questions_data[question] = answer
    return questions_data


def start(update: Update, context: CallbackContext):
    custom_keyboard = [["Новый вопрос", "Сдаться"],
                       ["Мой счёт"]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте, {user.mention_markdown_v2()}\! Для нового вопроса нажмите кнопку "Новый Вопрос"\.',
        reply_markup=reply_markup,
    )
    return NEW_QUESTION


def handle_new_question_request(update: Update, context: CallbackContext):
    question_rnd_index = random.randint(0, len(list(context.bot_data["questions_data"])) - 1)
    question = list(context.bot_data["questions_data"].keys())[question_rnd_index]
    update.message.reply_text(question)
    context.bot_data["redis"].set(str(update.message.chat_id), str(question))
    return USER_ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext):
    if context.bot_data["questions_data"][context.bot_data["redis"].get(str(update.message.chat_id)).decode()] in update.message.text:
        update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос».")
        return NEW_QUESTION
    else:
        update.message.reply_text("Неправильно… Попробуешь ещё раз?")
        return USER_ANSWER


def cancel(update):
    update.message.reply_text('Вы отменили действие.')

    return ConversationHandler.END


def main():
    load_dotenv()

    r = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        password=os.getenv("REDIS_PASSWORD"),
        username=os.getenv("REDIS_USERNAME")
    )

    questions_data = collect_questions(os.getenv("QUESTIONS_PATH"))

    updater = Updater(os.getenv("TOKEN"))

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NEW_QUESTION: [MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request)],

            USER_ANSWER: [MessageHandler(Filters.text, handle_solution_attempt)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    dispatcher.bot_data["redis"] = r
    dispatcher.bot_data["questions_data"] = questions_data

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
