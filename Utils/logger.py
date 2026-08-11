"""
В данном модуле написаны форматтеры для логгера.
"""
from colorama import Fore, Back, Style
import logging.handlers
import logging
import atexit
import queue
import re


LOG_COLORS = {
        logging.DEBUG: Fore.BLACK + Style.BRIGHT,
        logging.INFO: Fore.GREEN,
        logging.WARN: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Back.RED
}

CLI_LOG_FORMAT = f"{Fore.BLACK + Style.BRIGHT}[%(asctime)s]{Style.RESET_ALL}"\
                 f"{Fore.CYAN}>{Style.RESET_ALL} $RESET%(levelname).1s: %(message)s{Style.RESET_ALL}"
CLI_TIME_FORMAT = "%d-%m-%Y %H:%M:%S"

FILE_LOG_FORMAT = "[%(asctime)s][%(filename)s][%(lineno)d]> %(levelname).1s: %(message)s"
FILE_TIME_FORMAT = "%d.%m.%y %H:%M:%S"
CLEAR_RE = re.compile(r"(\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]))|(\n)|(\r)")


def add_colors(text: str) -> str:
    """
    Заменяет ключевые слова на коды цветов.

    $YELLOW - желтый текст.

    $CYAN - светло-голубой текст.

    $MAGENTA - фиолетовый текст.

    $BLUE - синий текст.

    :param text: текст.

    :return: цветной текст.
    """
    colors = {
        "$YELLOW": Fore.YELLOW,
        "$CYAN": Fore.CYAN,
        "$MAGENTA": Fore.MAGENTA,
        "$BLUE": Fore.BLUE,
        "$GREEN": Fore.GREEN,
        "$BLACK": Fore.BLACK,
        "$WHITE": Fore.WHITE,

        "$B_YELLOW": Back.YELLOW,
        "$B_CYAN": Back.CYAN,
        "$B_MAGENTA": Back.MAGENTA,
        "$B_BLUE": Back.BLUE,
        "$B_GREEN": Back.GREEN,
        "$B_BLACK": Back.BLACK,
        "$B_WHITE": Back.WHITE,
    }
    for c in colors:
        if c in text:
            text = text.replace(c, colors[c])
    return text


class CLILoggerFormatter(logging.Formatter):
    """
    Форматтер для вывода логов в консоль.
    """
    def __init__(self):
        super(CLILoggerFormatter, self).__init__()

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        msg = add_colors(msg)
        msg = msg.replace("$RESET", LOG_COLORS[record.levelno])
        record.msg = msg
        record.args = None
        log_format = CLI_LOG_FORMAT.replace("$RESET", Style.RESET_ALL + LOG_COLORS[record.levelno])
        formatter = logging.Formatter(log_format, CLI_TIME_FORMAT)
        return formatter.format(record)


class FileLoggerFormatter(logging.Formatter):
    """
    Форматтер для сохранения логов в файл.
    """
    def __init__(self):
        super(FileLoggerFormatter, self).__init__()

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        msg = CLEAR_RE.sub("", msg)
        record.msg = msg
        record.args = None
        formatter = logging.Formatter(FILE_LOG_FORMAT, FILE_TIME_FORMAT)
        return formatter.format(record)


LOGGER_NAMES = ["main", "FunPayAPI", "FPC", "TGBot"]
"""Логгеры, пишущие и в консоль, и в файл лога (в т.ч. дочерние, например FPC.<имя_плагина>)."""


class _QueueHandler(logging.handlers.QueueHandler):
    """
    QueueHandler, кладущий LogRecord в очередь как есть, без предварительного форматирования.

    Стандартный QueueHandler.prepare() заранее рендерит record в плоскую строку и обнуляет
    exc_info/exc_text - это сделано для multiprocessing, чтобы через очередь шли только
    picklable-данные. Очередь тут в пределах одного процесса, поэтому сериализация не нужна,
    а её побочный эффект вреден: exc_info схлопывается в record.msg одной строкой, из-за чего
    FileLoggerFormatter (вырезающий переносы строк из message) заодно съедает и переносы строк
    внутри трейсбека.
    """
    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        return record


def configure_logging() -> logging.handlers.QueueListener:
    """
    Настраивает логирование.

    Реальная запись в консоль и в файл лога выполняется не в потоке вызывающего кода, а в
    отдельном потоке-слушателе (QueueHandler/QueueListener): emit() из любого потока приложения
    лишь кладёт запись в очередь и не блокируется. Без этого все логгеры делят одни и те же
    хэндлеры с общим локом на запись - если запись в файл/консоль подвиснет (медленный диск,
    journald, антивирус и т.п.), это останавливает вообще все потоки бота, а не только логирование.

    :return: запущенный слушатель очереди логов. Останавливать вручную не обязательно - остановка
        (со сбросом накопившихся в очереди записей) зарегистрирована через atexit.
    """
    cli_handler = logging.StreamHandler()
    cli_handler.setLevel(logging.INFO)
    cli_handler.setFormatter(CLILoggerFormatter())
    # TeleBot исторически пишет только в файл лога (внутренние ошибки telebot слишком шумные для консоли).
    cli_handler.addFilter(lambda record: record.name != "TeleBot")

    file_handler = logging.handlers.RotatingFileHandler(
        filename="logs/log.log",
        maxBytes=20 * 1024 * 1024,  # 20 мегабайт в байтах
        backupCount=25,  # Сколько ротаций оставить
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(FileLoggerFormatter())

    log_queue = queue.SimpleQueue()
    queue_handler = _QueueHandler(log_queue)

    for name in LOGGER_NAMES:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(queue_handler)

    telebot_logger = logging.getLogger("TeleBot")
    telebot_logger.setLevel(logging.ERROR)
    telebot_logger.propagate = False
    telebot_logger.addHandler(queue_handler)

    listener = logging.handlers.QueueListener(log_queue, cli_handler, file_handler, respect_handler_level=True)
    listener.start()
    atexit.register(listener.stop)
    return listener
