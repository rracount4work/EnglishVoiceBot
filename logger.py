import logging
import os
import re
import datetime

today = datetime.datetime.now().strftime("%Y-%m-%d")

# Получаем настройку логирования из .env
LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'False') == 'True'

if LOG_TO_FILE:
    def get_next_log_filename():
        log_files = [f for f in os.listdir() if re.match(rf'bot_{today}_(\d{{2}})\\.log', f)]
        if not log_files:
            return f"bot_{today}_01.log"

        numbers = sorted([int(re.search(r'_(\d{2})\\.log', f).group(1)) for f in log_files])

        for i in range(1, 100):
            if i not in numbers:
                return f"bot_{today}_{i:02}.log"

        raise Exception("Все номера логов заняты за сегодня. Удалите старые лог-файлы.")

    log_name = get_next_log_filename()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_name, mode="w", encoding="utf-8")
        ]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
