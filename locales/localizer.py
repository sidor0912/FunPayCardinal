from typing import Literal

from locales import ru, en, uk
import logging

logger = logging.getLogger("localizer")


class Localizer:
    def __new__(cls, curr_lang: str | None = None):
        if not hasattr(cls, "instance"):
            cls.instance = super(Localizer, cls).__new__(cls)
            cls.instance.languages = {
                "ru": ru,
                "en": en,
                "uk": uk
            }
            cls.instance.current_language = "ru"
        if curr_lang in cls.instance.languages:
            cls.instance.current_language = curr_lang
            cls.instance.languages = {k: v for k, v in sorted(cls.instance.languages.items(),
                                                              key=lambda x: x[0] != curr_lang)}
        return cls.instance

    def translate(self, variable_name: str, *args, language: str | None = None):
        """
        Возвращает форматированный локализированный текст.

        :param variable_name: название переменной с текстом.
        :param args: аргументы для форматирования.
        :param language: язык перевода, опционально.

        :return: форматированный локализированный текст.
        """
        text = variable_name
        for lang in self.languages.values():
            if hasattr(lang, variable_name):
                text = getattr(lang, variable_name)
                break
        if language and language in self.languages.keys() and hasattr(self.languages[language], variable_name):
            text = getattr(self.languages[language], variable_name)

        args = list(args)
        formats = text.count("{}")
        if len(args) < formats:
            args.extend(["{}"] * (formats - len(args)))
        try:
            return text.format(*args)
        except:
            logger.debug("TRACEBACK", exc_info=True)
            return text

    def add_translation(self, uuid: str, variable_name: str, value: str, language: Literal["uk", "ru", "en"]):
        """Позволяет добавить перевод фраз из плагина."""
        setattr(self.languages[language], f"{uuid}_{variable_name}", value)

    def plugin_translate(self, uuid: str, variable_name: str, *args, language: str | None = None):
        """Позволяет получить перевод фраз из плагина."""
        s = f"{uuid}_{variable_name}"
        result = self.translate(s, *args, language=language)
        if result != s:
            return result
        else:
            return self.translate(variable_name, *args, language=language)
