import random
import os
from dotenv import load_dotenv

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from collect_questions_data import collect_questions

import redis


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


def echo(event, vk_api):
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')

    keyboard.add_line()
    keyboard.add_button('Мой счёт')

    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def main():
    load_dotenv()
    r = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        password=os.getenv("REDIS_PASSWORD"),
        username=os.getenv("REDIS_USERNAME")
    )

    questions_data = collect_questions(os.getenv("QUESTIONS_PATH"))

    vk_session = vk.VkApi(token=os.getenv("VK_GROUP_TOKEN"))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')

    keyboard.add_line()
    keyboard.add_button('Мой счёт')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            question = r.get(event.user_id).decode()
            if not question:
                user_id = event.user_id
                user_get = vk_session.method("users.get", {"user_ids": user_id})[0]
                question_rnd_index = random.randint(0, len(list(questions_data)) - 1)
                question = list(questions_data.keys())[question_rnd_index]
                r.set(question, event.user_id)
                vk_api.messages.send(
                    user_id=event.user_id,
                    message=fr'Здравствуйте, {user_get["first_name"]} {user_get["last_name"]}! Для нового вопроса нажмите кнопку "Новый Вопрос".',
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(1, 1000)
                )
            else:
                answer = questions_data[question]
                if event.text == "Новый вопрос":
                    question_rnd_index = random.randint(0, len(list(questions_data)) - 1)
                    question = list(questions_data.keys())[question_rnd_index]
                    r.set(str(event.user_id), str(question))
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message=question,
                        keyboard=keyboard.get_keyboard(),
                        random_id=random.randint(1, 1000)
                    )
                elif event.text == 'Сдаться':
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message="Правильный ответ: {}. Для следующего вопроса нажмите 'Новый вопрос'".format(
                            questions_data[question]
                        ),
                        keyboard=keyboard.get_keyboard(),
                        random_id=random.randint(1, 1000)
                    )
                elif event.text == "Мой счёт":
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message="Функция находится в разработке",
                        keyboard=keyboard.get_keyboard(),
                        random_id=random.randint(1, 1000)
                    )
                elif event.text == answer:
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message="Правильно! Поздравляю! Для следующего вопроса нажмите «Новый вопрос».",
                        keyboard=keyboard.get_keyboard(),
                        random_id=random.randint(1, 1000)
                    )
                else:
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message="Неправильно… Попробуешь ещё раз?",
                        keyboard=keyboard.get_keyboard(),
                        random_id=random.randint(1, 1000)
                    )


if __name__ == "__main__":
    main()
