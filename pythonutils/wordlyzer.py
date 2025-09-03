"""
▗▖ ▗▖ ▗▄▖ ▗▄▄▖ ▗▄▄▄ ▗▖ ▗▖  ▗▖▗▄▄▄▄▖▗▄▄▄▖▗▄▄▖
▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌▐▌  █▐▌  ▝▚▞▘    ▗▞▘▐▌   ▐▌ ▐▌
▐▌ ▐▌▐▌ ▐▌▐▛▀▚▖▐▌  █▐▌   ▐▌   ▗▞▘  ▐▛▀▀▘▐▛▀▚▖
▐▙█▟▌▝▚▄▞▘▐▌ ▐▌▐▙▄▄▀▐▙▄▄▖▐▌  ▐▙▄▄▄▖▐▙▄▄▖▐▌ ▐▌

A script to "cheat" at Wordle.

On one hand, you can't really cheat at a game that doesn't have winners or losers and is
only a competition against yourself. On the other hand, it's totally cheating.

It was fun to write though. I encourage you to use your brain to solve the Wordle, but
explore your options with Wordlyzer afterwards.

To use, enter your current progress with letters in the places where you know the
letters and underscores where you don't. Then enter the letters you've eliminated.
Next enter the "Uncertain Letters", that is the letters that you know are included but
don't know the exact location of (they're highlighted yellow in the game) Finally, enter
whether you'd like to see spoilers. Seeing spoilers means the remaining words are printed
out. "No Spoilers" means it will just output a count of remaining words at the end.
"""

from english_dictionary.scripts.read_pickle import get_dict
import re

RE_FIVE_LETTERS_OR_UNDERSCORES = r"^[a-zA-Z_]{5}$"


def convert_input_string_to_regex(input_string):
    """
    Input: a string of exactly 5 characters. All characters must be either letters or underscores.
    Returns: a regex string replacing the underscores with wildcards
    """
    if not bool(re.match(RE_FIVE_LETTERS_OR_UNDERSCORES, input_string)):
        raise ValueError("Input string must be exactly 5 characters")

    re_string = "^" + input_string.lower() + "$"
    re_string = re_string.replace("_", "[a-z]")

    return re_string


def get_yn_as_bool(yn_prompt):
    while True:
        yn_input = input(yn_prompt)
        if len(yn_input) != 1 or yn_input.lower() not in ["y", "n"]:
            print("Spoilers? must be either Y or N")
        else:
            return yn_input.lower() == "y"


def prompt_for_valid_template_string(prompt):
    clarification = "Current Letters must be exactly 5 characters and only contain letters or underscores"
    while True:
        template_string = input(prompt)

        if not bool(re.match(RE_FIVE_LETTERS_OR_UNDERSCORES, template_string)):
            print(clarification)
        else:
            return template_string


def get_inputs():
    template_string = prompt_for_valid_template_string("Current letters: ")
    regex_string = convert_input_string_to_regex(template_string)
    eliminated = set(input("Eliminated letters: "))
    uncertain_letters = set(input("Uncertain Letters: "))
    spoilers = get_yn_as_bool("Spoilers? [Y/N]: ")

    return regex_string, eliminated, spoilers, uncertain_letters


if __name__ == "__main__":
    english_dict = get_dict()
    regex_string, eliminated, spoilers, uncertain_letters = get_inputs()
    match_count = 0

    for word in english_dict.keys():
        if len(word) == 5 and re.fullmatch(regex_string, word):
            letter_set = set(word)
            if letter_set.isdisjoint(eliminated) and (
                uncertain_letters == () or letter_set.issuperset(uncertain_letters)
            ):
                if spoilers:
                    print(f"{word}{english_dict[word]}")
                match_count += 1

    print("Remaining possible words: " + str(match_count))
