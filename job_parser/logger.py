import os
import sys

from loguru import logger


def setup_logging() -> None:
    """Настройка логирования.

    Функция настраивает логирование для записи в файл и вывода в консоль.
    Файл лога называется 'parser_views.json' и находится в папке 'logs'.
    Логирование в файл происходит с уровнем 'ERROR', а в консоль - с уровнем 'TRACE'.

    """
    log_filename = "parser_views.json"
    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "logs", log_filename
    )

    logger.remove()
    logger.add(
        log_path,
        format="ВРЕМЯ {time:MMMM D, YYYY > HH:mm:ss!UTC} | ТИП {level} | СООБЩЕНИЕ {message} | {extra}",
        level="ERROR",
        backtrace=False,
        diagnose=False,
        serialize=True,
    )
    logger.add(
        sys.stderr,
        colorize=True,
        format="<yellow><level>ВРЕМЯ</level> {time:MMMM D, YYYY > HH:mm:ss!UTC}</yellow>  | <fg #4eff33><level>ТИП</level> {level}</fg #4eff33> | <blue><level>СООБЩЕНИЕ</level> {message}</blue> | <fg #8bfcda>{extra}</fg #8bfcda>",
        level="TRACE",
        backtrace=False,
        diagnose=False,
    )
