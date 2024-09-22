import unittest
from src.japanese_utils import clean_string, is_kanji, is_hiragana, is_katakana, get_char_type, CharacterType

class TestJapaneseUtils(unittest.TestCase):
    def test_clean_string(self):
        self.assertEqual(clean_string(' こんにちは　'), 'こんにちは')
        self.assertEqual(clean_string('\tこんにちは\n'), 'こんにちは')

    def test_is_kanji(self):
        test_cases = [
            ('漢', True),
            ('々', True),
            ('あ', False),
            ('ア', False),
            ('0', False),
            ('９', False),
            ('a', False)

        ]
        for char, expected in test_cases:
            with self.subTest(char=char):
                self.assertEqual(is_kanji(char), expected)

    def test_is_hiragana(self):
        test_cases = [
            ('あ', True),
            ('ア', False),
            ('漢', False),
            ('0', False),
            ('９', False),
            ('a', False),
            ('ん', True),
            ('っ', True)
        ]
        for char, expected in test_cases:
            with self.subTest(char=char):
                self.assertEqual(is_hiragana(char), expected)

    def test_is_katakana(self):
        test_cases = [
            ('ア', True),
            ('あ', False),
            ('漢', False),
            ('0', False),
            ('９', False),
            ('a', False),
            ('ン', True),
            ('ッ', True)
        ]
        for char, expected in test_cases:
            with self.subTest(char=char):
                self.assertEqual(is_katakana(char), expected)

    def test_get_char_type(self):
        test_cases = [
            ('漢', CharacterType.KANJI),
            ('々', CharacterType.KANJI),
            ('あ', CharacterType.HIRAGANA),
            ('ん', CharacterType.HIRAGANA),
            ('ぴ', CharacterType.HIRAGANA),
            ('っ', CharacterType.HIRAGANA),
            ('ア', CharacterType.KATAKANA),
            ('ン', CharacterType.KATAKANA),
            ('ピ', CharacterType.KATAKANA),
            ('ッ', CharacterType.KATAKANA),
            ('0', CharacterType.NUMBER),
            ('９', CharacterType.NUMBER),
            ('1', CharacterType.NUMBER),
            ('１', CharacterType.NUMBER),
            ('!', CharacterType.OTHER),
            ('。', CharacterType.OTHER),
            ('a', CharacterType.OTHER)
        ]
        for char, expected in test_cases:
            with self.subTest(char=char):
                self.assertEqual(get_char_type(char), expected)

        
if __name__ == '__main__':
    unittest.main()