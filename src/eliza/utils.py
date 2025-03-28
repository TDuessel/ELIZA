# utils.py
import regex as re

# Define apostrophes to support: straight and curly
APOSTROPHES = r"['’]"  # U+0027 and U+2019

# MVP Definition of a "word"
# Matches: basic words, apostrophes, accents, etc.
WORD = fr"(?:\p{{L}}+(?:{APOSTROPHES}\p{{L}}+)*|\p{{N}}+)"

# Explanation:
# - \p{L}+ : one or more Unicode letters (covers a-z, A-Z, and non-English letters like é, ñ)
# - (?:'\p{L}+)? : optional apostrophe + letters (for contractions like don't)
# - \p{N}+ : allows numbers as standalone words (optional, remove if not needed)

# Export precompiled pattern for performance
WORD_RE = re.compile(WORD)

# Sentence splitter for "end of thought" splitting
# Does not remove punctuation at the very end of a sentence.
# That is done by the tokenizer afterwards.
SPLIT_REGEX = re.compile(r"[.?!,:;]+(?=\s)")

# Default indentation for hierachical __str__
INDENT = '  '

def autogen_repr(cls):
    def __repr__(self):
        attrs = ', '.join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
    cls.__repr__ = __repr__
    return cls

def fmt(obj): return str(obj) or "None"
