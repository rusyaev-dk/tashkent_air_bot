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

        self.l10ns = {
            locale: FluentLocalization(
                [locale],
                resource_ids,
                self.l10n_loader,
            )
            for locale in locales
        }

        self.cur_translator = self.l10ns.get(default_locale)

    def get_text(self, key: str, args: Dict[str, Any] = None) -> str:
        """
        Retrieves localized text for a given key and optional arguments.

        Args:
            key (str): The key identifying the localized message.
            args (Dict[str, Any], optional): Dictionary of arguments for message interpolation. Defaults to None.

        Returns:
            str: The localized string corresponding to the key and arguments.
        """

        return self.cur_translator.format_value(msg_id=key, args=args)

    def change_locale(self, new_locale: str):
        if new_locale in self.l10ns:
            self.cur_translator = self.l10ns[new_locale]
