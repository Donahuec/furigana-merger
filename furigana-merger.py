
import re

def clean_string(string):
    out = string
    out = re.sub(r'\s', '', out)
    return out

def is_kanji(char):
    kanji_regex = '[一-龯々]'
    match = re.match(kanji_regex, char)
    return match is not None

def is_hiragana(char):
    hiragana_regex = '[ぁ-ん]'
    match = re.match(hiragana_regex, char)
    return match is not None

def is_katakana(char):
    katakana_regex = '[ァ-ン]'
    match = re.match(katakana_regex, char)
    return match is not None

def get_char_type(char):
    if is_kanji(char):
        return 'kanji'
    elif is_hiragana(char):
        return 'hiragana'
    elif is_katakana(char):
        return 'katakana'
    else:
        return 'other'
    
def segment_kanji(full_string):
    segments = []
    current_block = ''
    last_was_kanji = False
    # take the string full and break it into a list separating segments of kanji and kana
    for i in range(len(full_string)):
        if is_kanji(full_string[i]):
            if not last_was_kanji and not current_block == '':
                segments.append(current_block)
                current_block = ''
            current_block += full_string[i]
            last_was_kanji = True
        else:
            if last_was_kanji and not current_block == '':
                segments.append(current_block)
                current_block = ''
            current_block += full_string[i]
            last_was_kanji = False
    segments.append(current_block)
    return segments


def segment_char_types(full_string):
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

def build_regex(segments):
    regex = ''
    for segment in segments:
        segment_text = segment[0]
        segment_type = segment[1]
        if segment_type == 'kanji':
            regex += '([ぁ-ん]+)'
        elif segment_type == 'katakana':
            regex += '[ぁ-んァ-ン]{0,' + str(len(segment_text)) + '}'
        elif segment_type == 'hiragana':
            # these particles don't always get converted to hiragana well
            segment_text = re.sub(r'は', '[はわ]', segment_text)
            segment_text = re.sub(r'を', '[をお]', segment_text)
            regex += segment_text
        else:
            regex += '.{0,' + str(len(segment_text)) + '}'
    return regex

def build_matches(regex, kana):
    return re.match(regex, kana)

def match_furigana(segments, match):
    furigana = ''
    kana = ''
    match_index = 0
    for segment in segments:
        segment_text = segment[0]
        segment_type = segment[1]
        if segment_type == 'kanji':
            furigana += '{' + segment_text + '|' + match.groups()[match_index] + '}'
            kana += match.groups()[match_index]
            match_index += 1
        elif segment_type == 'katakana':
            furigana += segment_text
            kana += segment_text
        else:
            furigana += segment_text
            kana += segment_text
    return (furigana, kana)

def merge_furigana(full, kana):
    full = clean_string(full)
    kana = clean_string(kana)
    segments = segment_char_types(full)
    regex = build_regex(segments)
    match = build_matches(regex, kana)
    return match_furigana(segments, match)

def merge_files(full_file, kana_file, merged_file, new_kana_file):
    print("Merging files...")
    full_file = open(full_file, "r")
    kana_file = open(kana_file, "r")
    merged_file = open(merged_file, "w")
    new_kana_file = open(new_kana_file, "w")
    full_lines = full_file.readlines()
    kana_lines = kana_file.readlines()
    for i in range(len(full_lines)):
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


full_file = "inputs/full.txt"
kana_file = "inputs/kana.txt"
merged_file = "outputs/merged.txt"
new_kana_file = "outputs/kana.txt"

merge_files(full_file, kana_file, merged_file, new_kana_file)


