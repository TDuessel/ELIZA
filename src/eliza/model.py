# TODO: detect and handle leading "=" in rules
# TODO: understand and handle the PRE symbol
# TODO: handle the (* ored lists) in rules
from __future__ import annotations
import regex as re
from typing import Optional, List, Union
from textwrap import indent
from collections import deque
from .utils import INDENT, autogen_repr, fmt

from . import rules

class ElizaContext:
    def __init__(self, categories: ElizaCategories):
        self.categories = categories
        # Add more shared stuff here if needed (logger, memory stack, etc.)

    def __repr__(self):
        return f"<ElizaContext categories={len(self.categories)}>"

class ElizaDictionary(dict[str, "ElizaEntry"]):
    def __str__(self):
        return '\n'.join(f"{k}:\n{indent(str(v), INDENT)}" for k, v in self.items())
    
class ElizaCategories(dict[str, List[str]]):
    def __str__(self):
        return '\n'.join(f"{k}:\n{indent(str(v), INDENT)}" for k, v in self.items())

@autogen_repr
class ElizaEntry():
    def __init__(self,
                 alias: Optional[str] = None,
                 rank: Optional[int] = None,
                 redirection: Optional[str] = None,
                 response_rules: Optional[ElizaRulesList] = None,
                 memory_rules: Optional[ElizaRulesList] = None):

        self.alias = None
        self.rank = None
        self.redirection = None
        self.response_rules = ElizaRulesList()
        self.memory_rules = ElizaRulesList()
        self.update(alias=alias, rank=rank, redirection=redirection,
                    response_rules=response_rules, memory_rules=memory_rules)
    
    def __str__(self):
        return (f"{self.alias}, {self.rank}, {self.redirection},\n"
                f"{self.response_rules},\n{self.memory_rules}")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                if key in {'response_rules', 'memory_rules'}:
                    if not isinstance(value, ElizaRulesList):
                        raise TypeError("Expected ElizaRulesList")
                setattr(self, key, value)

    
class ElizaRulesList(list["ElizaRule"]):
    def __str__(self):
        return "["+',\n'.join(str(elem) for elem in self)+"]"

@autogen_repr
class ElizaRule():
    """Docstring"""
    def __init__(self,
                 pattern: str,
                 reassembly_list: Optional[ElizaReassemblyList] = None,
                 context: Optional[ElizaContext] = None):
        
        self.pattern = pattern
        self.reassembly_list = ElizaReassemblyList()
        self._compiled_regex = None
        self.context = context
        self.update(reassembly_list=reassembly_list)

    def __str__(self):
        return (f"['{self.pattern}',\n"
                f"{self.reassembly_list}]")

    # This one might be a little bit over the top,
    # but it allows for easy integration of future attributes.
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                if key in {'reassembly_list'}:
                    if not isinstance(value, ElizaReassemblyList):
                        raise TypeError("Expected ElizaReassemblyList")
                setattr(self, key, value)

    def add_reassembly(self, reassembly):
        self.reassembly_list.append(reassembly)

    @property
    def regex(self):
        # Lazy compile and cache
        if self._compiled_regex is None:
            pattern_str = self.to_regex()
            self._compiled_regex = re.compile(pattern_str, re.IGNORECASE)
        return self._compiled_regex

    # instance method to build the regex from the pattern
    to_regex = rules.drule_to_regex
    

class ElizaMemoryRule(ElizaRule):
    def __init__(self, pattern, reassembly_list=None):
        super().__init__(pattern, reassembly_list)
    
class ElizaReassemblyList(list["ElizaReassembly"]):
    def __init__(self, *args):
        super().__init__(*args)
        self._index = 0

    def __str__(self):
        return "["+',\n '.join("'"+str(elem)+"'" for elem in self)+"]"

    def __call__(self):
        return self.next()

    def next(self):
        if not self:
            raise IndexError("No reassembly rules available.")

        item = self[self._index]
        self._index = (self._index + 1) % len(self)
        return item

@autogen_repr
class ElizaReassembly():
    def __init__(self, reassembly: str):
        self.reassembly = reassembly
        self._format: Optional[str] = None
        self._indices: Optional[list[int]] = None
        
    def __str__(self):
        return f"{self.reassembly}"

    @property
    def template(self) -> tuple[str, list[int]]:
        # Lazy format and collect indices
        if self._format is None:
            self._format, self._indices = self.to_template()
        assert self._format is not None and self._indices is not None
        return self._format, self._indices

    # instance method to build the template
    to_template = rules.rrule_to_template
    
class ElizaKeystack:
    def __init__(self):
        self._stack = deque()
        self._seen_keys = set()
        
    def __repr__(self):
        return f"{self.__class__.__name__}({list(self._stack)})"

    def __str__(self):
        return ', '.join(f"{key} ({rank})" for key, rank in self)

    def __len__(self):
        return len(self._stack)

    def __iter__(self):
        return iter(self._stack)

    def push(self, item: tuple[str, int]) -> None:
        """Push to the top of the stack if not already present."""
        key, _ = item
        if key not in self._seen_keys:
            self._stack.appendleft(item)
            self._seen_keys.add(key)

    def append(self, item: tuple[str, int]) -> None:
        """Push to the bottom of the stack if not already present."""
        key, _ = item
        if key not in self._seen_keys:
            self._stack.append(item)
            self._seen_keys.add(key)

    def pop(self) -> tuple[str, int]:
        """Pop from the top of the stack and update seen_keys."""
        key, rank = self._stack.popleft()
        self._seen_keys.discard(key)
        return key, rank

    def clear(self):
        self._stack.clear()
        self._seen_keys.clear()

if __name__ == "__main__":
    pass
