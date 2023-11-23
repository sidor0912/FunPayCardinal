"""
В данном модуле описаны все кастомные исключения, которые райзятся при валидации конфигов.
"""
from locales.localizer import Localizer
localizer = Localizer()
_ = localizer.translate


class ParamNotFoundError(Exception):
    """
    Исключение, которое райзится, если при обработке конфига не был найден искомый параметр.
    """
    def __init__(self, param_name: str):
        """
        :param param_name: название параметра.
        """
        self.param_name = param_name

    def __str__(self):
        return _("exc_param_not_found", self.param_name)


class EmptyValueError(Exception):
    """
    Исключение, которое райзится, если при обработке конфига было найдено пустое значение.
    """
    def __init__(self, param_name: str):
        """
        :param param_name: название параметра.
        """
        self.param_name = param_name

    def __str__(self):
        return _("exc_param_cant_be_empty", self.param_name)


class ValueNotValidError(Exception):
    """
    Исключение, которое райзится, если при обработке конфига было найдено недопустимое значение.
    """
    def __init__(self, param_name: str, current_value: str, valid_values: list[str | None]):
        """
        :param param_name: название параметра.
        :param current_value: текущее значение.
        :param valid_values: допустимые значения.
        """
        self.param_name = param_name
        self.current_value = current_value
        self.valid_values = valid_values

    def __str__(self):
        return _("exc_param_value_invalid", self.param_name, self.valid_values, self.current_value)


class ProductsFileNotFoundError(Exception):
    """
    Исключение, которое райзится, если при обработке конфига автовыдачи не был найден указанный файл с товарами.
    """
    def __init__(self, goods_file_path: str):
        self.goods_file_path = goods_file_path

    def __str__(self):
        return _("exc_goods_file_not_found", self.goods_file_path)


class NoProductsError(Exception):
    """
    Исключение, которое райзится, если в товарном файле, указанном в конфиге автовыдачи, нет товаров.
    """
    def __init__(self, goods_file_path: str):
        self.goods_file_path = goods_file_path

    def __str__(self):
        return _("exc_goods_file_is_empty", self.goods_file_path)


class NotEnoughProductsError(Exception):
    """
    Исключение, которое райзится, если запрошено больше товаров, чем есть в товарном файле.
    """
    def __init__(self, goods_file_path: str, available: int, requested: int):
        """
        :param goods_file_path: путь до товарного файла.
        :param available: кол-во товаров в файле.
        :param requested: кол-во запрошенного товара.
        """
        self.goods_file_path = goods_file_path
        self.available = available
        self.requested = requested

    def __str__(self):
        return _("exc_not_enough_items", self.goods_file_path, self.requested, self.available)


class NoProductVarError(Exception):
    """
    Исключение, которое райзится, если в конфиге автовыдачи указан файл с товарами, но в параметре response нет
    ни одной переменной $product.
    """
    def __init__(self):
        pass

    def __str__(self):
        return _("exc_no_product_var")


class SectionNotFoundError(Exception):
    """
    Исключение, которое райзится, если при обработке конфига не была найдена обязательная секция.
    """
    def __init__(self):
        pass

    def __str__(self):
        return _("exc_no_section")


class SubCommandAlreadyExists(Exception):
    """
    Исключение, которое райзится, если при обработке конфига автоответчика был найден дубликат суб-команды.
    """
    def __init__(self, command: str):
        self.command = command

    def __str__(self):
        return _("exc_cmd_duplicate", self.command)


class DuplicateSectionErrorWrapper(Exception):
    """
    Исключение, которое райзится, если при обработке конфига было словлено configparser.DuplicateSectionError
    """
    def __init__(self):
        pass

    def __str__(self):
        return _("exc_section_duplicate")


class ConfigParseError(Exception):
    """
    Исключение, которое райзится, если при обработке конфига произошла одна из ошибок, описанных выше.
    """
    def __init__(self, config_path: str, section_name: str, exception: Exception):
        self.config_path = config_path
        self.section_name = section_name
        self.exception = exception

    def __str__(self):
        return _("exc_cfg_parse_err", self.config_path, self.section_name, self.exception)


class FieldNotExistsError(Exception):
    """
    Исключение, которое райзится, если при загрузке плагина не было обнаружено переданное поле.
    """
    def __init__(self, field_name: str, plugin_file_name: str):
        self.field_name = field_name
        self.plugin_file_name = plugin_file_name

    def __str__(self):
        return _("exc_plugin_field_not_found", self.plugin_file_name, self.field_name)
