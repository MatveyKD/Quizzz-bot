import os

import telegram
import random
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv


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
            answer = str(' '.join(sentence.split(':')[1:]))
            questions_data[question] = answer
    return questions_data


def start(update: Update, context: CallbackContext):
    custom_keyboard = [["Новый вопрос", "Сдаться"],
                       ["Мой счёт"]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )


def answer(update: Update, context: CallbackContext):
    if update.message.text == "Новый вопрос":
        question_rnd_index = random.randint(0, len(list(QUESTIONS_DATA))-1)
        question = list(QUESTIONS_DATA.keys())[question_rnd_index]
        update.message.reply_text(question)


def main():
    updater = Updater(os.getenv("TOKEN"))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, answer))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    load_dotenv()
    QUESTIONS_DATA = collect_questions(os.getenv("QUESTIONS_PATH"))
    main()
