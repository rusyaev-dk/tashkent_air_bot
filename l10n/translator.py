from typing import List, Dict, Any
from fluent.runtime import FluentResourceLoader, FluentLocalization


class Translator:
    def __init__(
            self,
            locales_dir_path: str,
            locales: List[str],
            resource_ids: List[str],
            default_locale: str = "ru",
    ):
        self.l10n_loader = FluentResourceLoader(str(locales_dir_path) + "/{locale}")
        self.locales = locales
        self.resource_ids = resource_ids
        self.default_locale = default_locale
        self.__cur_locale = default_locale

        self.l10ns = {
            locale: FluentLocalization(
                [locale],
                resource_ids,
                self.l10n_loader,
            )
            for locale in locales
        }

    def get_text(self, key: str, args: Dict[str, Any] = None, locale: str = None) -> str:
        if locale:
            return self.l10ns[locale].format_value(msg_id=key, args=args)
        return self.l10ns[self.__cur_locale].format_value(msg_id=key, args=args)

    def change_locale(self, new_locale: str):
        if new_locale in self.l10ns:
            self.__cur_locale = new_locale
