import re
import unittest
from src.furigana_merger import FuriganaMerger
from src.japanese_utils import CharacterType

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
        expected_regex = '([ぁ-ん]+)です.{0,1}[ぁ-んァ-ン]{3,5}'
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
        with self.subTest('furigana'):
            self.assertEqual(furigana_out, '{漢字|かんじ}です。カタカナ')
        with self.subTest('kana'):
            self.assertEqual(kana_out, '**かんじ**です。カタカナ')

    def test_merge_furigana(self):
        full = '漢字です。カタカナ'
        kana = 'かんじです。カタカナ'
        furigana_out, kana_out = self.merger.merge_furigana(full, kana)
        with self.subTest('furigana'):
            self.assertEqual(furigana_out, '{漢字|かんじ}です。カタカナ')
        with self.subTest('kana'):
            self.assertEqual(kana_out, '**かんじ**です。カタカナ')

    def test_merged_furigana_with_numbers(self):
        full = '漢字です。カタカナ123'
        kana = 'かんじです。カタカナ123'
        furigana_out, kana_out = self.merger.merge_furigana(full, kana)
        with self.subTest('All numbers - furigana'):
            self.assertEqual(furigana_out, '{漢字|かんじ}です。カタカナ123')
        with self.subTest('All numbers - kana'):
            self.assertEqual(kana_out, '**かんじ**です。カタカナ123')
        
        full = '漢字です。カタカナ123'
        kana = 'かんじです。カタカナいちにさん'
        furigana_out, kana_out = self.merger.merge_furigana(full, kana)
        with self.subTest('Hiragana numbers - furigana'):
            self.assertEqual(furigana_out, '{漢字|かんじ}です。カタカナ123')
        with self.subTest('Hiragana numbers - kana'):
            self.assertEqual(kana_out, '**かんじ**です。カタカナ123')
        
    def test_merged_furigana_with_numbers_and_kanji(self):
        full = '漢字です123年'
        kana = 'かんじですいちにさんねん'
        furigana_out, kana_out = self.merger.merge_furigana(full, kana)
        with self.subTest('furigana'):
            self.assertEqual(furigana_out, '{漢字|かんじ}です{123年|いちにさんねん}')
        with self.subTest('kana'):
            self.assertEqual(kana_out, '**かんじ**です**いちにさんねん**')

if __name__ == '__main__':
    unittest.main()