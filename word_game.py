#!/usr/bin/env python3
""" Countdown word game solver in Python """


import sys
import math
import pickle
import os.path
import itertools
import urllib.error
import urllib.request


class WordGame:
    """WordGame: Class for countdown word game which stores
    the max and min length for words to be output
    """
    def __init__(self):
        if not os.path.exists('.search_space.b'):
            pickle.dump(tuple({0, 0}), open('.search_space.b', 'wb'), -1)
        self.search_space = pickle.load(open('.search_space.b', 'rb'))

    def preprocess_dictionary_file(self, search_space=tuple({0, math.inf})):
        """Pre-process: Uses the pickle module to create a dictionary
        of which the keys are the sorted word, and the value is a tuple of words which when
        sorted would create the key
        """
        if search_space == self.search_space and os.path.exists('.processed_words.b'):
            return
        self.search_space = search_space
        pickle.dump(self.search_space, open('.search_space.b', 'wb', -1))

        if not os.path.exists('English Words.txt'):
            self.get_dictionary_file()

        with open('English Words.txt') as file:
            valid_words = dict()
            dictionary_words = file.readlines()

            for test_word in dictionary_words:
                if "'" in test_word or (len(test_word) > self.search_space[1] + 1) or \
                        (len(test_word) < self.search_space[0] + 1):
                    continue

                test_word = ''.join(test_word.strip().lower())
                sorted_word = ''.join(sorted(test_word.strip().lower()))

                if sorted_word not in valid_words:
                    valid_words[sorted_word] = [test_word]
                else:
                    valid_words[sorted_word].append(test_word)

            for key, value in valid_words.items():
                valid_words[key] = tuple(value)
            pickle.dump(valid_words, open('.processed_words.b', 'wb'), -1)

    def fetch_valid_words(self):
        """fetch_valid_words: Use pickle to fetch the already pre-processed
        dictionary
        """
        if not os.path.exists('.processed_words.b'):
            self.preprocess_dictionary_file()

        return pickle.load(open('.processed_words.b', 'rb'))

    def solve(self, word):
        """solve: Use the already pre-processed dictionary and combinations to
        find all valid anagrams for 'word'

        :param word: string which you want to find the anagrams for
        """
        word = word.lower()
        anagrams = set()
        valid_words = self.fetch_valid_words()
        for size in range(1, 10):
            for combined_letters in itertools.combinations(''.join(sorted(word)), size):
                sorted_combination = ''.join(combined_letters)
                if sorted_combination in valid_words:
                    for valid_word in valid_words[sorted_combination]:
                        anagrams.add(valid_word)
        return anagrams

    @classmethod
    def get_dictionary_file(cls):
        """get_dictionary_file: Uses urllib to fetch a dictions file from
        http://www-01.sil.org/linguistics/wordlists/english/wordlist/wordsEN.txt
        this file contains around 120,000 valid words
        """
        for _ in range(3):
            try:
                url = 'http://www-01.sil.org/linguistics/wordlists/english/wordlist/wordsEN.txt'
                urllib.request.urlretrieve(url, 'English Words.txt', reporthook=cls.report)
                return
            except urllib.error.URLError as error:
                print(error)
        sys.exit(1)

    @classmethod
    def report(cls, blocknum, blocksize, totalsize):
        """report: Report pregress when downloading. Full disclosure
        I didn't write this
        """
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = min(readsofar * 1e2 / totalsize, 100)
            status = "\r%5.1f%% %*d / %d" % (
                percent, len(str(totalsize)), readsofar, totalsize)
            sys.stderr.write(status)
            if readsofar >= totalsize:
                sys.stderr.write("\n")
        else:
            sys.stderr.write("read %d\n" % (readsofar,))


def main():
    """main: Command line useage of Morse class
    """
    parser = argparse.ArgumentParser(description='Simple Countdown "Word Game" solver')
    parser.add_argument('-w', '--word', action="store", type=str,
                        help='Generate anagrams for input')
    parser.add_argument('-s', '--search-space', action='store', type=int, nargs='*',
                        help='Maximum word length')
    parser.add_argument('-u', '--update-dictionary', action='store_true',
                        help='Download latest version of the dictionary')
    parser.add_argument('-p', '--preprocess_dictionary', action='store_true',
                        help='Pre-process dictionary the file')
    arguments = parser.parse_args()

    game = WordGame()

    if arguments.update_dictionary:
        game.get_dictionary_file()
        game.preprocess_dictionary_file()

    if arguments.search_space:
        if arguments.search_space[0] > arguments.search_space[1]:
            raise ValueError('Min > Max!')
        game.preprocess_dictionary_file(arguments.search_space)

    if arguments.preprocess_dictionary:
        game.preprocess_dictionary_file()

    if arguments.word:
        anagrams = sorted(game.solve(arguments.word), key=len, reverse=True)
        print('Searching for words between {0} and {1}'.format(game.search_space[0],
                                                               game.search_space[1]))
        for index, anagram in enumerate(anagrams):
            print('{0}: {1} - {2}'.format(index + 1, len(anagram), anagram))


if __name__ == '__main__':
    import argparse
    main()
