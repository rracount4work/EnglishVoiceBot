import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print(f"Текущий API ключ: {os.getenv('OPENAI_API_KEY')}")

chat_completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello! Are you working?"}]
)

print("Ответ от OpenAI:")
print(chat_completion.choices[0].message.content)
