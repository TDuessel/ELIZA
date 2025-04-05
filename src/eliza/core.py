# TODO: detect and handle leading "=" in rules
# TODO: understand and handle the PRE symbol
# TODO: handle the (* ored lists) in rules
from __future__ import annotations
import regex as re
from typing import Optional, List, Union
from textwrap import indent
from collections import deque
from . import parser, logic
from .utils import INDENT, autogen_repr, fmt
from .model import (
    ElizaKeystack,
    ElizaCategories,
    ElizaContext,
    ElizaDictionary,
    ElizaEntry
)
# from .parser import parse_eliza_data, parse_eliza_script
# from .logic import get_response_logic

@autogen_repr
class Eliza():
    def __init__(self, script_data=None, script_path=None):
        self.keystack = ElizaKeystack()
        self.categories = ElizaCategories()
        self.context = ElizaContext(self.categories)
        self.dictionary = ElizaDictionary()
        if script_data:
            self.parse_data(script_data)
        if script_path:
            self.parse_script(script_path)
            
    def __str__(self):
        dict_str = fmt(self.dictionary)
        cate_str = fmt(self.categories)
        keyst_str = fmt(self.keystack)
        return (f"ELIZA Dictionary:\n{indent(dict_str, INDENT)}\n"
                f"ELIZA Categories:\n{indent(cate_str, INDENT)}\n"
                f"ELIZA Keystack:\n{indent(keyst_str, INDENT)}")
    
    def update_entry(self, key, **kwargs):
        # If key is not present
        if key not in self.dictionary:
            if any(value is not None for value in kwargs.values()):
                self.dictionary[key] = ElizaEntry(**kwargs)
        else:
            self.dictionary[key].update(**kwargs)

    def update_category(self, key, item):
        # If key is not present
        if key not in self.categories:
            self.categories[key] = [item]
        else:
            self.categories[key].append(item)

    parse_script = parser.parse_eliza_script
    parse_data = parser.parse_eliza_data
    get_response = logic.get_response_logic  # Attach as method

