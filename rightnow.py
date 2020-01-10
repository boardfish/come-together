import os
import pronouncing
import random
import logging
from twython import Twython, TwythonError
import time

APP_KEY = os.environ.get('TWYTHON_APP_KEY')
APP_SECRET = os.environ.get('TWYTHON_APP_SECRET')
OAUTH_TOKEN = os.environ.get('TWYTHON_OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.environ.get('TWYTHON_OAUTH_TOKEN_SECRET')

twitter_character_limit = 280

pronouns = ["he", "she", "they", "we"]
verbs = ["come", "got", "one", "wear", "shoot", "say", "bag", "go", "bought"]

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

feet_down = [
  "hair down to his knee",
  "I know you you know me",
  "feet down below his knee",
  "one and one and one is three",
]

armchairs = [
  "got to be a joker he just do what he please",
  "one thing I can tell you is you got to be free",
  "hold you in his armchair you can feel his disease",
  "got to be good looking coz he's so hard to see"
]

def generate_he_got(min_syllables = 2):
    he_got = random.choice(pronouns)
    give_two = random.randint(0, 1)
    syllables = 1
    if min_syllables > 1 or give_two == 1:
        he_got += ' ' + random.choice(verbs)
        syllables += 1
    return [syllables, he_got]

# Typical syllable limit is 4, first line is 5 inc. he

def total_syllables_in_string(text):
    try:
        phones = [pronouncing.phones_for_word(p)[0] for p in text.split()]
        return sum([pronouncing.syllable_count(p) for p in phones])
    except IndexError:
        logging.error("Syllables could not be found for %s.", text)
        return False
    
def count_syllables_for_word(word):
  return pronouncing.syllable_count(pronouncing.phones_for_word(word)[0])

def rhymes_with_same_syllables(word):
  syllable_count = count_syllables_for_word(word)
  rhymes = pronouncing.rhymes(word)
  return list(filter(lambda w: count_syllables_for_word(w) == syllable_count, rhymes))

def choose_rhyme_with_same_syllables(word):
  rhymes_with_same_syllables_for_word = rhymes_with_same_syllables(word)
  if len(rhymes_with_same_syllables_for_word) > 0:
    return (random.choice(rhymes_with_same_syllables_for_word))
  return word

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
# Type = 0: first, 1: mid, 2: last (extra he_got), 3: break (two lines before COME TOGETHER)
def determine_syllable_limit(he_got, first):
    syllables_in_he_got = he_got[0]
    words = he_got[1].split()
    if first:
        if syllables_in_he_got == 2 and words[1] == "come":
            return 7
        else:
            return 5
    else:
        return 6

def generate_line(type = 1):
    if type == 3:
        return generate_feet_down()
    first = type == 0
    random_he_got = generate_he_got(1 if first else 2)
    syllable_limit = determine_syllable_limit(random_he_got, first)
    syllable_limit -= random_he_got[0]
    output_array = [random_he_got[1], generate_joo_joo_eyeball(syllable_limit)]
    if type == 2:
        output_array += [generate_he_got(2)[1]]
    return output_array

def generate_feet_down():
    text = [random.choice(feet_down), random.choice(armchairs)]
    return([' '.join([choose_rhyme_with_same_syllables(word) for word in line.split()]) for line in text])

# Generates a full verse. Comes out as an array of arrays of strings.
def generate_verse():
    return [generate_line(first) for first in [0, 1, 1, 2, 3]]

# Splits a verse as made by generate_verse as follows:
# he_got, joo_joo_eyeball, he got
# joo_joo_eyeball, he got
# joo_joo_eyeball, he got
# joo_joo_eyeball, he got
def split_for_pretty_printing():
    verse = generate_verse()
    flattened_verse = [words for phrase in verse for words in phrase]
    first_line = flattened_verse[:3]
    other_lines = flattened_verse[3:-2]
    other_lines_paired = list(zip(other_lines[::2], other_lines[1::2]))
    return [first_line] + other_lines_paired + [verse[-1]]

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
        raise TweetTooLongError
    return '\n'.join([stringify(line) for line in thing[:-1]] + [line.capitalize() for line in thing[-1]])

def get_length(thing):
    return len('\n'.join([stringify(line) for line in thing[:-1]] + [line.capitalize() for line in thing[-1]]))

def tweet_one():
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    print ("Tweeting...")
    try:
        verse = pretty_print()
        twitter.update_status(status=verse)
    except TweetTooLongError as e:
        print(e)
    except TwythonError as e:
        print(e)

class TweetTooLongError(Exception):
    """Raised when the generated verse is too long to fit in a tweet"""
    pass

tweet_one()
