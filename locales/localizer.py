from locales import ru, en, uk


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
        return text.format(*args)
