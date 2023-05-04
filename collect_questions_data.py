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