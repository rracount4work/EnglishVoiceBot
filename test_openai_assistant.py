import os
import openai
from dotenv import load_dotenv
import asyncio

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

ASSISTANT_ID = "asst_Kbg4tw65flbzsPegKhoiX5zt"  # <-- Твой ID ассистента

async def test_assistant():
    print(f"API ключ: {openai.api_key}")
    print(f"Проверяем ассистента: {ASSISTANT_ID}")

    # Создаём thread
    thread = openai.beta.threads.create()
    thread_id = thread.id
    print(f"Создан thread: {thread_id}")

    # Отправляем сообщение ассистенту
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="Hello! Are you working?"
    )

    # Запускаем ассистента
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    print("Ждём ответа ассистента...")

    # Проверяем статус до готовности
    while True:
        status = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if status.status == "completed":
            break
        await asyncio.sleep(1)

    # Получаем ответ ассистента
    messages = openai.beta.threads.messages.list(thread_id=thread_id)

    print("\nОтвет ассистента:")
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            print(msg.content[0].text.value)

asyncio.run(test_assistant())
