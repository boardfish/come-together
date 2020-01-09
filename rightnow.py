import pronouncing
import random
import logging

twitter_character_limit = 280

he_got = [
  [2, "here come"],
  [2, "he come"],
  [2, "he got"],
  [2, "he one"],
  [2, "he wear"],
  [2, "he shoot"],
  [2, "he say"],
  [2, "he bag"],
  [1, "he"],
]

joo_joo_eyeball = [
  [3, "old flat top"],
  [5, "moving up slowly"],
  [4, "jew jew eyeball"],
  [4, "holy roller"],
  [3, "no shoeshine"],
  [4, "toe jam football"],
  [4, "monkey finger"],
  [4, "Coca-Cola"],
  [3, "production"],
  [4, "walrus gum boot"],
  [4, "oh no side board"],
  [4, "spinal cracker"],
  [4, "rollercoaster"],
  [4, "early warning"],
  [4, "muddy water"],
  [4, "mojo filter"],
]

# Typical syllable limit is 4, first line is 5 inc. he

def total_syllables_in_string(text):
    try:
        phones = [pronouncing.phones_for_word(p)[0] for p in text.split()]
        return sum([pronouncing.syllable_count(p) for p in phones])
    except IndexError:
        logging.error("Syllables could not be found for %s.", text)
        return False
    
# Find a phrase with the same syllables and stresses as one of the phrases
# used at the start of most lines.
def generate_joo_joo_eyeball(syllable_count):
    text = [0]
    while(text[0] != syllable_count):
        text = random.choice(joo_joo_eyeball)
    text = text[1] # Discard count, we don't need it
    result = []
    for word in text.split():
        pronunciations = pronouncing.phones_for_word(word)
        pat = pronouncing.stresses(pronunciations[0])
        replacement = random.choice(pronouncing.search_stresses("^"+pat+"$"))
        result.append(replacement)
    return ' '.join(result)

# Build lines that can be used to make a verse.
# The first line can use 'he' and has 5 syllables (7 if it starts with "he come")
# The last has an extra "he got" that leads into the break lines
# The rest have six syllables.
# Type = 0: first, 1: mid, 2: last (extra he_got)
def generate_line(type = 1):
    first = type == 0
    random_he_got = random.choice(he_got) if first else random.choice(he_got[:-1])
    syllable_limit = ((7 if (random_he_got[1] == "he come") else 5) if first else 6)
    syllable_limit -= random_he_got[0]
    output_array = [random_he_got[1], generate_joo_joo_eyeball(syllable_limit)]
    if type == 2:
        output_array += [random.choice(he_got[:-1])[1]]
    return output_array

# Generates a full verse. Comes out as an array of arrays of strings.
def generate_verse():
    return [generate_line(first) for first in [0, 1, 1, 2]]

# Splits a verse as made by generate_verse as follows:
# he_got, joo_joo_eyeball, he got
# joo_joo_eyeball, he got
# joo_joo_eyeball, he got
# joo_joo_eyeball, he got
def split_for_pretty_printing():
    verse = generate_verse()
    flattened_verse = [words for phrase in verse for words in phrase]
    first_line = flattened_verse[:3]
    other_lines = flattened_verse[3:]
    other_lines_paired = list(zip(other_lines[::2], other_lines[1::2]))
    return [first_line] + other_lines_paired

# Converts the arrays representing lines into strings with correct
# punctuation and capitalisation.
def stringify(line):
    string_output = ''
    for index, phrase in enumerate(line):
        if index > 0:
            string_output += ',' if index == (len(line) - 1) else ''
            string_output += ' '
        string_output += phrase
    return string_output.capitalize()

# Generates a pretty-printed verse as follows:
# He_got joo_joo_eyeball, he got
# Joo_joo_eyeball, he got
# Joo_joo_eyeball, he got
# Joo_joo_eyeball, he got
def pretty_print():
    thing = split_for_pretty_printing()
    if get_length(thing) > twitter_character_limit:
        return 1
    return '\n'.join([stringify(line) for line in thing])

def get_length(one_d_string_array):
    return len('\n'.join([stringify(line) for line in one_d_string_array]))

print(pretty_print())