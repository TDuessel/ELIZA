# utils.py
import logging
import sys
from typing import Any, Type, TypeVar
import regex as re

INT = r'\d+'

# Define apostrophes to support: straight and curly
APOSTROPHES = r"['’]"  # U+0027 and U+2019

# MVP Definition of a "word"
# Matches: basic words, apostrophes, accents, etc.
WORD = fr"(?:\p{{L}}+(?:{APOSTROPHES}\p{{L}}+)*)"

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

#REDIR_RE = re.compile(r'^=\s*(\S+)\s*$')
REDIR_RE = re.compile(fr'^=\s*({WORD})\s*$')

# PRE rule detection an capturing of preformatter and redirection target
PRE_RE = re.compile(r"^PRE\s*\(\s*(.*?)\s*\)\s*\(\s*=\s*(.*?)\s*\)$")
#PRE_FULL_RE = re.compile(r'^PRE\s*\((.*)\)\s*=\s*(\S+)\s*$')

NEWKEY_RE = re.compile(r'^NEWKEY$')

SWORD = fr"(?:\p{{L}}+(?:\\{APOSTROPHES}\p{{L}}+)*)"
LISTWORD = rf"\(\s*[\/\*]?\s*{SWORD}(?:\s+{SWORD})*\s*\)"
VALID_DECO = re.compile(
    rf"""^
        (?:
            {INT}(?!\s+{INT})    # INT not followed by another INT
          |
            {SWORD}
          |
            {LISTWORD}
        )
        (?:\s+
            (?:
                {INT}(?!\s+{INT})
              |
                {SWORD}
              |
                {LISTWORD}
            )
        )*
    $""",
    re.VERBOSE
)

# Default indentation for hierachical __str__
INDENT = '  '

T = TypeVar("T")

def autogen_repr(cls: Type[T]) -> Type[T]:
    def __repr__(self: Any) -> str:
        attrs = ', '.join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
    cls.__repr__ = __repr__  # type: ignore[method-assign]
    return cls

def fmt(obj: Any) -> str: return str(obj) or "None"

def clean_response(response: str) -> str:
    return response.replace('\\', '')
