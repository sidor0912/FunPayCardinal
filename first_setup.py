"""
В данном модуле написана подпрограмма первичной настройки FunPayCardinal'а.
"""

import os
from configparser import ConfigParser
import time
from colorama import Fore, Style


default_config = {
    "FunPay": {
        "golden_key": "",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "autoRaise": "0",
        "autoResponse": "0",
        "autoDelivery": "0",
        "multiDelivery": "0",
        "autoRestore": "0",
        "autoDisable": "0",
        "oldMsgGetMode": "0"
    },
    "Telegram": {
        "enabled": "0",
        "token": "",
        "secretKey": "СекретныйПароль"
    },

    "BlockList": {
        "blockDelivery": "0",
        "blockResponse": "0",
        "blockNewMessageNotification": "0",
        "blockNewOrderNotification": "0",
        "blockCommandNotification": "0"
    },

    "NewMessageView": {
        "includeMyMessages": "1",
        "includeFPMessages": "1",
        "includeBotMessages": "0",
        "notifyOnlyMyMessages": "0",
        "notifyOnlyFPMessages": "0",
        "notifyOnlyBotMessages": "0"
    },

    "Greetings": {
        "cacheInitChats": "0",
        "ignoreSystemMessages": "0",
        "sendGreetings": "0",
        "greetingsText": "Привет, $username!"
    },

    "OrderConfirm": {
        "sendReply": "1",
        "replyText": "$username, спасибо за подтверждение заказа $order_id!\nЕсли не сложно, оставь, пожалуйста, отзыв!"
    },

    "ReviewReply": {
        "star1Reply": "0",
        "star2Reply": "0",
        "star3Reply": "0",
        "star4Reply": "0",
        "star5Reply": "0",
        "star1ReplyText": "",
        "star2ReplyText": "",
        "star3ReplyText": "",
        "star4ReplyText": "",
        "star5ReplyText": "",
    },

    "Proxy": {
        "enable": "0",
        "ip": "",
        "port": "",
        "login": "",
        "password": "",
        "check": "0"
    },

    "Other": {
        "watermark": "",
        "requestsDelay": "4",
        "language": "ru"
    }
}


def create_configs():
    if not os.path.exists("configs/auto_response.cfg"):
        with open("configs/auto_response.cfg", "w", encoding="utf-8"):
            ...

    if not os.path.exists("configs/auto_response.cfg"):
        with open("configs/auto_delivery.cfg", "w", encoding="utf-8"):
            ...


def create_config_obj(settings) -> ConfigParser:
    """
    Создает объект конфига с нужными настройками.

    :param settings: dict настроек.

    :return: объект конфига.
    """
    config = ConfigParser(delimiters=(":", ), interpolation=None)
    config.optionxform = str
    config.read_dict(settings)
    return config


def first_setup():
    config = create_config_obj(default_config)
    sleep_time = 1

    print(f"{Fore.CYAN}{Style.BRIGHT}Привет! {Fore.RED}(`-`)/{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Не могу найти основной конфиг... {Fore.RED}(-_-;). . .{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Давай ка проведем первичную настройку! {Fore.RED}°++°{Style.RESET_ALL}")
    time.sleep(sleep_time)

    while True:
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
              f"Для начала введи токен (golden_key) твоего FunPay аккаунта {Fore.RED}(._.){Style.RESET_ALL}")
        golden_key = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
        if len(golden_key) != 32:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Неверный формат токена. Попробуй еще раз! {Fore.RED}\(!!˚0˚)/{Style.RESET_ALL}")
            continue
        config.set("FunPay", "golden_key", golden_key)
        break

    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
          f"Если хочешь, ты можешь указать свой User-agent. Если ты не знаешь, что это такое, просто нажми Enter. "
          f"{Fore.RED}¯\(°_o)/¯{Style.RESET_ALL}")
    user_agent = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
    if user_agent:
        config.set("FunPay", "user_agent", user_agent)

    while True:
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
              f"Нужно ли включать Telegram бота? (1 - да / 0 - нет) {Fore.RED}(Ծ- Ծ){Style.RESET_ALL}")

        tg = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
        if tg not in ["0", "1"]:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Не понял тебя... Попробуй еще раз! {Fore.RED}\(!!˚0˚)/{Style.RESET_ALL}")
            continue
        if tg == "1":
            while True:
                print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}Введи токен Telegram-бота "
                      f" {Fore.RED}(._.){Style.RESET_ALL}")
                token = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
                if not token:
                    print(f"\n{Fore.CYAN}{Style.BRIGHT}Попробуй еще раз! {Fore.RED}\(!!˚0˚)/{Style.RESET_ALL}")
                    continue
                break

            while True:
                print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}Придумай пароль (его потребует Telegram-бот) "
                      f" {Fore.RED}ᴖ̮ ̮ᴖ{Style.RESET_ALL}")
                password = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
                if not password:
                    print(f"\n{Fore.CYAN}{Style.BRIGHT}Попробуй еще раз! {Fore.RED}\(!!˚0˚)/{Style.RESET_ALL}")
                    continue
                break

            config.set("Telegram", "enabled", "1")
            config.set("Telegram", "token", token)
            config.set("Telegram", "secretKey", password)

        break

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Готово! Сейчас я сохраню конфиг и завершу программу! "
          f"{Fore.RED}ʘ>ʘ{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}Запусти меня снова и напиши своему Telegram-боту (если ты его включил). "
          f"Все остальное ты сможешь настроить через него. {Fore.RED}ʕ•ᴥ•ʔ{Style.RESET_ALL}")
    with open("configs/_main.cfg", "w", encoding="utf-8") as f:
        config.write(f)
