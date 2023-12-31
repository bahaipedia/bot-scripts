"""
This family file was auto-generated by generate_family_file.py script.

Configuration parameters:
  url = https://bahaipedia.org/
  name = bahaipedia

Please do not commit this to the Git repository!
"""
from pywikibot import family


class Family(family.Family):  # noqa: D101

    name = 'bahaipedia'
    langs = {
        'en': 'bahaipedia.org',
        'de': 'de.bahaipedia.org',
        'es': 'es.bahaipedia.org',
        'fa': 'fa.bahaipedia.org',
        'fr': 'fr.bahaipedia.org',
        'pt': 'pt.bahaipedia.org',
        'ru': 'ru.bahaipedia.org',
        'vi': 'vi.bahaipedia.org',
        'zh': 'zh.bahaipedia.org',
    }

    def scriptpath(self, code):
        return {
            'en': '',
            'de': '',
            'es': '',
            'fa': '',
            'fr': '',
            'pt': '',
            'ru': '',
            'vi': '',
            'zh': '',
        }[code]

    def protocol(self, code):
        return {
            'en': 'https',
            'de': 'https',
            'es': 'https',
            'fa': 'https',
            'fr': 'https',
            'pt': 'https',
            'ru': 'https',
            'vi': 'https',
            'zh': 'https',
        }[code]
