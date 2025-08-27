import pytest
from pythonutils.wordlyzer import convert_input_string_to_regex
import re

@pytest.mark.parametrize("input_string,expected_regex", [
    ("abcde", "^abcde$"),
    ("a_c_e", "^a[a-z]c[a-z]e$"),
    ("_____", "^[a-z][a-z][a-z][a-z][a-z]$"),
    ("A_C_E", "^a[a-z]c[a-z]e$"),
])
def test_convert_input_string_to_regex_valid(input_string, expected_regex):
    assert convert_input_string_to_regex(input_string) == expected_regex

@pytest.mark.parametrize("input_string", [
    "abcd",      # Too short
    "abcdef",    # Too long
    "abc1e",     # Contains digit
    "abc$e",     # Contains symbol
    "abc e",     # Contains space
    "abce__",    # Contains extra underscore
])
def test_convert_input_string_to_regex_invalid(input_string):
    with pytest.raises(ValueError):
        convert_input_string_to_regex(input_string)

# def test_word_filtering_logic():  TODO AMM - I think this is just replicating my code, and not really a valid test case
#     # Simulate a small dictionary
#     english_dict = {
#         'apple': None,
#         'angle': None,
#         'amble': None,
#         'alien': None,
#         'baker': None,
#         'cider': None,
#     }
#     # Test case: known letters 'a__le', eliminated 'b', spoilers True
#     regex_string = convert_input_string_to_regex('a__le')
#     eliminated = set('b')
#     possible_words = [
#         word for word in english_dict.keys()
#         if len(word) == 5 and re.fullmatch(regex_string, word)
#         and set(word).isdisjoint(eliminated)
#     ]
#     assert 'apple' in possible_words
#     assert 'amble' in possible_words
#     assert 'angle' in possible_words
#     assert 'alien' not in possible_words
#     assert 'baker' not in possible_words
#     assert 'cider' not in possible_words
#     assert len(possible_words) == 3

def test_prompt_for_valid_template_string_valid(monkeypatch):
    # Simulate valid input
    monkeypatch.setattr('builtins.input', lambda _: 'abcde')
    from pythonutils.wordlyzer import prompt_for_valid_template_string
    assert prompt_for_valid_template_string('Prompt:') == 'abcde'

@pytest.mark.parametrize("inputs", [
    (['abcd', 'abcde']),   # Too short, then valid
    (['abcdef', 'abcde']), # Too long, then valid
    (['abc1e', 'abcde']),  # Invalid char, then valid
])
def test_prompt_for_valid_template_string_invalid_then_valid(monkeypatch, inputs):
    # Simulate invalid then valid input
    input_iter = iter(inputs)
    monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
    from pythonutils.wordlyzer import prompt_for_valid_template_string
    assert prompt_for_valid_template_string('Prompt:') == 'abcde'

@pytest.mark.parametrize("user_input,expected", [
    ('y', True),
    ('Y', True),
    ('n', False),
    ('N', False),
])
def test_get_yn_as_bool_valid(monkeypatch, user_input, expected):
    monkeypatch.setattr('builtins.input', lambda _: user_input)
    from pythonutils.wordlyzer import get_yn_as_bool
    assert get_yn_as_bool('Spoilers?') == expected

@pytest.mark.parametrize("inputs,expected", [
    (['x', 'y'], True),
    (['', 'n'], False),
    (['maybe', 'Y'], True),
])
def test_get_yn_as_bool_invalid_then_valid(monkeypatch, inputs, expected):
    input_iter = iter(inputs)
    monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
    from pythonutils.wordlyzer import get_yn_as_bool
    assert get_yn_as_bool('Spoilers?') == expected

# Integration test for get_inputs

def test_get_inputs(monkeypatch):
    # Simulate: valid template, eliminated letters, spoilers
    responses = iter(['abcde', 'xyz', 'y'])
    monkeypatch.setattr('builtins.input', lambda _: next(responses))
    from pythonutils.wordlyzer import get_inputs
    regex_string, eliminated, spoilers = get_inputs()
    assert regex_string == '^abcde$'
    assert eliminated == set('xyz')
    assert spoilers is True
