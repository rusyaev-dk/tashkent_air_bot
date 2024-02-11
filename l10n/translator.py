from typing import List, Dict, Any

from fluent.runtime import FluentResourceLoader, FluentLocalization


class TranslatorHub:
    def __init__(
            self,
            locales_dir_path: str,
            locales: List[str],
            resource_ids: List[str],
            default_locale: str = "ru"):
        self.l10n_loader = FluentResourceLoader(str(locales_dir_path) + "/{locale}")
        self.default_locale = default_locale
        self.l10ns = {
            locale: LocalizedTranslator(
                [locale],
                resource_ids,
                self.l10n_loader,
            )
            for locale in locales
        }


class LocalizedTranslator:
    l10n: FluentLocalization

    def __init__(self, locales: List[str], resource_ids: List[str], loader: FluentResourceLoader):
        self.l10n = FluentLocalization(locales, resource_ids, loader)

    def get_text(self, key: str, args: Dict[str, Any] = None) -> str:
        return self.l10n.format_value(msg_id=key, args=args)
