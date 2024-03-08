import re

from discord import Message

from util import corpora, parser

RESTRICTED = True

def get_reverse(ngram):
    return ngram[::-1]

def calculate_freq(item, ngrams):
    pattern = re.compile(item.replace('.', '\.').replace('_', '.'))
    count = sum(value for key, value in ngrams.items() if pattern.search(key))
    return count / sum(ngrams.values())

def exec(message: Message):
    id = message.author.id
    query = parser.get_args(message)

    ntype = len(query[0]) if len(query) > 0 else None

    if not query or ntype != 2:
        return "Please provide at least 1 ngram that is 2 char"

    if len(query) > 3:
        return "Please provide no more than 3 ngrams"

    corpus = corpora.get_corpus(id)
    res = ['```', f'{corpus.upper()}']

    processed_ngrams = set()
    freqs = [0] * (len(corpora.NGRAMS) - 2)

    for item in query:
        if len(item) != ntype:
            return 'All ngrams must be the same length'

        rev = get_reverse(item)

        if item in processed_ngrams or (ntype > 1 and rev in processed_ngrams):
            continue

        for i in range(len(corpora.NGRAMS) - 2):
            ngrams = corpora.ngrams(i + 2, id=id)
            gram = item[:1] + "_" * i + item[1:]
            rgram = get_reverse(gram)
            freq_gram = calculate_freq(gram, ngrams)
            freq_rgram = calculate_freq(rgram, ngrams)
            freq_grams = freq_gram + freq_rgram

            if i < len(freqs): 
                freqs[i] += freq_gram + freq_rgram
            else: 
                freqs.insert(i, freq_gram + freq_rgram)

            res.extend([
                f'{gram} + {rgram}: {freq_grams:.2%}',
                f'  {gram}: {freq_gram:.2%}',
                f'  {rgram}: {freq_rgram:.2%}',
            ])

        processed_ngrams.update({item, rev})

    if len(query) == 1 or all(item == query[0] or get_reverse(item) == query[0] for item in query):
        res.append('```')
    elif len(query) > 1:
        max_len = max(len(ngram_type.capitalize()) for ngram_type in corpora.NGRAMS[1:-1])
        for i in range(1, len(corpora.NGRAMS) - 1):
            ngram_type = corpora.NGRAMS[i]
            spaces = ' ' * (max_len - len(ngram_type) + 1)
            res.extend([f'{ngram_type.capitalize()}:{spaces}{freqs[i - 1]:.2%}'])
        res.append('```')
    return '\n'.join(res)
