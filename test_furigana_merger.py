import re
import unittest
from furigana_merger import FuriganaMerger, CharacterType

class TestFuriganaMerger(unittest.TestCase):

    def setUp(self):
        self.merger = FuriganaMerger(
            full_file='',
            kana_file='',
            merged_file='',
            new_kana_file='',
            furigana_template='{${kanji}|${hiragana}}',
            kana_template='**${hiragana}**'
        )

    def test_clean_string(self):
        self.assertEqual(self.merger.clean_string(' こんにちは　'), 'こんにちは')
        self.assertEqual(self.merger.clean_string('\tこんにちは\n'), 'こんにちは')

    def test_is_kanji(self):
        self.assertTrue(self.merger.is_kanji('漢'))
        self.assertTrue(self.merger.is_kanji('々'))
        self.assertFalse(self.merger.is_kanji('あ'))

    def test_is_hiragana(self):
        self.assertTrue(self.merger.is_hiragana('あ'))
        self.assertFalse(self.merger.is_hiragana('ア'))

    def test_is_katakana(self):
        self.assertTrue(self.merger.is_katakana('ア'))
        self.assertFalse(self.merger.is_katakana('あ'))

    def test_get_char_type(self):
        self.assertEqual(self.merger.get_char_type('漢'), CharacterType.KANJI)
        self.assertEqual(self.merger.get_char_type('あ'), CharacterType.HIRAGANA)
        self.assertEqual(self.merger.get_char_type('ア'), CharacterType.KATAKANA)
        self.assertEqual(self.merger.get_char_type('a'), CharacterType.OTHER)

    def test_segment_char_types(self):
        result = self.merger.segment_char_types('漢字です。カタカナ')
        expected = [
            ('漢字', CharacterType.KANJI),
            ('です', CharacterType.HIRAGANA),
            ('。', CharacterType.OTHER),
            ('カタカナ', CharacterType.KATAKANA)
        ]
        self.assertEqual(result, expected)

    def test_build_regex(self):
        segments = [
            ('漢字', CharacterType.KANJI),
            ('です', CharacterType.HIRAGANA),
            ('。', CharacterType.OTHER),
            ('カタカナ', CharacterType.KATAKANA)
        ]
        regex = self.merger.build_regex(segments)
        expected_regex = '([ぁ-ん]+?)です.{0,1}[ぁ-んァ-ン]{3,5}'
        self.assertEqual(regex, expected_regex)

    def test_format_from_template(self):
        template = '{${kanji}|${hiragana}}'
        format_vars = {'kanji': '漢字', 'hiragana': 'かんじ'}
        result = self.merger.format_from_template(template, format_vars)
        self.assertEqual(result, '{漢字|かんじ}')

    def test_match_furigana(self):
        segments = [
            ('漢字', CharacterType.KANJI),
            ('です', CharacterType.HIRAGANA),
            ('。', CharacterType.OTHER),
            ('カタカナ', CharacterType.KATAKANA)
        ]
        match = re.match('([ぁ-ん]+?)です.{0,1}[ぁ-んァ-ン]{3,5}', 'かんじです。カタカナ')
        furigana_out, kana_out = self.merger.match_furigana(segments, match)
        self.assertEqual(furigana_out, '{漢字|かんじ}です。カタカナ')
        self.assertEqual(kana_out, '**かんじ**です。カタカナ')

    def test_merge_furigana(self):
        full = '漢字です。カタカナ'
        kana = 'かんじです。カタカナ'
        furigana_out, kana_out = self.merger.merge_furigana(full, kana)
        self.assertEqual(furigana_out, '{漢字|かんじ}です。カタカナ')
        self.assertEqual(kana_out, '**かんじ**です。カタカナ')

if __name__ == '__main__':
    unittest.main()