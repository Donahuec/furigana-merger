import unittest
from src.japanese_utils import clean_string, is_kanji, is_hiragana, is_katakana, get_char_type, CharacterType

class TestJapaneseUtils(unittest.TestCase):
    def test_clean_string(self):
        self.assertEqual(clean_string(' こんにちは　'), 'こんにちは')
        self.assertEqual(clean_string('\tこんにちは\n'), 'こんにちは')

    def test_is_kanji(self):
        self.assertTrue(is_kanji('漢'))
        self.assertTrue(is_kanji('々'))
        self.assertFalse(is_kanji('あ'))

    def test_is_hiragana(self):
        self.assertTrue(is_hiragana('あ'))
        self.assertFalse(is_hiragana('ア'))

    def test_is_katakana(self):
        self.assertTrue(is_katakana('ア'))
        self.assertFalse(is_katakana('あ'))

    def test_get_char_type(self):
        self.assertEqual(get_char_type('漢'), CharacterType.KANJI)
        self.assertEqual(get_char_type('あ'), CharacterType.HIRAGANA)
        self.assertEqual(get_char_type('ア'), CharacterType.KATAKANA)
        self.assertEqual(get_char_type('a'), CharacterType.OTHER)

        
if __name__ == '__main__':
    unittest.main()