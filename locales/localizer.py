from locales import ru, eng


class Localizer:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Localizer, cls).__new__(cls)
        return getattr(cls, "instance")

    def __init__(self, curr_lang: str | None = None):
        self.languages = {
            "ru": ru,
            "eng": eng
        }
        self.default_language = "ru"
        self.current_language = curr_lang if curr_lang in self.languages else self.default_language

    def translate(self, variable_name: str, *args):
        """
        Возвращает форматированный локализированный текст.

        :param variable_name: название переменной с текстом.
        :param args: аргументы для форматирования.

        :return: форматированный локализированный текст.
        """
        if not hasattr(self.languages[self.current_language], variable_name):
            if not hasattr(self.languages[self.default_language], variable_name):
                return variable_name
            text = getattr(self.languages[self.default_language], variable_name)
        else:
            text = getattr(self.languages[self.current_language], variable_name)

        args = list(args)
        formats = text.count("{}")
        if len(args) < formats:
            args.extend(["{}"] * (formats - len(args)))
        return text.format(*args)
