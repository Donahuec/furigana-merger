import re
from enum import Enum

KANJI_REGEX = re.compile(r'[一-龯々]')
HIRAGANA_REGEX = re.compile(r'[ぁ-ん]')
KATAKANA_REGEX = re.compile(r'[ァ-ン]')
NUMBER_REGEX = re.compile(r'[0-9０-９]')

class CharacterType(Enum):
    KANJI = 'kanji'
    HIRAGANA = 'hiragana'
    KATAKANA = 'katakana'
    NUMBER = 'number'
    OTHER = 'other'

def clean_string(string: str) -> str:
    return string.translate(str.maketrans('', '', '\t\n\r\f\v \u3000'))

def is_kanji(char: str) -> bool:
    return bool(KANJI_REGEX.match(char))

def is_hiragana(char: str) -> bool:
    return bool(HIRAGANA_REGEX.match(char))

def is_katakana(char: str) -> bool:
    return bool(KATAKANA_REGEX.match(char))

def is_number(char: str) -> bool:
    return bool(NUMBER_REGEX.match(char))

def get_char_type(char: str) -> CharacterType:
    if is_kanji(char):
        return CharacterType.KANJI
    elif is_hiragana(char):
        return CharacterType.HIRAGANA
    elif is_katakana(char):
        return CharacterType.KATAKANA
    elif is_number(char):
        return CharacterType.NUMBER
    return CharacterType.OTHER