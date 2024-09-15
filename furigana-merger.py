
import re
from enum import Enum
from string import Template

class CharacterType(Enum):
    KANJI = 'kanji'
    HIRAGANA = 'hiragana'
    KATAKANA = 'katakana'
    OTHER = 'other'

KANJI_REGEX = re.compile(r'[一-龯々]')
HIRAGANA_REGEX = re.compile(r'[ぁ-ん]')
KATAKANA_REGEX = re.compile(r'[ァ-ン]')

def clean_string(string: str) -> str:
    return string.translate(str.maketrans('', '', '\t\n\r\f\v \u3000'))

def is_kanji(char: str) -> bool:
    return bool(KANJI_REGEX.match(char))

def is_hiragana(char: str) -> bool:
    return bool(HIRAGANA_REGEX.match(char))

def is_katakana(char: str) -> bool:
    return bool(KATAKANA_REGEX.match(char))

def get_char_type(char: str) -> CharacterType:
    if is_kanji(char):
        return CharacterType.KANJI
    elif is_hiragana(char):
        return CharacterType.HIRAGANA
    elif is_katakana(char):
        return CharacterType.KATAKANA
    return CharacterType.OTHER

def segment_char_types(full_string: str) -> list[tuple[str, CharacterType]]:
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
        cur_type = get_char_type(full_string[i])
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

def build_regex(segments: list[tuple[str, CharacterType]]) -> str:
    regex = ''
    for segment in segments:
        segment_text = segment[0]
        segment_type = segment[1]
        if segment_type == CharacterType.KANJI:
            # we want to match the hiragana conversion of the kanji
            regex += '([ぁ-ん]+)'
        elif segment_type == CharacterType.HIRAGANA:
            # these particles don't always get converted to hiragana well
            segment_text = re.sub(r'は', '[はわ]', segment_text)
            segment_text = re.sub(r'を', '[をお]', segment_text)
            regex += segment_text
        elif segment_type == CharacterType.KATAKANA:
            # sometimes hirigana conversion for lyrics overwill convert katakana to hirigana
            # so we just want to match the length of the segment and that it is kana
            regex += '[ぁ-んァ-ン]{0,' + str(len(segment_text)) + '}'
        else:
            regex += '.{0,' + str(len(segment_text)) + '}'
    print(regex)
    return regex

def build_matches(regex: str, kana: str) -> re.Match:
    return re.match(regex, kana)

def format_from_template(template: str, format_vars: dict) -> str:
    template = Template(template)
    return template.safe_substitute(format_vars)

def match_furigana(segments: list[tuple[str, CharacterType]], match: str) -> tuple[str, str]:
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
            furigana_template = '{${hiragana}|${kanji}}'
            furigana_out += format_from_template(furigana_template, format_vars)

            kana_template = '**${hiragana}**'
            kana_out += format_from_template(kana_template, format_vars)

            match_index += 1
        elif segment_type == CharacterType.KATAKANA:
            furigana_out += segment_text
            kana_out += segment_text
        else:
            furigana_out += segment_text
            kana_out += segment_text
    return (furigana_out, kana_out)

def merge_furigana(full: str, kana: str) -> tuple[str, str]:
    full = clean_string(full)
    kana = clean_string(kana)
    print(full)
    print(kana)
    segments = segment_char_types(full)
    regex = build_regex(segments)
    match = build_matches(regex, kana)
    return match_furigana(segments, match)

def merge_files(full_file: str, kana_file: str, merged_file: str, new_kana_file: str):
    print("Merging files...")
    full_file = open(full_file, "r")
    kana_file = open(kana_file, "r")
    merged_file = open(merged_file, "w")
    new_kana_file = open(new_kana_file, "w")
    full_lines = full_file.readlines()
    kana_lines = kana_file.readlines()
    for i in range(len(full_lines)):
        print(i)
        # check if line is empty
        if full_lines[i] == '\n':
            merged_file.write('\n')
            new_kana_file.write('\n')
        else:
            full = full_lines[i]
            kana = kana_lines[i]
            furigana = merge_furigana(full, kana)
            merged_file.write(furigana[0] + '\n')
            new_kana_file.write(furigana[1] + '\n')    
    full_file.close()
    kana_file.close()
    merged_file.close()
    new_kana_file.close()
    print("Files merged!")

def main():
    full_file = "inputs/full.txt"
    kana_file = "inputs/kana.txt"
    merged_file = "outputs/merged.txt"
    new_kana_file = "outputs/kana.txt"

    merge_files(full_file, kana_file, merged_file, new_kana_file)

if __name__ == "__main__":
    main()