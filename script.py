import openai
import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"


SYSTEM_PROMPT = """Ты — ИИ-ассистент Айсулу для портала закупок СКК. Отвечай кратко и по делу. 
Если информации для ответа нет, говори: \"Извините, я не нашел ответа на ваш вопрос.\""""

def load_knowledge(file_path: str, max_chars: int = 4000) -> List[str]:
    """Загружает и разбивает файл знаний на фрагменты для экономии токенов"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Разбиваем на фрагменты по предложениям для сохранения смысла
    sentences = content.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        if current_length + len(sentence) < max_chars:
            current_chunk.append(sentence)
            current_length += len(sentence)
        else:
            chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentence]
            current_length = len(sentence)
    
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')
    
    return chunks

def ask_openai(user_question: str, knowledge_file: str = "knowledge.txt") -> str:
    """Запрашивает ответ у ИИ, оптимизируя использование токенов"""
    knowledge_chunks = load_knowledge(knowledge_file)
    
    # Ищем наиболее релевантный фрагмент
    best_chunk = ""
    for chunk in knowledge_chunks:
        if user_question.lower() in chunk.lower():
            best_chunk = chunk
            break
    
    # Если не нашли точного совпадения, берем первый фрагмент (можно улучшить)
    if not best_chunk and knowledge_chunks:
        best_chunk = knowledge_chunks[0]
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Контекст: {best_chunk[:3000]}\n\nВопрос: {user_question}"}
    ]
    
    response = openai.ChatCompletion.create(
        #model="gpt-4",
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.2,
        max_tokens=500  # Ограничиваем длину ответа
    )
    
    return response.choices[0].message['content']


# Пример содержимого knowledge.txt (краткая версия)
example_knowledge = """
Протокол заседания комиссии по закупкам СКК №123 от 01.06.2023. 
Присутствовали: Иванов И.И. (председатель), Петров П.П., Сидоров С.С. 
Повестка дня: 1. Рассмотрение заявок на поставку оргтехники. 
2. Утверждение технического задания на закупку мебели. 
По первому вопросу: рассмотрено 5 заявок. Лучшее предложение от ООО "ТехноПром". 
По второму вопросу: техническое задание утверждено с изменениями. 
Следующее заседание 15.06.2023. 
(Далее следует аналогичная информация на несколько страниц...)
"""

# Создаем файл knowledge.txt, если его нет
if not os.path.exists("knowledge.txt"):
    with open("knowledge.txt", "w", encoding='utf-8') as f:
        f.write(example_knowledge)



if __name__ == "main":
    question = input("Введите ваш вопрос: ")
    answer = ask_openai(question)
    print("\nОтвет:", answer)