from discord import Message

from util import corpora, memory, parser
from util.analyzer import TABLE

def exec(message: Message):
    name = parser.get_arg(message)
    ll = memory.find(name.lower())

    trigrams = corpora.ngrams(3, id=message.author.id)
    total = sum(trigrams.values())

    outrolls = {}
    for gram, count in trigrams.items():
        gram = gram.lower()
        
        if len(set(gram)) != len(gram): # ignore repeats
            continue

        key = '-'.join([ll.keys[x].finger for x in gram if x in ll.keys])

        if key in TABLE and TABLE[key].startswith('roll-out'):
            outrolls[gram] = outrolls.get(gram, 0) + count

    g_total = sum(count for (_, count) in outrolls.items()) / total

    res = []
    format_len = f'{len(f"{g_total:.3%}")}'
    for ngram, count in outrolls.items():
        res.append(f'{ngram:<{format_len}} {count / total:.3%}')

    return '\n'.join(['```', f'Top 10 {ll.name} Outrolls:'] + res[:10] + [f'Total: {g_total:.3%}'] + ['```'])

def use():
    return 'outrolls [layout name]'

def desc():
    return 'see the highest inrolls for a particular layout'
