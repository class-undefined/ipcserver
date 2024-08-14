import logging
from colorama import Fore, Style, Fore, init
from typing import *

import datetime
from typing import *


class Console:
    logfile = "./ipcserver.log"

    @staticmethod
    def log(*args: List[Any], is_print=True) -> None:
        message = Console.formatted_message(Fore.GREEN, "LOG", *args)
        Console.print_and_write(message, is_print=is_print)

    @staticmethod
    def error(*args: List[Any], is_print=True) -> None:
        message = Console.formatted_message(Fore.RED, "ERROR", *args)
        Console.print_and_write(message, is_print=is_print)

    @staticmethod
    def warn(*args: List[Any], is_print=True) -> None:
        message = Console.formatted_message(Fore.YELLOW, "WARN", *args)
        Console.print_and_write(message, is_print=is_print)

    @staticmethod
    def info(*args: List[Any], is_print=True) -> None:
        message = Console.formatted_message(Fore.CYAN, "INFO", *args)
        Console.print_and_write(message, is_print=is_print)

    @staticmethod
    def formatted_message(color, level, *args: List[Any]) -> str:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = ' '.join(map(str, args))
        return f"{color}[{level}][{current_time}] {message}{Fore.RESET}"

    @staticmethod
    def print_and_write(message, is_print=True):
        if is_print:
            print(message)
        if Console.logfile:
            # 去除颜色标记
            clean_message = message[5:-5]
            with open(Console.logfile, 'a') as f:
                f.write(clean_message + '\n')


def test_console():
    Console.log("log")
    Console.info("info")
    Console.warn("warn")
    Console.error("error")
