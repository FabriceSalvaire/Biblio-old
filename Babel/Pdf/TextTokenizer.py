####################################################################################################
# 
# Babel - A Bibliography Manager 
# Copyright (C) Salvaire Fabrice 2013 
# 
####################################################################################################

"""
"""

# word: [a-zA-z\-]+[0-9]*
#   - could be cesure or hyphenation
#   . as in "e.g." "fig."
# 
# number:
#   integer: [0-9]+
#     thousand separator "123 456"
#   float: [0-9]+.[0-9]+
#     ".1" "0.2"
#     French convention "1,2"
# 
# punctuation:
#   terminal: . ? !
#   speparator: , ; :
# 
# group: ()

####################################################################################################

import unicodedata

####################################################################################################

from Babel.Tools.EnumFactory import EnumFactory

####################################################################################################

class Token(object):

    Category = EnumFactory('TokenCategory', ('word',
                                             'number',
                                             'punctuation',
                                             'space',
                                             'symbol',
                                             ))

    ##############################################

    def __init__(self, category, text):

        self._category = category
        self._text = unicode(text)

    ##############################################

    @property
    def category(self):
        return self._category

    ##############################################

    @property
    def is_word(self) :
        return self._category == Token.Category.word

    ##############################################

    @property
    def is_number(self) :
        return self._category == Token.Category.number

    ##############################################

    @property
    def is_punctuation(self) :
        return self._category == Token.Category.punctuation

    ##############################################

    @property
    def is_space(self) :
        return self._category == Token.Category.space

    ##############################################

    @property
    def is_symbol(self) :
        return self._category == Token.Category.symbol

    ##############################################

    def __unicode__(self):

        return self._text

    ##############################################

    def __len__(self):

        return len(self._text)

    ##############################################

    def __repr__(self):

        return 'Token %s:"%s"' % (unicode(self._category), self._text)

####################################################################################################

class TokenisedText(list):

    ##############################################

    def word_iterator(self):

        """ Iterate over words. """

        for token in self:
            if token.category == Token.Category.word:
                yield token

    ##############################################

    def word_number_iterator(self):

        """ Iterate over word and number. """

        for token in self:
            if token.category in (Token.Category.word, Token.Category.number):
                yield token

    ##############################################

    def count_word_number(self):

        """ Count the number of words and numbers. """

        # Fixme: iterator doesn't have len method
        counter = 0
        for token in self.word_number_iterator():
            counter += 1

        return counter

####################################################################################################

class TextTokenizer(object):

    State = EnumFactory('LexerState', ('letter',
                                       'number',
                                       'special',
                                       ))

    ##############################################

    def lex(self, text):

        state = None
        word = u''
        tokenised_text = TokenisedText()

        def initial_transition(category, char):
            if category in ('Ll', 'Lu'):
                state = TextTokenizer.State.letter
                word = char
            elif category == 'Nd':
                state = TextTokenizer.State.number
                word = char
            else:
                if category == 'Zs':
                    token_category = Token.Category.space
                elif category in ('Po', 'Pd'):
                    token_category = Token.Category.punctuation
                # Ps Pe e.g. ()
                else:
                    token_category = Token.Category.symbol
                tokenised_text.append(Token(token_category, char))
                state = None
                word = u''
            return state, word

        for char in text:
            category = unicodedata.category(char)
            # print '>', char, category, state, word
            if state is None:
                state, word = initial_transition(category, char)
            else:
                if state == TextTokenizer.State.letter:
                    if category in ('Ll', 'Lu', 'Nd'):
                        word += char
                    else:
                        tokenised_text.append(Token(Token.Category.word, word))
                        state, word = initial_transition(category, char)
                elif state == TextTokenizer.State.number:
                    if category == 'Nd':
                        word += char
                    else:
                        tokenised_text.append(Token(Token.Category.number, word))
                        state, word = initial_transition(category, char)
        if word:
            if state == TextTokenizer.State.letter:
                tokenised_text.append(Token(Token.Category.word, word))
            elif state == TextTokenizer.State.number:
                tokenised_text.append(Token(Token.Category.number, word))

        return tokenised_text

####################################################################################################

def strip_word_list(word_list):

    """ Return a word list where the leading and trailing spaces was removed. """

    lower_index = 0
    while True:
        if word_list[lower_index].is_space:
            lower_index += 1
        else:
            break
    upper_index = len(word_list) -1
    while True:
        if word_list[upper_index].is_space:
            upper_index -= 1
        else:
            break

    return word_list[lower_index:upper_index +1]

####################################################################################################

def join_tokens(tokens):
    return ''.join([unicode(token) for token in tokens])

####################################################################################################
# 
# End
# 
####################################################################################################
