import os
import subprocess
import whisper
import warnings
import asyncio
from gtts import gTTS
from telegram import Update
from telegram.ext import ContextTypes
from assistant_api import ask_assistant
from logger import logging

# Отключаем предупреждения Whisper
warnings.filterwarnings("ignore", category=UserWarning)

# Глобальная переменная для модели Whisper
model = None

# Асинхронная функция для загрузки модели Whisper
async def load_model_once():
    global model
    if model is None:
        print("Loading Whisper model...")
        logging.info("Loading Whisper model...")
        try:
            model = whisper.load_model("base")
            print("Whisper model loaded successfully")
            logging.info("Whisper model loaded successfully")
        except Exception as e:
            print(f"Failed to load Whisper model: {e}")
            logging.error(f"Failed to load Whisper model: {e}")
            model = None

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Processing message...")
    logging.info("Processing message...")

    # Загружаем модель Whisper, если она ещё не загружена
    await load_model_once()

    user_input = ""

    if update.message.voice:
        print("Voice message received")
        logging.info("Voice message received")
        try:
            voice = await update.message.voice.get_file()
        except Exception as e:
            print(f"Error getting voice file: {e}")
            logging.error(f"Error getting voice file: {e}")
            await update.message.reply_text("Ошибка при получении голосового файла.")
            return

        ogg_path = "voice.ogg"
        wav_path = "voice.wav"

        try:
            print(f"Downloading voice file to {ogg_path}")
            logging.info(f"Downloading voice file to {ogg_path}")
            await voice.download_to_drive(ogg_path)
            print(f"Voice file downloaded to {ogg_path}")
            logging.info(f"Voice file downloaded to {ogg_path}")

            print(f"Converting {ogg_path} to {wav_path} using ffmpeg")
            logging.info(f"Converting {ogg_path} to {wav_path} using ffmpeg")
            process = subprocess.run([
                "ffmpeg", "-y", "-i", ogg_path, "-ar", "16000", "-ac", "1", wav_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode != 0:
                raise Exception(f"ffmpeg failed with return code {process.returncode}: {process.stderr.decode()}")
            print(f"Conversion completed: {ogg_path} to {wav_path}")
            logging.info(f"Conversion completed: {ogg_path} to {wav_path}")

            print("Transcribing audio with Whisper")
            logging.info("Transcribing audio with Whisper")
            if model is None:
                raise Exception("Whisper model is not loaded")
            result = model.transcribe(wav_path, language="en")
            user_input = result.get("text", "").strip()

            if not user_input:
                await update.message.reply_text("Не удалось распознать голосовое сообщение.")
                logging.warning("Whisper не распознал текст")
                return

            print(f"[Whisper] Распознано: {user_input}")
            logging.info(f"[Whisper] Распознано: {user_input}")

        except Exception as e:
            print(f"Error processing voice message: {e}")
            logging.error(f"Error processing voice message: {e}")
            await update.message.reply_text("Ошибка при обработке голосового сообщения.")
            return
        finally:
            if os.path.exists(ogg_path):
                try:
                    os.remove(ogg_path)
                    print(f"Removed temporary file: {ogg_path}")
                    logging.info(f"Removed temporary file: {ogg_path}")
                except Exception as e:
                    print(f"Failed to remove {ogg_path}: {e}")
                    logging.error(f"Failed to remove {ogg_path}: {e}")
            if os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                    print(f"Removed temporary file: {wav_path}")
                    logging.info(f"Removed temporary file: {wav_path}")
                except Exception as e:
                    print(f"Failed to remove {wav_path}: {e}")
                    logging.error(f"Failed to remove {wav_path}: {e}")

    elif update.message.text:
        user_input = update.message.text
        print(f"[Text] Получено сообщение: {user_input}")
        logging.info(f"[Text] Получено сообщение: {user_input}")

    else:
        await update.message.reply_text("Пожалуйста, отправьте текст или голосовое сообщение.")
        return

    if user_input.lower().strip() == "сброс":
        from assistant_api import reset_dialog
        reset_dialog()
        await update.message.reply_text("Диалог сброшен.")
        return

    try:
        print("Sending request to assistant...")
        logging.info("Sending request to assistant...")
        response = await ask_assistant(user_input)
        print(f"[Assistant Response] {response}")
        logging.info(f"[Assistant Response] {response}")
    except Exception as e:
        print(f"Error getting response from assistant: {e}")
        logging.error(f"Error getting response from assistant: {e}")
        await update.message.reply_text("Ошибка при получении ответа от ассистента.")
        return

    await update.message.reply_text(response)
    print("Text response sent")
    logging.info("Text response sent")

    try:
        print("Generating voice response...")
        logging.info("Generating voice response...")
        tts = gTTS(response, lang="en")
        tts.save("response.mp3")
        print("Voice response generated")
        logging.info("Voice response generated")

        with open("response.mp3", "rb") as audio:
            await update.message.reply_voice(audio)
        print("Voice response sent")
        logging.info("Voice response sent")
    except Exception as e:
        print(f"Error generating voice response: {e}")
        logging.error(f"Error generating voice response: {e}")
        await update.message.reply_text("Ошибка при генерации голосового ответа.")
    finally:
        if os.path.exists("response.mp3"):
            try:
                # Добавляем небольшую задержку, чтобы файл успел освободиться
                await asyncio.sleep(1)
                os.remove("response.mp3")
                print("Removed temporary file: response.mp3")
                logging.info("Removed temporary file: response.mp3")
            except Exception as e:
                print(f"Failed to remove response.mp3: {e}")
                logging.error(f"Failed to remove response.mp3: {e}")