"""
This module integrates language filtering capabilities with a Telegram bot
"""
import functools

from telegram.ext.filters import MessageFilter
from telegram.ext import filters

from common.exceptions import LanguageFilterError

class LanguageFilter:
    """Class for filtering language in messages received by a Telegram bot"""
    KEY_PHRASES_FILE_PATH = "../resources/key.txt"
    BAN_PHRASES_FILE_PATH = "../resources/ban.txt"
    WORD_LENGTH_LIMIT = 20
    MESSAGE_LENGTH_LIMIT = 90

    def __init__(self):
        self.key_words = self.__load_words_from_file(self.KEY_PHRASES_FILE_PATH)
        self.banned_words = self.__load_words_from_file(self.BAN_PHRASES_FILE_PATH)

    def check_for_inappropriate_language(self, message: str) -> bool:
        """Checks if the message was using inappropriate language"""
        words = set(message.lower().split())
        if words.intersection(self.banned_words):
            return True
        return False

    def check_for_message_length(self, message: str) -> bool:
        """Checks if the message complies with lengths limitations"""
        maximum_word_length = len(max(set(message.lower().split()), key=len))
        message_length = len(message)
        breaks_word_length_limit = maximum_word_length > self.WORD_LENGTH_LIMIT
        breaks_message_length_limit = message_length > self.MESSAGE_LENGTH_LIMIT
        return breaks_word_length_limit or breaks_message_length_limit

    def construct_message_filter(self) -> MessageFilter:
        """Constructs message filter for Telegram bot to trigger"""
        regex_filters = [filters.Regex(key_word) for key_word in self.key_words]
        return functools.reduce(lambda f1, f2: f1 | f2, regex_filters)

    def detect_prompt(self, message: str) -> str:
        """Returns possible prompt defined in the message"""
        matched_key_words = [
            key_word for key_word in self.key_words if message.startswith(key_word)
        ]
        if not matched_key_words:
            raise LanguageFilterError(
                f"No key word was found for the message {message}", "detect", "No match")

        return matched_key_words[0].split(' ')[-1] + message.split(matched_key_words[0])[1]

    def __load_words_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return set(file.read().splitlines())
