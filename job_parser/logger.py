import sys
from loguru import logger


def setup_logging():
    logger.remove()
    logger.add(
        "logs/parser_views.log",
        format="ВРЕМЯ: {time:MMMM D, YYYY > HH:mm:ss!UTC} | ТИП: {level} | СООБЩЕНИЕ: {message} | {extra}",
        level="ERROR",
        backtrace=False,
        diagnose=False,
        serialize=True,
    )
    logger.add(
        sys.stderr,
        colorize=True,
        format="<yellow><level>ВРЕМЯ:</level>: {time:MMMM D, YYYY > HH:mm:ss!UTC}</yellow>  | <fg #4eff33><level>ТИП:</level>: {level}</fg #4eff33> | <blue><level>СООБЩЕНИЕ:</level> {message}</blue> | <fg #8bfcda>{extra}</fg #8bfcda>",
        level="TRACE",
        backtrace=False,
        diagnose=False,
    )
