
import re
from enum import Enum
from string import Template
import argparse
import logging

logger = logging.getLogger('furigana_merger')
logger.setLevel(logging.DEBUG)

KANJI_REGEX = re.compile(r'[一-龯々]')
HIRAGANA_REGEX = re.compile(r'[ぁ-ん]')
KATAKANA_REGEX = re.compile(r'[ァ-ン]')

class CharacterType(Enum):
    KANJI = 'kanji'
    HIRAGANA = 'hiragana'
    KATAKANA = 'katakana'
    OTHER = 'other'

class FuriganaMerger:
    def __init__(self, 
                 full_file: str, 
                 kana_file: str, 
                 merged_file: str, 
                 new_kana_file: str, 
                 furigana_template: str, 
                 kana_template: str):
        self.full_file = full_file
        self.kana_file = kana_file
        self.merged_file = merged_file
        self.new_kana_file = new_kana_file
        self.furigana_template = furigana_template
        self.kana_template = kana_template

    def clean_string(self, string: str) -> str:
        return string.translate(str.maketrans('', '', '\t\n\r\f\v \u3000'))

    def is_kanji(self, char: str) -> bool:
        return bool(KANJI_REGEX.match(char))

    def is_hiragana(self, char: str) -> bool:
        return bool(HIRAGANA_REGEX.match(char))

    def is_katakana(self, char: str) -> bool:
        return bool(KATAKANA_REGEX.match(char))

    def get_char_type(self, char: str) -> CharacterType:
        if self.is_kanji(char):
            return CharacterType.KANJI
        elif self.is_hiragana(char):
            return CharacterType.HIRAGANA
        elif self.is_katakana(char):
            return CharacterType.KATAKANA
        return CharacterType.OTHER

    def segment_char_types(self, full_string: str) -> list[tuple[str, CharacterType]]:
        """
        Takes a string and breaks it into a list of tuples segmented on character type.
        Each tuple contains a segment of the string and the type of characters in that segment.
        
        Example: segment_kanji('漢字です。カタカナ') -> 
        [('漢字', CharacterType.KANJI), ('です', CharacterType.HIRAGANA), ('。', CharacterType.OTHER), ('カタカナ', CharacterType.KATAKANA)]
        """
        segments = []
        current_block = ''
        last_type = ''
        # take the string full and break it into a list separating segments of kanji and kana
        for i in range(len(full_string)):
            cur_type = self.get_char_type(full_string[i])
            if cur_type == last_type:
                current_block += full_string[i]
            else:
                if not current_block == '':
                    segments.append((current_block, last_type))
                    current_block = ''
                current_block += full_string[i]
                last_type = cur_type
        segments.append((current_block, last_type))
        return segments

    def build_regex(self, segments: list[tuple[str, CharacterType]]) -> str:
        regex = ''
        for segment in segments:
            segment_text = segment[0]
            segment_type = segment[1]
            if segment_type == CharacterType.KANJI:
                # we want to match the hiragana conversion of the kanji
                regex += '([ぁ-ん]+)'
            elif segment_type == CharacterType.HIRAGANA:
                # these particles don't always get converted to hiragana well
                segment_text = re.sub(r'は', '(?:は|わ)', segment_text)
                segment_text = re.sub(r'を', '[をお]', segment_text)
                segment_text = re.sub(r'へ', '[へえ]', segment_text)
                segment_text = re.sub(r'[いゆ]', '[いゆ]', segment_text)
                regex += segment_text
            elif segment_type == CharacterType.KATAKANA:
                # sometimes hirigana conversion for lyrics overwill convert katakana to hirigana
                # so we just want to match the length of the segment and that it is kana
                # we also want to allow for a little bit of leeway in the length
                min_length = max(0, len(segment_text) - 1)
                max_length = len(segment_text) + 1
                regex += '[ぁ-んァ-ン]{' + str(min_length) + ',' + str(max_length) + '}'
            else:
                regex += '.{0,' + str(len(segment_text)) + '}'
        logger.debug(regex)
        return regex

    def build_matches(self, regex: str, kana: str) -> re.Match:
        match = re.match(regex, kana)
        if not match:
            logger.critical("No match found! for regex: " + regex + " and kana: " + kana)
        return match

    def format_from_template(self, template: str, format_vars: dict) -> str:
        template = Template(template)
        return template.safe_substitute(format_vars)

    def match_furigana(self, segments: list[tuple[str, CharacterType]], match: str) -> tuple[str, str]:
        furigana_out = ''
        kana_out = ''
        match_index = 0
        for segment in segments:
            segment_text = segment[0]
            segment_type = segment[1]
            if segment_type == CharacterType.KANJI:
                format_vars = {
                    'kanji': segment_text,
                    'hiragana': match.groups()[match_index]
                }
                furigana_out += self.format_from_template(self.furigana_template, format_vars)
                kana_out += self.format_from_template(self.kana_template, format_vars)

                match_index += 1
            elif segment_type == CharacterType.KATAKANA:
                furigana_out += segment_text
                kana_out += segment_text
            else:
                furigana_out += segment_text
                kana_out += segment_text
        return (furigana_out, kana_out)

    def merge_furigana(self, full: str, kana: str) -> tuple[str, str]:
        full = self.clean_string(full)
        kana = self.clean_string(kana)
        logger.debug(full)
        logger.debug(kana)
        segments = self.segment_char_types(full)
        regex = self.build_regex(segments)
        match = self.build_matches(regex, kana)
        return self.match_furigana(segments, match)

    def merge_files(self):
        logger.info("Merging files...")
        full_file = open(self.full_file, "r")
        kana_file = open(self.kana_file, "r")
        merged_file = open(self.merged_file, "w")
        new_kana_file = open(self.new_kana_file, "w")
        full_lines = full_file.readlines()
        kana_lines = kana_file.readlines()
        num_errors = 0
        error_lines = []
        for i in range(len(full_lines)):
            logger.debug("=====================================")
            logger.debug("Merging line " + str(i + 1))
            # check if line is empty
            if full_lines[i] == '\n':
                merged_file.write('\n')
                new_kana_file.write('\n')
            else:
                full = full_lines[i]
                kana = kana_lines[i]
                try:
                    furigana = self.merge_furigana(full, kana)
                except:
                    msg = "!!! Error merging line " + str(i + 1) + " !!!"
                    num_errors += 1
                    error_lines.append(i + 1)
                    logger.critical(msg)
                    merged_file.write(msg + '\n')
                    new_kana_file.write(msg + '\n') 
                    continue
                merged_file.write(furigana[0] + '\n')
                new_kana_file.write(furigana[1] + '\n') 
        full_file.close()
        kana_file.close()
        merged_file.close()
        new_kana_file.close()
        logger.info("Merging complete with " + str(num_errors) + " errors.")
        if num_errors > 0:
            logger.info("Errors occurred on lines: " + str(error_lines))

def main():
    parser = argparse.ArgumentParser(description='Merge furigana and kana files.')
    parser.add_argument('-f', '--full_file', type=str, default="inputs/full.txt", help='Path to the full text file')
    parser.add_argument('-k', '--kana_file', type=str, default="inputs/kana.txt", help='Path to the kana text file')
    parser.add_argument('-m', '--merged_file', type=str, default="outputs/merged.txt", help='Path to the merged output file')
    parser.add_argument('-n', '--new_kana_file', type=str, default="outputs/kana.txt", help='Path to the new kana output file')
    parser.add_argument('-ft', '--furigana_template', type=str, default='{${kanji}|${hiragana}}', help='Template for furigana')
    parser.add_argument('-kt', '--kana_template', type=str, default='**${hiragana}**', help='Template for kana')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    if args.debug:
        file_handler = logging.FileHandler('debug.log', mode='w')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    merger = FuriganaMerger(
        full_file=args.full_file,
        kana_file=args.kana_file,
        merged_file=args.merged_file,
        new_kana_file=args.new_kana_file,
        furigana_template=args.furigana_template,
        kana_template=args.kana_template
    )
    merger.merge_files()

if __name__ == "__main__":
    main()