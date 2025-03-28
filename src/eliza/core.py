# TODO: detect and handle leading "=" in rules
# TODO: understand and handle the PRE symbol
# TODO: handle the (* ored lists) in rules
from __future__ import annotations
import regex as re
from typing import Optional, List, Union
from textwrap import indent
from collections import deque
from eliza.rules import drule_to_regex, rrule_to_fstring
from eliza.logic import get_response_logic
from eliza.utils import INDENT, autogen_repr, fmt

class ElizaScriptError(Exception):
    """Exception raised for errors in the ELIZA script."""
    pass

@autogen_repr
class Eliza():
    def __init__(self, script_path=None):
        self.dictionary = ElizaDictionary()
        self.categories = ElizaCategories()
        self.keystack = ElizaKeystack()
        if script_path:
            # Avoid circular import
            from .parser import parse_eliza_script
            parse_eliza_script(script_path, eliza=self)
            
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

    get_response = get_response_logic  # Attach as method


class ElizaFormattedDict(dict):
    def __str__(self):
        return '\n'.join(f"{k}:\n{indent(str(v), INDENT)}" for k, v in self.items())

class ElizaDictionary(ElizaFormattedDict): pass
class ElizaCategories(ElizaFormattedDict): pass

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

class ElizaRulesList(list):
    def __str__(self):
        return "["+',\n'.join(str(elem) for elem in self)+"]"

@autogen_repr
class ElizaRule():
    def __init__(self,
                 pattern: str,
                 reassembly_list: Optional[ElizaReassemblyList] = None):
        
        self.pattern = pattern
        self.reassembly_list = ElizaReassemblyList()
        self._compiled_regex = None
        
        self.update(reassembly_list=reassembly_list)

    @property
    def regex(self):
        # Lazy compile and cache
        if self._compiled_regex is None:
            pattern_str = drule_to_regex(self.pattern)
            self._compiled_regex = re.compile(pattern_str, re.IGNORECASE)
        return self._compiled_regex

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

class ElizaMemoryRule(ElizaRule):
    def __init__(self, pattern, reassembly_list=None):
        super().__init__(pattern, reassembly_list)
    
class ElizaReassemblyList(list):
    def __str__(self):
        return "["+',\n '.join("'"+str(elem)+"'" for elem in self)+"]"

@autogen_repr
class ElizaReassembly():
    def __init__(self, reassembly):
        self.reassembly = reassembly

    @property
    def compiled_template(self):
        return rrule_to_fstring(self.reassembly)

    def __str__(self):
        return f"{self.reassembly}"

class ElizaKeystack:
    def __init__(self):
        self._stack = deque()

    def push(self, item: tuple[str, int]):
        """Push to the top of the stack."""
        self._stack.appendleft(item)

    def append(self, item: tuple[str, int]):
        """Push to the bottom of the stack."""
        self._stack.append(item)

    def pop(self) -> tuple[str, int]:
        """Pop from the top of the stack."""
        return self._stack.popleft()

    def clear(self):
        self._stack.clear()

    def __len__(self):
        return len(self._stack)

    def __iter__(self):
        return iter(self._stack)

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self._stack)})"

    def __str__(self):
        return ', '.join(f"{key} ({rank})" for key, rank in self)

if __name__ == "__main__":
    pass
