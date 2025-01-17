import pytest

from pyicumessageformat import Parser

## Setup

parser = Parser()
tag_parser = Parser({'allow_tags': True})

def token(type, text):
    return {
        'type': type,
        'text': text
    }

def tNumber(text):
    return token('number', str(text))

def tSelector(text):
    return token('selector', text)

def tStyle(text):
    return token('style', text)

def tType(text):
    return token('type', text)

def tSyntax(text):
    return token('syntax', text)

def tText(text):
    return token('text', text)

def tName(text):
    return token('name', text)

tOpen = tSyntax('{')
tClose = tSyntax('}')
tTagOpen = tSyntax('<')
tTagEnd = tSyntax('>')
tTagOpenClosing = tSyntax('</')
tTagClosing = tSyntax('/>')
tSep = tSyntax(',')
tSpace = token('space', ' ')
tOffset = token('offset','offset:')
tHash = token('hash', '#')

def tokensToString(tokens):
    return ''.join(x['text'] for x in tokens)

def parse(input, tokens = None):
    out = parser.parse(input, tokens)
    if tokens:
        assert tokensToString(tokens) == input
    return out

def parseTags(input, tokens = None):
    out = tag_parser.parse(input, tokens)
    if tokens:
        assert tokensToString(tokens) == input
    return out


## The Tests

def test_hello_world():
    tokens = []
    assert parse('Hello, World!', tokens) == ['Hello, World!']
    assert tokens == [
        tText('Hello, World!')
    ]

def test_hello_name():
    tokens = []
    assert parse('Hello, {name}!', tokens) == ['Hello, ', {'name': 'name'}, '!']
    assert tokens == [
        tText('Hello, '),
        tOpen,
            tName('name'),
        tClose,
        tText('!')
    ]

def test_n_number():
    tokens = []
    assert parse('{n, number}', tokens) == [{'name': 'n', 'type': 'number'}]
    assert tokens == [
        tOpen,
            tName('n'),
            tSep,
            tSpace,
            tType('number'),
        tClose
    ]

def test_n_number_percent():
    tokens = []
    assert parse('{num, number, percent }', tokens) == [{
        'name': 'num',
        'type': 'number',
        'format': 'percent'
    }]
    assert tokens == [
        tOpen,
            tName('num'),
            tSep,
            tSpace,
            tType('number'),
            tSep,
            tSpace,
            tStyle('percent'),
            tSpace,
        tClose
    ]

def test_plural_photos():
    tokens = []
    assert parse('{numPhotos, plural, =0{no photos} =1{one photo} other{# photos}}', tokens) == [{
        'name': 'numPhotos',
        'type': 'plural',
        'offset': 0,
        'options': {
            '=0': ['no photos'],
            '=1': ['one photo'],
            'other': [
                {'name': 'numPhotos', 'type': 'number'},
                ' photos'
            ]
        }
    }]
    assert tokens == [
        tOpen,
            tName('numPhotos'),
            tSep,
            tSpace,
            tType('plural'),
            tSep,
            tSpace,
            tSelector('=0'),
            tOpen,
                tText('no photos'),
            tClose,
            tSpace,
            tSelector('=1'),
            tOpen,
                tText('one photo'),
            tClose,
            tSpace,
            tSelector('other'),
            tOpen,
                tHash,
                tText(' photos'),
            tClose,
        tClose
    ]

def test_plural_offset():
    tokens = []
    assert parse('{numGuests, plural, offset:1 =0{no party} one{host and a guest} other{# guests}}', tokens) == [{
        'name': 'numGuests',
        'type': 'plural',
        'offset': 1,
        'options': {
            '=0': ['no party'],
            'one': ['host and a guest'],
            'other': [
                {'name': 'numGuests', 'type': 'number'},
                ' guests'
            ]
        }
    }]
    assert tokens == [
        tOpen,
            tName('numGuests'),
            tSep,
            tSpace,
            tType('plural'),
            tSep,
            tSpace,
            tOffset,
            tNumber(1),
            tSpace,
            tSelector('=0'),
            tOpen,
                tText('no party'),
            tClose,
            tSpace,
            tSelector('one'),
            tOpen,
                tText('host and a guest'),
            tClose,
            tSpace,
            tSelector('other'),
            tOpen,
                tHash,
                tText(' guests'),
            tClose,
        tClose
    ]

def test_negative_offset():
    tokens = []
    assert parse('{n, plural, offset:-12 other{x}}', tokens) == [{
        'name': 'n',
        'type': 'plural',
        'offset': -12,
        'options': {
            'other': ['x']
        }
    }]
    assert tokens == [
        tOpen,
            tName('n'),
            tSep,
            tSpace,
            tType('plural'),
            tSep,
            tSpace,
            tOffset,
            tNumber(-12),
            tSpace,
            tSelector('other'),
            tOpen,
                tText('x'),
            tClose,
        tClose
    ]

def test_no_weird_offset():
    tokens = []
    with pytest.raises(SyntaxError, match='Expected {'):
        parse('{n, plural, offset:1-2 other{x}}', tokens)

    assert tokens == [
        tOpen,
            tName('n'),
            tSep,
            tSpace,
            tType('plural'),
            tSep,
            tSpace,
            tOffset,
            tNumber(1),
            tSelector('-2'),
            tSpace
    ]

def test_ordinal():
    tokens = []
    assert parse('{rank, selectordinal, one {#st} two {#nd} few {#rd} other {#th}}', tokens) == [{
        'name': 'rank',
        'type': 'selectordinal',
        'offset': 0,
        'options': {
            'one': [
                {'name': 'rank', 'type': 'number'},
                'st'
            ],
            'two': [
                {'name': 'rank', 'type': 'number'},
                'nd'
            ],
            'few': [
                {'name': 'rank', 'type': 'number'},
                'rd'
            ],
            'other': [
                {'name': 'rank', 'type': 'number'},
                'th'
            ]
        }
    }]
    assert tokens == [
        tOpen,
            tName('rank'),
            tSep,
            tSpace,
            tType('selectordinal'),
            tSep,
            tSpace,
            tSelector('one'),
            tSpace,
            tOpen,
                tHash,
                tText('st'),
            tClose,
            tSpace,
            tSelector('two'),
            tSpace,
            tOpen,
                tHash,
                tText('nd'),
            tClose,
            tSpace,
            tSelector('few'),
            tSpace,
            tOpen,
                tHash,
                tText('rd'),
            tClose,
            tSpace,
            tSelector('other'),
            tSpace,
            tOpen,
                tHash,
                tText('th'),
            tClose,
        tClose
    ]

def test_select():
    tokens = []
    assert parse('{gender, select, female {woman} male {man} other {person}}', tokens) == [{
        'name': 'gender',
        'type': 'select',
        'options': {
            'female': ['woman'],
            'male': ['man'],
            'other': ['person']
        }
    }]
    assert tokens == [
        tOpen,
            tName('gender'),
            tSep,
            tSpace,
            tType('select'),
            tSep,
            tSpace,
            tSelector('female'),
            tSpace,
            tOpen,
                tText('woman'),
            tClose,
            tSpace,
            tSelector('male'),
            tSpace,
            tOpen,
                tText('man'),
            tClose,
            tSpace,
            tSelector('other'),
            tSpace,
            tOpen,
                tText('person'),
            tClose,
        tClose
    ]

def test_custom_one():
    tokens = []
    assert parse('{a, custom, one}', tokens) == [{
        'name': 'a',
        'type': 'custom',
        'format': 'one'
    }]
    assert tokens == [
        tOpen,
            tName('a'),
            tSep,
            tSpace,
            tType('custom'),
            tSep,
            tSpace,
            tStyle('one'),
        tClose
    ]

def test_weird_tags():
    tokens = []
    assert parse('{<0/>,</>,void}', tokens) == [{
        'name': '<0/>',
        'type': '</>',
        'format': 'void'
    }]
    assert tokens == [
        tOpen,
            tName('<0/>'),
            tSep,
            tType('</>'),
            tSep,
            tStyle('void'),
        tClose
    ]

def test_weird_with_tags():
    tokens = []
    assert parseTags('{<0/>,</>,void}', tokens) == [{
        'name': '<0/>',
        'type': '</>',
        'format': 'void'
    }]
    assert tokens == [
        tOpen,
            tName('<0/>'),
            tSep,
            tType('</>'),
            tSep,
            tStyle('void'),
        tClose
    ]

def test_loose_submessages():
    x = Parser({
        'loose_submessages': True
    })

    input = '{a,<,>{click here}}'
    tokens = []
    assert x.parse(input, tokens) == [{
        'name': 'a',
        'type': '<',
        'options': {
            '>': ['click here']
        }
    }]
    assert tokensToString(tokens) == input
    assert tokens == [
        tOpen,
            tName('a'),
            tSep,
            tType('<'),
            tSep,
            tSelector('>'),
            tOpen,
                tText('click here'),
            tClose,
        tClose
    ]

def test_loose_other():
    x = Parser({
        'loose_submessages': True,
        'require_other': 'all'
    })

    with pytest.raises(SyntaxError, match='Expected < sub-message other'):
        x.parse('{a,<,>{click here}}')

def test_no_loose():
    tokens = []
    with pytest.raises(SyntaxError, match='Expected }'):
        parse('{a,<,>{click here}}', tokens)

    assert tokens == [
        tOpen,
            tName('a'),
            tSep,
            tType('<'),
            tSep,
            tStyle('>')
    ]

def test_loose_with_tags():
    x = Parser({
        'loose_submessages': True,
        'allow_tags': True
    })

    input = '{a,<,>{click here}}'
    tokens = []
    assert x.parse(input, tokens) == [{
        'name': 'a',
        'type': '<',
        'options': {
            '>': ['click here']
        }
    }]
    assert tokensToString(tokens) == input
    assert tokens == [
        tOpen,
            tName('a'),
            tSep,
            tType('<'),
            tSep,
            tSelector('>'),
            tOpen,
                tText('click here'),
            tClose,
        tClose
    ]


def test_ignore_brackets():
    tokens = []
    assert parse('</close>', tokens) == ['</close>']
    assert tokens == [tText('</close>')]

def test_simple_xml():
    tokens = []
    assert parseTags('<a><i/>here</a>', tokens) == [{
        'name': 'a',
        'type': 'tag',
        'contents': [
            {'name': 'i', 'type': 'tag'},
            'here'
        ]
    }]
    assert tokens == [
        tTagOpen,
            tName('a'),
        tTagEnd,
        tTagOpen,
            tName('i'),
        tTagClosing,
        tText('here'),
        tTagOpenClosing,
            tName('a'),
        tTagEnd
    ]

def test_escape_xml():
    tokens = []
    assert parseTags('\'<a><i/>\'here\'</a>\'', tokens) == ['<a><i/>here</a>']
    assert tokens == [
        tText('\'<a><i/>\'here\'</a>\'')
    ]

def test_escaping():
    assert parse("'{'", []) == ['{']
    assert parse("'}'", []) == ['}']
    assert parse("''", []) == ["'"]
    assert parse("'{'''", []) == ["{'"]
    assert parse('#', []) == ['#']
    assert parse("'", []) == ["'"]
    assert parse("{0} '{1}' {2}", []) == [
        {'name': '0'},
        ' {1} ',
        {'name': '2'}
    ]
    assert parse("{0} '{1} {2}", []) == [
        {'name': '0'},
        ' {1} {2}'
    ]
    assert parse("{0} ''{1} {2}", []) == [
        {'name': '0'},
        " '",
        {'name': '1'},
        ' ',
        {'name': '2'}
    ]
    assert parse("So, '{Mike''s Test}' is real.", []) == ["So, {Mike's Test} is real."]
    assert parse("You've done it now, {name}.", []) == [
        "You've done it now, ",
        {'name': 'name'},
        '.'
    ]
    assert parse("{n,plural,other{#'#'}}", []) == [{
        'name': 'n',
        'type': 'plural',
        'offset': 0,
        'options': {
            'other': [
                {'name': 'n', 'type': 'number'},
                '#'
            ]
        }
    }]

def test_escape_format():
    tokens = []
    assert parse("{n,date,'a style'}", tokens) == [{
        'name': 'n',
        'type': 'date',
        'format': 'a style'
    }]
    assert tokens == [
        tOpen,
            tName('n'),
            tSep,
            tType('date'),
            tSep,
            tStyle("'a style'"),
        tClose
    ]

def test_mixed_tags_placeholders():
    tokens = []
    assert parseTags('Our price is <boldThis>{price, number, ::currency/USD precision-integer }</boldThis> with <link>{pct, number, ::percent} discount</link>', tokens) == [
        'Our price is ',
        {
            'name': 'boldThis',
            'type': 'tag',
            'contents': [
                {
                    'name': 'price',
                    'type': 'number',
                    'format': '::currency/USD precision-integer'
                }
            ]
        },
        ' with ',
        {
            'name': 'link',
            'type': 'tag',
            'contents': [
                {
                    'name': 'pct',
                    'type': 'number',
                    'format': '::percent'
                },
                ' discount'
            ]
        }
    ]
    assert tokens == [
        tText('Our price is '),
        tTagOpen,
            tName('boldThis'),
        tTagEnd,
            tOpen,
                tName('price'),
                tSep,
                tSpace,
                tType('number'),
                tSep,
                tSpace,
                tStyle('::currency/USD precision-integer'),
                tSpace,
            tClose,
        tTagOpenClosing,
            tName('boldThis'),
        tTagEnd,
        tText(' with '),
        tTagOpen,
            tName('link'),
        tTagEnd,
            tOpen,
                tName('pct'),
                tSep,
                tSpace,
                tType('number'),
                tSep,
                tSpace,
                tStyle('::percent'),
            tClose,
            tText(' discount'),
        tTagOpenClosing,
            tName('link'),
        tTagEnd
    ]

def test_throws_extra_close():
    with pytest.raises(SyntaxError, match='Unexpected "}"'):
        parse('}')

def test_throws_no_close():
    with pytest.raises(SyntaxError, match='Expected , or }'):
        parse('{a')

def test_throws_empty_placeholder():
    with pytest.raises(SyntaxError, match='Expected placeholder name'):
        parse('{}')

def test_throws_open_brace_placeholder():
    with pytest.raises(SyntaxError, match='Expected , or }'):
        parse('{n{')

def test_throws_missing_type():
    with pytest.raises(SyntaxError, match='Expected placeholder type'):
        parse('{n,}')

def test_throws_ends_type():
    with pytest.raises(SyntaxError, match='Expected placeholder type'):
        parse('{n,')

def test_throws_open_brace_after_type():
    with pytest.raises(SyntaxError, match='Expected , or }'):
        parse('{n,d{')

def test_throws_missing_style():
    with pytest.raises(SyntaxError, match='Expected placeholder style'):
        parse('{n,t,}')

def test_throws_empty_style():
    with pytest.raises(SyntaxError, match='Expected placeholder style'):
        parse('{n,t,  }')

def test_throws_missing_submessage_select():
    with pytest.raises(SyntaxError, match='Expected select sub-messages'):
        parse('{n,select}')

def test_throws_missing_submessage_selectordinal():
    with pytest.raises(SyntaxError, match='Expected selectordinal sub-messages'):
        parse('{n,selectordinal}')

def test_throws_missing_submessage_plural():
    with pytest.raises(SyntaxError, match='Expected plural sub-messages'):
        parse('{n,plural}')

    with pytest.raises(SyntaxError, match='Expected plural sub-message other'):
        parse('{n,plural,one{# thing}}')

def test_throws_missing_other_select():
    with pytest.raises(SyntaxError, match='Expected select sub-messages'):
        parse('{n,select,}')

def test_throws_missing_other_selectordinal():
    with pytest.raises(SyntaxError, match='Expected selectordinal sub-messages'):
        parse('{n,selectordinal,}')

def test_throws_missing_other_plural():
    with pytest.raises(SyntaxError, match='Expected plural sub-messages'):
        parse('{n,plural,}')

def test_throws_missing_selector():
    with pytest.raises(SyntaxError, match='Expected sub-message selector'):
        parse('{n,select,{a}}')

def test_throws_missing_submessage_open():
    with pytest.raises(SyntaxError, match='Expected {'):
        parse('{n,select,other a}')

def test_throws_missing_submessage_close():
    with pytest.raises(SyntaxError, match='Expected }'):
        parse('{n,select,other{a')

def test_throws_missing_offset_number():
    with pytest.raises(SyntaxError, match='Expected offset number'):
        parse('{n,plural,offset:}')

def test_throws_missing_closing_brace():
    with pytest.raises(SyntaxError, match='Expected }'):
        parse('{a,b,c')

def test_throws_missing_tag_id():
    with pytest.raises(SyntaxError, match='Expected tag name'):
        parseTags('<>')

def test_throws_missing_tag_end():
    with pytest.raises(SyntaxError, match='Expected > or />'):
        parseTags('<a')

def test_throws_open_tag():
    with pytest.raises(SyntaxError, match='Expected </'):
        parseTags('<a>')

def test_throws_missing_end_tag_end():
    with pytest.raises(SyntaxError, match='Expected >'):
        parseTags('<a></a')

def test_throws_invalid_close_tag():
    with pytest.raises(SyntaxError, match='Unexpected "</"'):
        parseTags('</a>')

def test_throws_mismatch_tag():
    with pytest.raises(SyntaxError, match='Expected </a>'):
        parseTags('<a></b>')

def test_custom_require_other():
    x = Parser({
        'require_other': ['plural']
    })

    assert x.parse('{n,select,cake{lie}}')

    with pytest.raises(SyntaxError, match='Expected plural sub-message other'):
        x.parse('{n,plural,one{two}}')

    x = Parser({
        'require_other': 'subnumeric'
    })

    assert x.parse('{n,select,cake{lie}}')

    with pytest.raises(SyntaxError, match='Expected plural sub-message other'):
        x.parse('{n,plural,one{two}}')

    x = Parser({
        'require_other': False
    })

    assert x.parse('{n,select,cake{lie}}')
    assert x.parse('{n,plural,one{two}}')
