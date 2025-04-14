import pytest
from eliza.utils import WORD_RE

@pytest.mark.parametrize("input_text,expected_tokens", [
    # Simple words
    ("Hello there", ["HELLO", "THERE"]),

    # Contractions
    ("I don't know", ["I", "DON'T", "KNOW"]),
    ("You'll see", ["YOU'LL", "SEE"]),

    # Accented characters
    ("niño crème brûlée", ["NIÑO", "CRÈME", "BRÛLÉE"]),

    # Mixed casing
    ("eLiZa KnOwS", ["ELIZA", "KNOWS"]),

    # Unicode apostrophes
    ("I’m fine", ["I’M", "FINE"]),

    # Emo-styled text
    ("y’all rock’n’roll", ["Y’ALL", "ROCK’N’ROLL"]),

    # No matches (just punctuation)
    ("?!... ,;", []),

    # Embedded punctuation
    ("Don't... you think?!", ["DON'T", "YOU", "THINK"]),
])
@pytest.mark.smoke
def test_word_tokenizer(input_text, expected_tokens):
    tokens = WORD_RE.findall(input_text.upper())
    assert tokens == expected_tokens
