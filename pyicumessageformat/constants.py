CHAR_OPEN = '{'
CHAR_CLOSE = '}'
CHAR_TAG_OPEN = '<'
CHAR_TAG_CLOSE = '/'
CHAR_TAG_END = '>'
CHAR_SEP = ','
CHAR_HASH = '#'
CHAR_ESCAPE = "'"

OFFSET = 'offset:'

VAR_CHARS = [
    CHAR_OPEN,
    CHAR_CLOSE
]

TAG_CHARS = [
    CHAR_TAG_OPEN,
    CHAR_TAG_CLOSE,
    CHAR_TAG_END
]

TAG_CLOSING = '/>'
TAG_END = '</'

SPACE_CHARS = [
    0x20,
    0x85,
    0xA0,
    0x180E,
    0x2028,
    0x2029,
    0x202F,
    0x205F,
    0x2060,
    0x3000,
    0xFEFF
]

CLOSE_TAG = {}
