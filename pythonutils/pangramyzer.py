"""
██████╗  █████╗ ███╗   ██╗ ██████╗ ██████╗  █████╗ ███╗   ███╗██╗   ██╗███████╗███████╗██████╗
██╔══██╗██╔══██╗████╗  ██║██╔════╝ ██╔══██╗██╔══██╗████╗ ████║╚██╗ ██╔╝╚══███╔╝██╔════╝██╔══██╗
██████╔╝███████║██╔██╗ ██║██║  ███╗██████╔╝███████║██╔████╔██║ ╚████╔╝   ███╔╝ █████╗  ██████╔╝
██╔═══╝ ██╔══██║██║╚██╗██║██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║  ╚██╔╝   ███╔╝  ██╔══╝  ██╔══██╗
██║     ██║  ██║██║ ╚████║╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║   ██║   ███████╗███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝

"""

from english_dictionary.scripts.read_pickle import get_dict
import re
from nltk.corpus import words

# RE_FIVE_LETTERS_OR_UNDERSCORES = r"^[a-zA-Z]{7}$"
# RE_SEVEN_LETTERS = r"^[a-zA-Z]+$"
LETTERS_COUNT = 7
RE_SEVEN_LETTERS = r"^[a-zA-Z]{7}$"


def prompt_for_valid_template_string(prompt):
    clarification = (
        f"'Letters' must be exactly {LETTERS_COUNT} characters and only contain letters"
    )
    while True:
        input_string = input(prompt)

        if not len(set(input_string)) == LETTERS_COUNT or not bool(
            re.match(RE_SEVEN_LETTERS, input_string)
        ):
            print(clarification)
        else:
            return input_string.upper()


def get_inputs():
    letters_input = prompt_for_valid_template_string("Letters: ")

    return letters_input


if __name__ == "__main__":
    english_dict = get_dict()
    letters = get_inputs()
    letter_set = set(letters)
    match_found = False

    for word in words.words():  # english_dict.keys():
        if len(word) < LETTERS_COUNT and word[0] not in letter_set:
            continue
        else:
            word_set = set(word.upper())
            if word_set == letter_set:
                print(f"Pangram found: {word}")
                match_found = True
    if not match_found:
        print(f"No pangram found for {letters}")
