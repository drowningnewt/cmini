import re

from discord import Message

from util import corpora, parser

RESTRICTED = True

def exec(message: Message):
    id = message.author.id
    query = parser.get_args(message)

    if not query or not all(len(item) == 2 for item in query):
        return "Please provide bigrams"

    if len(query) > 6:
        return "Please provide no more than 6 bigrams"

    corpus = short_corpus(id, 7)
    start = f' {corpus.upper()}' + ' ' * (8 - len(corpus))
    res = ['```', start]

    max_ngram = len(corpora.NGRAMS)
    processed_ngrams = set()
    freqs = []

    dividers = f'{"-" * len(start)}{("-" * 8) * max_ngram}'

    for item in query:
        rvrs = get_reverse(item)

        if item in processed_ngrams or rvrs in processed_ngrams:
            continue

        res.append(dividers)
        
        # Add ngram and its reverse to the result; if it's a double letter, forgo reverse
        if item != rvrs:
            res.extend([f' {item} + {rvrs} ',
                        f'   {item}    ',
                        f'   {rvrs}    '])
        else: 
            res.append(f'   {item}    ')

        # Calculate frequencies for each ngram size
        for i in range(max_ngram):
            ngrams = corpora.ngrams(i + 2, id=id)
            ogram = item[:1] + "_" * i + item[1:]
            rgram = get_reverse(ogram)
            freq_ogram = calculate_freq(ogram, ngrams)
            freq_rgram = calculate_freq(rgram, ngrams)
            freq_grams = freq_ogram + (freq_rgram if item != rvrs else 0)

            if i < len(freqs): 
                freqs[i] += freq_grams
            else: 
                freqs.append(freq_grams)

            if not processed_ngrams:
                res[1] += f'| x{"_" * i}x{" " * (6 - len(ogram))}'
            if item != rvrs:
                res[-3] += f'| {freq_grams:.2%} '
                res[-2] += f'| {freq_ogram:.2%} '
                res[-1] += f'| {freq_rgram:.2%} '
            else: 
                res[-1] += f'| {freq_ogram:.2%} '
        
        processed_ngrams.update({item, rvrs})

    # Add total frequencies if multiple bigrams are provided
    if len(query) > 1:
        res.extend([dividers, f' total   '])
        res[-1] += ''.join([f'| {freq:.2%} ' for freq in freqs])
    res.append('```')
    return '\n'.join(res)

def get_reverse(ngram):
    return ngram[::-1]

def calculate_freq(item, ngrams):
    pattern = re.compile(item.replace('.', '\.').replace('?', '\?').replace('_', '.'))
    count = sum(value for key, value in ngrams.items() if pattern.search(key))
    return count / sum(ngrams.values())

def short_corpus(id: int, length: int):
    name = corpora.get_corpus(id)

    replacements = {"monkey": "m", "racer": "r", "type": "t", "-quotes": ""}

    for key, value in replacements.items():
        if key in name:
            name = name.replace(key, value)

    if name.startswith("english-"):
        name = "e" + name[len("english-"):]
    elif "-" in name:
        parts = name.split("-")
        name = f'{parts[0][0]}-{parts[1][0]}'

    if len(name) > length:
        name = name[:length]

    return name
