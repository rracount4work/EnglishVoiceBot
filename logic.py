import os
import subprocess
import whisper
import warnings

from gtts import gTTS

from telegram import Update
from telegram.ext import ContextTypes

from assistant_api import ask_assistant

# Отключаем предупреждения Whisper
warnings.filterwarnings("ignore", category=UserWarning)

# Загружаем модель Whisper один раз
model = whisper.load_model("base")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = ""

    if update.message.voice:
        # Если голосовое сообщение — распознаём через Whisper
        voice = await update.message.voice.get_file()
        ogg_path = "voice.ogg"
        wav_path = "voice.wav"

        await voice.download_to_drive(ogg_path)

        #subprocess.run([
        #    "ffmpeg", "-y", "-i", ogg_path,
        #   "-ar", "16000", "-ac", "1", wav_path
        #], check=True)

        subprocess.run([
            "ffmpeg", "-y", "-i", ogg_path,
            "-ar", "16000", "-ac", "1", wav_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        result = model.transcribe(wav_path, language="en")
        user_input = result["text"]
        print(f"[Whisper] Распознано: {user_input}")

        os.remove(ogg_path)
        os.remove(wav_path)

    elif update.message.text:
        # Если текст — берём как есть
        user_input = update.message.text
        print(f"[Text] Получено сообщение: {user_input}")

    else:
        await update.message.reply_text("Пожалуйста, отправьте текст или голосовое сообщение.")
        return

    # Обработка команды сброса контекста
    if user_input.lower().strip() == "сброс":
        from assistant_api import reset_dialog
        reset_dialog()
        await update.message.reply_text("Диалог сброшен.")
        return

    # Отправляем сообщение ассистенту
    response = await ask_assistant(user_input)
    await update.message.reply_text(response)

    # Генерация голосового ответа
    tts = gTTS(response, lang="en")
    tts.save("response.mp3")

    with open("response.mp3", "rb") as audio:
        await update.message.reply_voice(audio)

    os.remove("response.mp3")
