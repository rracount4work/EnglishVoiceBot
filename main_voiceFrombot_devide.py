import os
import uuid
import sys
import warnings
import logging
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import language_tool_python
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

# Подавляем предупреждения от pydub (SyntaxWarning)
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Настройка логирования для отладки (вывод в консоль)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ваш токен
TOKEN = "7888544972:AAFuwZoSxvkToMX_KK7P9f95wLmQqtF39Uk"

# Если ffmpeg не в PATH, можно явно указать путь:
# AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"

def split_into_chunks(text, chunk_size=4096):
    """
    Разбивает текст на части длиной не более chunk_size символов.
    """
    chunks = []
    current = ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) <= chunk_size:
            current += line
        else:
            chunks.append(current)
            current = line
    if current:
        chunks.append(current)
    return chunks

async def start(update, context):
    await update.message.reply_text(
        "Привет! Отправь мне голосовое сообщение на английском, "
        "а я объясню твои ошибки по-русски и покажу исправленный вариант."
    )

async def help_command(update, context):
    await update.message.reply_text(
        "Просто отправь голосовое сообщение на английском, "
        "я распознаю его, проверю грамматику и объясню ошибки по-русски."
    )

async def text_handler(update, context):
    user_text = update.message.text
    await update.message.reply_text(
        f"Вы отправили текст: {user_text}\n"
        "Чтобы проверить голосом, отправьте voice."
    )

async def voice_handler(update, context):
    logger.debug("Voice handler triggered.")
    voice = update.message.voice
    file_id = voice.file_id
    file = await context.bot.get_file(file_id)

    # Генерируем уникальные имена для временных файлов
    ogg_file = f"voice_{uuid.uuid4()}.ogg"
    wav_file = f"voice_{uuid.uuid4()}.wav"
    mp3_file = f"response_{uuid.uuid4()}.mp3"
    response_ogg_file = f"response_{uuid.uuid4()}.ogg"

    # Скачиваем голосовое сообщение (OGG)
    await file.download_to_drive(ogg_file)
    logger.debug(f"Downloaded voice file: {ogg_file}")

    # Конвертируем OGG -> WAV (для распознавания)
    audio = AudioSegment.from_ogg(ogg_file)
    audio.export(wav_file, format="wav")
    logger.debug(f"Converted to WAV: {wav_file}")

    # Распознавание речи (на английском)
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
    try:
        recognized_text = recognizer.recognize_google(audio_data, language="en-US")
    except sr.UnknownValueError:
        recognized_text = "Sorry, I couldn't understand your speech."
    except sr.RequestError:
        recognized_text = "Speech recognition service error."
    logger.debug(f"Recognized text: {recognized_text}")

    # Проверка грамматики через language_tool_python (на английском)
    tool = language_tool_python.LanguageTool('en-US')
    # Отключаем нежелательные правила:
    tool.disabled_rules = ["UPPERCASE_SENTENCE_START", "ENGLISH_WORD_REPEAT_RULE"]
    matches = tool.check(recognized_text)
    # Выводим для отладки, какие правила обнаружены:
    for match in matches:
        logger.debug(f"Found rule: {match.ruleId} - {match.message}")
    corrected_text = language_tool_python.utils.correct(recognized_text, matches)
    logger.debug(f"Corrected text: {corrected_text}")

    # Формируем ответ на русском, объясняем ошибки
    response_text_rus = (
        f"Вы сказали (по-английски):\n{recognized_text}\n\n"
        f"Исправленный вариант:\n{corrected_text}\n\n"
    )
    if matches:
        response_text_rus += "Ниже приведены найденные ошибки:\n"
        for match in matches:
            context_str = match.context
            replacements = ", ".join(match.replacements) if match.replacements else "нет предложений"
            rule_id = match.ruleId
            response_text_rus += (
                f"- Ошибка в фрагменте: '{context_str}'\n"
                f"  Предлагаемое исправление: {replacements}\n"
                f"  Правило: {rule_id}\n\n"
            )
    else:
        response_text_rus += "Отлично! Ошибок не обнаружено.\n"
    logger.debug(f"Response text length: {len(response_text_rus)}")
    print("Response text length:", len(response_text_rus))
    print("Full response text:")
    print(response_text_rus)

       # Преобразуем ответ в голос (TTS на русском)
    tts = gTTS(response_text_rus, lang='ru')
    tts.save(mp3_file)
    logger.debug(f"TTS saved to: {mp3_file}")

    # Конвертируем MP3 -> OGG (для отправки голосового сообщения Telegram)
    response_audio = AudioSegment.from_mp3(mp3_file)
    response_audio.export(response_ogg_file, format="ogg", codec="libopus")
    logger.debug(f"Converted response to OGG: {response_ogg_file}")

    # Отправляем голосовое сообщение-ответ
    with open(response_ogg_file, "rb") as voice_response:
        await update.message.reply_voice(voice=voice_response)
    logger.debug("Voice response sent.")

    # Отправляем текстовый ответ частями (если он длинный)
    chunks = split_into_chunks(response_text_rus, 4096)
    for i, chunk in enumerate(chunks):
        await update.message.reply_text(chunk)
        logger.debug(f"Sent text chunk {i+1}/{len(chunks)}, length: {len(chunk)}")

    # Удаляем временные файлы
    os.remove(ogg_file)
    os.remove(wav_file)
    os.remove(mp3_file)
    os.remove(response_ogg_file)
    logger.debug("Temporary files removed.")

def main():
    print("Main function started")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    logger.info("Bot started. Running polling...")
    print("Handlers added, starting polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
