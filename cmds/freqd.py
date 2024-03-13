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

    if len(query) > 6:
        return "Please provide no more than 6 ngrams"

    corpus = corpora.short_corpus(id, 7)
    start = f' {corpus.upper()}' + ' ' * (8 - len(corpus))
    alt = ['```', start]

    processed_ngrams = set()
    freqs = []

    intersection = f'{"-" * len(start)}{("-" * 8) * (len(corpora.NGRAMS) - 1)}'

    for item in query:
        if len(item) != ntype:
            return 'All ngrams must be the same length'

        rvrs = get_reverse(item)

        if item in processed_ngrams or rvrs in processed_ngrams:
            continue
        alt.append(intersection)
        if item != rvrs:
            alt.extend([f' {item} + {rvrs} ',
                        f'   {item}    ',
                        f'   {rvrs}    '])
        else: 
            alt.append(f' {item}      ')

        for i in range(len(corpora.NGRAMS) - 1):
            ngrams = corpora.ngrams(i + 2, id=id)
            ogram = item[:1] + "_" * i + item[1:]
            rgram = get_reverse(ogram)
            freq_ogram = calculate_freq(ogram, ngrams)
            freq_rgram = calculate_freq(rgram, ngrams)
            freq_grams = freq_ogram + freq_rgram

            if i < len(freqs): 
                freqs[i] += freq_ogram + freq_rgram if item != rvrs else freq_ogram
            else: 
                freqs.insert(i, freq_ogram + freq_rgram if item != rvrs else freq_ogram)

            if not processed_ngrams:
                alt[1] += f'| x{"_" * i}x{" " * (6 - len(ogram))}'
            if item != rvrs:
                alt[-3] += f'| {freq_grams:.2%} '
                alt[-2] += f'| {freq_ogram:.2%} '
                alt[-1] += f'| {freq_rgram:.2%} '
            else: 
                alt[-1] += f'| {freq_ogram:.2%} '
        
        processed_ngrams.update({item, rvrs})

    if len(query) == 1 or all(item == query[0] or get_reverse(item) == query[0] for item in query):
        alt.append('```')
    elif len(query) > 1:
        alt.extend([intersection, 
                    f' total   '])
        for i, freq in enumerate(freqs):
            alt[-1] += f'| {freq:.2%} '
        alt.append('```')
    return '\n'.join(alt)
