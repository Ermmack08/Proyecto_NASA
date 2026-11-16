import ast
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from modules.i18n import TRANSLATIONS, detect_system_language, translate


class InternationalizationTests(unittest.TestCase):
    def test_translation_catalogs_have_the_same_keys(self):
        self.assertEqual(set(TRANSLATIONS["es"]), set(TRANSLATIONS["en"]))

    def test_literal_translation_calls_exist_in_both_languages(self):
        project_root = Path(__file__).resolve().parents[1]
        source_files = [
            project_root / "app.py",
            project_root / "modules" / "map_utils.py",
            *sorted((project_root / "pages").glob("*.py")),
        ]
        used_keys = set()
        for source_file in source_files:
            tree = ast.parse(source_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "t"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                ):
                    used_keys.add(node.args[0].value)

        missing = {
            language: used_keys.difference(translations)
            for language, translations in TRANSLATIONS.items()
        }
        self.assertFalse(any(missing.values()), missing)

    def test_detects_spanish_or_english_from_system_locale(self):
        with (
            patch.dict(os.environ, {"LC_ALL": "es_CO.UTF-8"}, clear=True),
            patch("modules.i18n.locale.getlocale", return_value=(None, None)),
        ):
            self.assertEqual(detect_system_language(), "es")

        with (
            patch.dict(os.environ, {"LANG": "en_US.UTF-8"}, clear=True),
            patch("modules.i18n.locale.getlocale", return_value=(None, None)),
        ):
            self.assertEqual(detect_system_language(), "en")

    def test_defaults_to_spanish_for_unsupported_system_locale(self):
        with (
            patch.dict(os.environ, {"LANG": "fr_FR.UTF-8"}, clear=True),
            patch("modules.i18n.locale.getlocale", return_value=(None, None)),
        ):
            self.assertEqual(detect_system_language(), "es")

    def test_formats_translated_text(self):
        self.assertEqual(
            translate("selected_point", "en", latitude=6.3, longitude=-75.7, layer="NDVI"),
            "Selected point: 6.30000, -75.70000 · NDVI.",
        )


if __name__ == "__main__":
    unittest.main()
