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

    def translate(self, variable_name: str, *args):
        """
        Возвращает форматированный локализированный текст.

        :param variable_name: название переменной с текстом.
        :param args: аргументы для форматирования.

        :return: форматированный локализированный текст.
        """
        text = variable_name
        for language in self.languages.values():
            if hasattr(language, variable_name):
                text = getattr(language, variable_name)
                break

        args = list(args)
        formats = text.count("{}")
        if len(args) < formats:
            args.extend(["{}"] * (formats - len(args)))
        return text.format(*args)
