from discord import Message

from util import corpora, memory, parser
from util.analyzer import TABLE

OUTPUT = 10

def exec(message: Message):
    kwargs: dict[str, bool] = parser.get_kwargs(message, str, bad=bool)
    layout_name = kwargs['args']
    ll = memory.find(layout_name.lower())

    if not layout_name:
        tips = [
            'Usage: `redirects [layout_name] [--arg]`',
            "```",
            "no arg:",
            "    view all redirects of a layout",
            "--bad:",
            "    view bad redirects of a layout",
            "```"
        ]
        return '\n'.join(tips)

    arg = 'Redirect'
    if kwargs['bad']:
        arg = 'Bad-Redirect'

    trigrams = corpora.ngrams(3, id=message.author.id)
    total = sum(trigrams.values())

    red = {}
    for gram, count in trigrams.items():
        gram = gram.lower()

        if len(set(gram)) != len(gram): # ignore repeats
            continue

        key = '-'.join([ll.keys[x].finger for x in gram if x in ll.keys])

        if key in TABLE and TABLE[key].lower().endswith(arg.lower()):
            red[gram] = red.get(gram, 0) + count

    g_total = sum(count for (_, count) in red.items())

    res = []
    for ngram, count in red.items():
        res.append(f'{ngram:<6} {count / total:.3%}')

    return '\n'.join(['```', f'Top {OUTPUT} {ll.name} {arg}s:'] + res[:OUTPUT] + [f'Total: {g_total / total:.3%}'] + ['```'])

def use():
    return 'redirects [layout name] [--arg]'

def desc():
    return 'see the worst redirects for a particular layout'
