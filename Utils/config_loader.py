"""
В данном модуле написаны функции для валидации конфигов.
"""
import configparser
from configparser import ConfigParser, SectionProxy
import codecs
import os

from Utils.exceptions import (ParamNotFoundError, EmptyValueError, ValueNotValidError, SectionNotFoundError,
                              ConfigParseError, ProductsFileNotFoundError, NoProductVarError,
                              SubCommandAlreadyExists, DuplicateSectionErrorWrapper)


def check_param(param_name: str, section: SectionProxy, valid_values: list[str | None] | None = None,
                raise_if_not_exists: bool = True) -> str | None:
    """
    Проверяет, существует ли в переданной секции указанный параметр и если да, валидно ли его значение.

    :param param_name: название параметра.
    :param section: объект секции.
    :param valid_values: валидные значения. Если None, любая строка - валидное значение.
    :param raise_if_not_exists: возбуждать ли исключение, если параметр не найден.

    :return: Значение ключа, если ключ найден и его значение валидно. Если ключ не найден и
    raise_ex_if_not_exists == False - возвращает None. В любом другом случае возбуждает исключения.
    """
    if param_name not in list(section.keys()):
        if raise_if_not_exists:
            raise ParamNotFoundError(param_name)
        return None

    value = section[param_name].strip()

    # Если значение пустое ("", оно не может быть None)
    if not value:
        if valid_values and None in valid_values:
            return value
        raise EmptyValueError(param_name)

    if valid_values and valid_values != [None] and value not in valid_values:
        raise ValueNotValidError(param_name, value, valid_values)
    return value


def create_config_obj(config_path: str) -> ConfigParser:
    """
    Создает объект конфига с нужными настройками.

    :param config_path: путь до файла конфига.

    :return: объект конфига.
    """
    config = ConfigParser(delimiters=(":", ), interpolation=None)
    config.optionxform = str
    config.read_file(codecs.open(config_path, "r", "utf8"))
    return config


def load_main_config(config_path: str):
    """
    Парсит и проверяет на правильность основной конфиг.

    :param config_path: путь до основного конфига.

    :return: спарсеный основной конфиг.
    """
    config = create_config_obj(config_path)
    values = {
        "FunPay": {
            "golden_key": "any",
            "user_agent": "any+empty",
            "autoRaise": ["0", "1"],
            "autoResponse": ["0", "1"],
            "autoDelivery": ["0", "1"],
            "multiDelivery": ["0", "1"],
            "autoRestore": ["0", "1"],
            "autoDisable": ["0", "1"],
            "oldMsgGetMode": ["0", "1"]
        },

        "Telegram": {
            "enabled": ["0", "1"],
            "token": "any+empty",
            "secretKey": "any"
        },

        "BlockList": {
            "blockDelivery": ["0", "1"],
            "blockResponse": ["0", "1"],
            "blockNewMessageNotification": ["0", "1"],
            "blockNewOrderNotification": ["0", "1"],
            "blockCommandNotification": ["0", "1"]
        },

        "NewMessageView": {
            "includeMyMessages": ["0", "1"],
            "includeFPMessages": ["0", "1"],
            "includeBotMessages": ["0", "1"],
            "notifyOnlyMyMessages": ["0", "1"],
            "notifyOnlyFPMessages": ["0", "1"],
            "notifyOnlyBotMessages": ["0", "1"],
        },

        "Greetings": {
            "cacheInitChats": ["0", "1"],
            "ignoreSystemMessages": ["0", "1"],
            "sendGreetings": ["0", "1"],
            "greetingsText": "any"
        },

        "OrderConfirm": {
            "sendReply": ["0", "1"],
            "replyText": "any"
        },

        "ReviewReply": {
            "star1Reply": ["0", "1"],
            "star2Reply": ["0", "1"],
            "star3Reply": ["0", "1"],
            "star4Reply": ["0", "1"],
            "star5Reply": ["0", "1"],
            "star1ReplyText": "any+empty",
            "star2ReplyText": "any+empty",
            "star3ReplyText": "any+empty",
            "star4ReplyText": "any+empty",
            "star5ReplyText": "any+empty",
        },

        "Proxy": {
            "enable": ["0", "1"],
            "ip": "any+empty",
            "port": "any+empty",
            "login": "any+empty",
            "password": "any+empty",
            "check": ["0", "1"]
        },

        "Other": {
            "watermark": "any+empty",
            "requestsDelay": [str(i) for i in range(1, 101)],
            "language": ["ru", "eng"]
        }
    }

    for section_name in values:
        if section_name not in config.sections():
            raise ConfigParseError(config_path, section_name, SectionNotFoundError())

        for param_name in values[section_name]:

            # UPDATE 009
            if section_name == "FunPay" and param_name == "oldMsgGetMode" and param_name not in config[section_name]:
                config.set("FunPay", "oldMsgGetMode", "0")
                with open("configs/_main.cfg", "w", encoding="utf-8") as f:
                    config.write(f)
            elif section_name == "Greetings" and param_name == "ignoreSystemMessages" and param_name not in config[section_name]:
                config.set("Greetings", "ignoreSystemMessages", "0")
                with open("configs/_main.cfg", "w", encoding="utf-8") as f:
                    config.write(f)
            elif section_name == "Other" and param_name == "language" and param_name not in config[section_name]:
                config.set("Other", "language", "ru")
                with open("configs/_main.cfg", "w", encoding="utf-8") as f:
                    config.write(f)
            # END OF UPDATE 009

            try:
                if values[section_name][param_name] == "any":
                    check_param(param_name, config[section_name])
                elif values[section_name][param_name] == "any+empty":
                    check_param(param_name, config[section_name], valid_values=[None])
                else:
                    check_param(param_name, config[section_name], valid_values=values[section_name][param_name])
            except (ParamNotFoundError, EmptyValueError, ValueNotValidError) as e:
                raise ConfigParseError(config_path, section_name, e)

    return config


def load_auto_response_config(config_path: str):
    """
    Парсит и проверяет на правильность конфиг команд.

    :param config_path: путь до конфига команд.

    :return: спарсеный конфиг команд.
    """
    try:
        config = create_config_obj(config_path)
    except configparser.DuplicateSectionError as e:
        raise ConfigParseError(config_path, e.section, DuplicateSectionErrorWrapper())

    command_sets = []
    for command in config.sections():
        try:
            check_param("response", config[command])
            check_param("telegramNotification", config[command], valid_values=["0", "1"], raise_if_not_exists=False)
            check_param("notificationText", config[command], raise_if_not_exists=False)
        except (ParamNotFoundError, EmptyValueError, ValueNotValidError) as e:
            raise ConfigParseError(config_path, command, e)

        if "|" in command:
            command_sets.append(command)

    for command_set in command_sets:
        commands = command_set.split("|")
        parameters = config[command_set]

        for new_command in commands:
            new_command = new_command.strip()
            if not new_command:
                continue
            if new_command in config.sections():
                raise ConfigParseError(config_path, command_set, SubCommandAlreadyExists(new_command))
            config.add_section(new_command)
            for param_name in parameters:
                config.set(new_command, param_name, parameters[param_name])
    return config


def load_raw_auto_response_config(config_path: str):
    """
    Загружает исходный конфиг автоответчика.

    :param config_path: путь до конфига команд.

    :return: спарсеный конфиг команд.
    """
    return create_config_obj(config_path)


def load_auto_delivery_config(config_path: str):
    """
    Парсит и проверяет на правильность конфиг автовыдачи.

    :param config_path: путь до конфига автовыдачи.

    :return: спарсеный конфиг товаров для автовыдачи.
    """
    try:
        config = create_config_obj(config_path)
    except configparser.DuplicateSectionError as e:
        raise ConfigParseError(config_path, e.section, DuplicateSectionErrorWrapper())

    for lot_title in config.sections():
        try:
            lot_response = check_param("response", config[lot_title])
            products_file_name = check_param("productsFileName", config[lot_title], raise_if_not_exists=False)
            check_param("disable", config[lot_title], valid_values=["0", "1"], raise_if_not_exists=False)
            check_param("disableAutoRestore", config[lot_title], valid_values=["0", "1"], raise_if_not_exists=False)
            check_param("disableAutoDisable", config[lot_title], valid_values=["0", "1"], raise_if_not_exists=False)
            check_param("disableAutoDelivery", config[lot_title], valid_values=["0", "1"], raise_if_not_exists=False)
            if products_file_name is None:
                # Если данного параметра нет, то в текущем лоте более нечего проверять -> переход на след. итерацию.
                continue
        except (ParamNotFoundError, EmptyValueError, ValueNotValidError) as e:
            raise ConfigParseError(config_path, lot_title, e)

        # Проверяем, существует ли файл.
        if not os.path.exists(f"storage/products/{products_file_name}"):
            raise ConfigParseError(config_path, lot_title,
                                   ProductsFileNotFoundError(f"storage/products/{products_file_name}"))

        # Проверяем, есть ли хотя бы 1 переменная $product в тексте response.
        if "$product" not in lot_response:
            raise ConfigParseError(config_path, lot_title, NoProductVarError())
    return config
