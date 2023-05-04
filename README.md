# Quizzz-bot

Бот для викторин в тг/вк.

Рабочий бот тг: https://t.me/quiziziziz_bot

Рабочий бот вк сообщество: https://vk.com/club220287431 

## Как установить

Python3 должен быть установлен. Далее загрузите ряд зависимостей с помощью pip (pip3):

    pip install -r requirements.txt

Далее создайте бота в тг. Сделать это можно у [BotFather](https://t.me/BotFather).

Создайте сообщество в вк. Разрешите писать сообщение ботам. Дальше нажмите "Разрешить сообщения" на вкладке сообщества. Напишите сообщение в сообщество.

Зарегистрируйтесь в Redis (необходимо использовать VPN). Создайте новую бд с настройками по умолчанию.

Рядом с программой создайте файл .env. Его содержимое должно быть похожим на это:

    TG_BOT_TOKEN=945605632:AAbgiIGRFGueFGesiuMzzhiufsifsif-BNk
    QUESTIONS_PATH=1vs1200.txt
    REDIS_HOST=redis-34512.g566.ap-south-1-1.ec2.cloud.redislabs.com
    REDIS_PORT=34512
    REDIS_PASSWORD=2uglVGUIDSvisdluvgSIVG
    REDIS_USERNAME=default

    VK_GROUP_TOKEN=vk1.a.riqJeTE_Qf-huFUIUSGHIudsghf_hfkjsdhviFBS:UIfjbsfsfexZPPxws6J-DSVHIfhssIUFhSIhfPDiuhS:UFUHSufh-kjscvG-IIufghiudHfIUHFUhdfLIFHUOHFhfIlhfeiuhflHlfLisuhFeuilshfilsfIUFISHUFUIOfhgosdiFGhsUIFh81i2g3igysGvhosdgyfisf


TG_BOT_TOKEN - токен бота тг, полученный у [BotFather](https://t.me/BotFather).

QUESTIONS_PATH - путь до файла с тестовыми вопросами. Используйте 1vs1200.txt (файл изи репозитория).

REDIS_HOST - адрес бд Redis. 

REDIS_PORT - порт бд Redis. Указывается после адреса через двоеточие.

REDIS_PASSWORD - пароль от бд Redis. Можно получить на странице бд. 

REDIS_USERNAME - имя пользователя бд Redis. По умолчанию default.

VK_GROUP_TOKEN - токен сообщества вк.


Запустите файл тг бота командой `python3 tg_bot.py`
Запустите файл вк бота командой `python3 vk_bot.py`
