import random
import os
from dotenv import load_dotenv

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard

from collect_questions_data import collect_questions

import redis


def start_dialog(event, questions_data, r, keyboard, vk_session):
    user_id = event.user_id
    user_get = vk_session.method("users.get", {"user_ids": user_id})[0]
    question_rnd_index = random.randint(0, len(list(questions_data)) - 1)
    question = list(questions_data.keys())[question_rnd_index]
    r.set(event.user_id, question)
    vk_session.get_api().messages.send(
        user_id=event.user_id,
        message=fr'Здравствуйте, {user_get["first_name"]} {user_get["last_name"]}! Для нового вопроса нажмите кнопку "Новый Вопрос".',
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def send_new_question(event, r, questions_data, keyboard, vk_api):
    question_rnd_index = random.randint(0, len(list(questions_data)) - 1)
    question = list(questions_data.keys())[question_rnd_index]
    r.set(str(event.user_id), str(question))
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
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
            question = r.get(event.user_id)
            if not question:
                start_dialog(event, questions_data, r, keyboard, vk_session)
            else:
                answer = questions_data[question.decode()]
                if event.text == "Новый вопрос":
                    send_new_question(event, r, questions_data, keyboard, vk_api)
                elif event.text == 'Сдаться':
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message="Правильный ответ: {}. Для следующего вопроса нажмите 'Новый вопрос'".format(
                            answer
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
