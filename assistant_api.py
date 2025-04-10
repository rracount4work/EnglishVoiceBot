import openai
import os
from dotenv import load_dotenv

# Загружаем API ключ из файла
load_dotenv(".env")
openai.api_key = os.getenv("OPENAI_API_KEY")

# ID твоего ассистента
ASSISTANT_ID = "asst_Kbg4tw65flbzsPegKhoiX5zt"

async def ask_assistant(user_message: str) -> str:
    # Создаём новую нитку диалога каждый раз
    thread = openai.beta.threads.create()
    thread_id = thread.id

    # Отправляем сообщение от пользователя
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message,
    )

    # Запускаем ассистента
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
    )

    # Ждём завершения
    while True:
        status = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        if status.status == "completed":
            break

    # Получаем ответ
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            return msg.content[0].text.value

    return "Я не получил ответ от ассистента."

# Функция сброса контекста
def reset_dialog():
    global current_thread_id
    current_thread_id = None