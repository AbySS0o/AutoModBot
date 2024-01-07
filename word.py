import string
import itertools
import pymorphy2


def morph(word: str):
    word = word.lower().translate(str.maketrans('', '', string.punctuation))
    word = ''.join(i for i, _ in itertools.groupby(word))
    morph = pymorphy2.MorphAnalyzer()
    parsed_token = morph.parse(word)
    normal_form = parsed_token[0].normal_form
    print(normal_form)
    return normal_form