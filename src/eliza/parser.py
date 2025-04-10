import sys
from typing import Optional
import sexpdata
from sexpdata import Symbol, dumps
from .exceptions import ElizaScriptError
from .utils import REDIR_RE, PRE_RE, NEWKEY_RE
from .model import (
    ElizaEntry,
    ElizaRulesList,
    ElizaReassemblyList,
    ElizaRule,
    ElizaReassembly,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core import Eliza

# Some special keywords are not used in input scan
# They are marked during parsing by a rank == None 
special_keys = ["DIT", "XFREMD", "NONE"]

class ElizaScriptEntryError(ElizaScriptError):
    def __init__(self, entry):
        self.entry = entry
        super().__init__(f"Malformed entry: {dumps(entry)}")

class ElizaScriptRuleError(ElizaScriptError):
    def __init__(self, rule):
        self.rule = rule
        super().__init__(f"Malformed rule: {dumps(rule)}")

def parse_eliza_rules(rules_data: list[list],
                      context = None) -> ElizaRulesList:
    """Parses ELIZA rules data from a list and returns an ElizaRulesList."""
    
    rules_list = ElizaRulesList()

    for i, raw_rule in enumerate(rules_data):
        if not isinstance(raw_rule, list):
            raise ElizaScriptRuleError(rules_data)

        # Rule-level redirections: A single keyword in the last rule
        if raw_rule and all(isinstance(e, Symbol) for e in raw_rule):
            redirection = sexpdata.dumps(raw_rule)[1:-1].strip('= ')
            if ' ' in redirection or i < len(rules_data) - 1:
                raise ElizaScriptRuleError(rules_data)  # show all rules
            
            rules_list.append(ElizaRule.from_redirection(redirection, context))
            continue
        
        # Common rules:
        # One decomposition rule followed by one or more reassembly rules
        if len(raw_rule) < 2 or not all(isinstance(e, list) for e in raw_rule):
            raise ElizaScriptRuleError(raw_rule)
        
        pattern_str = sexpdata.dumps(raw_rule[0])[1:-1]
        reassembly_list = ElizaReassemblyList()
        
        for item in raw_rule[1:]:
            rr = sexpdata.dumps(item)[1:-1].strip()
            
            # 1) Check if it's just =SOMETHING
            m = REDIR_RE.match(rr)
            if m:
                reassembly_list.append(
                    ElizaReassembly.from_redirection(m.group(1))
                )
                continue

            # 2) Check if it's PRE (...) (=SOMETHING)
            m = PRE_RE.match(rr)
            if m:
                reassembly_list.append(
                    ElizaReassembly.from_preformat(m.group(1), m.group(2))
                )
                continue

            # 3) Check if it's NEWKEY
            m = NEWKEY_RE.match(rr)
            if m:
                reassembly_list.append(
                    ElizaReassembly.from_newkey()
                )
                continue

            # 4) Otherwise it's a plain "reassembly" text
            reassembly_list.append(
                ElizaReassembly.from_pattern(rr)
            )

        new_rule = ElizaRule.from_pattern(pattern_str, reassembly_list, context)
        
        rules_list.append(new_rule)

    return rules_list if rules_list else None


def parse_eliza_data(self: "Eliza", data: str) -> None:
    """Parses ELIZA script data from a string."""
    parsed_data = sexpdata.loads(f'({data})')

    for entry in parsed_data:
        # Symbol STOP or empty list '()' stops the parsing
        if ((isinstance(entry, Symbol) and str(entry) == "STOP")
            or (isinstance(entry, list) and not entry)):
            break;
        # A keyword without any meaning is an error
        if not (isinstance(entry, list) and len(entry) > 1):
            raise ElizaScriptEntryError(entry)
        # The first item has to be a Symbol
        if not isinstance(entry[0], Symbol):
            raise ElizaScriptEntryError(entry)
        
        key = str(entry[0])  # Keyword
        alias = None
        rank = None
        response_rules = None
        memory_rules = None

        # What we are looking for:
        # key ( DLIST (categories) | MEMORY (rule) ... | [= ALIAS] [rank] (rule) ... )
        
        # Check if this is a MEMORY entry
        if isinstance(entry[1], Symbol) and str(entry[1]) == "MEMORY":

            if not (len(entry) >= 3 and all(isinstance(e, list) for e in entry[2:])):
                raise ElizaScriptEntryError(entry)
            
            memory_rules = parse_eliza_rules(entry[2:], context=self.context)

            self.update_entry(key, memory_rules=memory_rules)
            continue

        index = 1  # Start checking the items at index 1

        # Check if the second item is "=" (indicating an alias)
        if (isinstance(entry[1], Symbol) and str(entry[1]) == "="):
            if not (len(entry) >= 3 and isinstance(entry[2], Symbol)):
                raise ElizaScriptEntryError(entry)

            alias = str(entry[2])  # entry[2] is the alias
            index = 3

        # Check if this is a DLIST entry
        if (len(entry) > index and isinstance(entry[index], Symbol)
            and str(entry[index]) == "DLIST"):
            
            if not (len(entry) == index + 2 and isinstance(entry[index+1], list)
                    and all(isinstance(item, str) for item in entry[index+1])):
                raise ElizaScriptEntryError(entry)
            
            for dlist_key in entry[index+1]:
                self.update_category(str(dlist_key), key)
            continue

        if len(entry) > index and isinstance(entry[index], int):
            rank = entry[index]
            index += 1  # Rules start on next index

        # Make sure, we have at least an alias or a rule
        if not (index > 2 or len(entry) > index):
            raise ElizaScriptEntryError(entry)
        
        # Unpack individual response rules
        response_rules = parse_eliza_rules(entry[index:], context=self.context)
                                           
         # Apply default rank for all but special keys
        if not rank and not key in special_keys:
            rank = 0

        # Store in dictionary as object
        self.update_entry(key, alias=alias, rank=rank,
                           response_rules=response_rules)
    

def parse_eliza_script(self: "Eliza", file_path: str) -> None:
    """Reads ELIZA script from a file and parses it."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    return parse_eliza_data(self, data)

# Example usage
if __name__ == "__main__":
    pass
