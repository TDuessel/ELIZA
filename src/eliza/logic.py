import regex as re
from .utils import SPLIT_REGEX, WORD_RE
from .exceptions import ElizaScriptError
from .model import ElizaEntry

from typing import TYPE_CHECKING, List, cast
if TYPE_CHECKING:
    from .core import Eliza

def scan_for_keywords(self: "Eliza", part_sentence: str) -> tuple[str, bool]:
    """
    Tokenizes a part sentence, scans it for keywords and applies
    alias-based substitutions to it.

    :param part_sentence: A part sentence to scan and transform.
    :return: The transformed input sentence and a flag that signals
    wheter or not a keyword was found.
    """

    tokens = WORD_RE.findall(part_sentence.upper())
    toprank = 0
    found_keyword = False

    for i, token in enumerate(tokens):
        entry = self.dictionary.get(token)
        if entry and entry.rank is not None:
            rank = entry.rank
            
            if entry.alias:
                tokens[i] = entry.alias

            if entry.redirection or entry.response_rules:
                found_keyword = True
                if rank >= toprank:
                    self.keystack.push((token, rank))
                    toprank = rank
                else:
                    self.keystack.append((token, rank))
                
    return " ".join(tokens), found_keyword


def resolve_redirection(self: "Eliza",
                        entry: ElizaEntry,
                        visited_keys: List[str],
                        debug: bool = False) -> ElizaEntry:
    """
    Follows redirections for an dictionary entry and returns the final resolved entry.
    Raises ElizaScriptError if a circular redirection is detected
    or if a redirection target is missing.
    """

    while entry and entry.redirection:
        redirection = entry.redirection
        if redirection in visited_keys:
            path = " -> ".join(visited_keys + [redirection])
            raise ElizaScriptError(f"Circular redirection detected: {path}")
        visited_keys.append(redirection)
        entry = self.dictionary.get(redirection)
        if not entry:
            raise ElizaScriptError(f"Redirection '{redirection}' does not exist.")
        if debug:
            print(f" → Entry-level redirection to '{redirection}'")

    return entry


def process_keyword_entry(self: "Eliza",
                          key: str,
                          reflected_input: str,
                          visited_keys: List[str],
                          debug: bool = False) -> str | None:
    """
    Resolves redirection and rules for a given keyword.
    Returns a response if a rule matches, otherwise None.
    Prevents circular rule-level redirections.
    """
    if key in visited_keys:
        path = " -> ".join(visited_keys + [key])
        raise ElizaScriptError(f"Circular rule-level redirection detected: {path}")
    visited_keys.append(key)

    entry = self.dictionary.get(key)
    if not entry:
        raise ElizaScriptError(f"Keyword '{key}' does not exist in the dictionary.")

    entry = resolve_redirection(self, entry, visited_keys, debug)

    for rule in entry.response_rules:
        if debug:
            print(f"  rule.pattern: {rule.pattern}")

        # Normal pattern matching
        match = rule.regex.fullmatch(reflected_input)
        if match:
            groups = match.groups()
            response_format: str
            capture_indices: list[int]
            # reassembly_list as callable returns entries in round-robin manner
            response_format, capture_indices = rule.reassembly_list().template

            # Handle rule-level redirection like '=OTHERKEY'
            if response_format.startswith("="):
                redirection_target = response_format.strip("= ")
                if debug:
                    print(f"   → Rule-level redirection to '{redirection_target}'")
                response = process_keyword_entry(self, redirection_target,
                                                 reflected_input, visited_keys, debug)
                if response:
                    return response
                else:
                    continue  # try next rule if redirected-to entry didn't match

            # Handle the NEWKEY special reassembly rule
            elif response_format == "NEWKEY":
                return None
            
            selected_groups = ([re.sub(r"\s+", " ", groups[i-1]) if groups[i-1]
                                is not None else ""
                               for i in capture_indices])
            if debug:
                print(f"   ↳ Matched. Groups: {selected_groups}")
            return response_format.format(*selected_groups)

    return None  # No rule matched

def get_response_logic(self: "Eliza", user_input: str, debug: bool = False) -> str:
    """
    Tokenizes user input, builds keystack, and returns a response.
    """
    part_sentences = SPLIT_REGEX.split(user_input)

    reflected_input = ""
    found = None
    response = None
    
    for part in part_sentences:
        part_clean = part.strip()
        if not part_clean:
            continue
        
        reflected_input, found = scan_for_keywords(self, part_clean)
        if found:
            break

    # A special keyword NONE should be in the dictionary
    # and it should be terminal, i.e. without redirections
    # and with a proper catch all (0) rule.
    if 'NONE' in self.dictionary:
        self.keystack.append(('NONE', 0))
    
    if debug:
        print(f"reflected_input: {reflected_input}")
        print(f"keystack: {str(self.keystack)}")
    
    while self.keystack:
        key, _ = self.keystack.pop()
        if debug:
            print(f" key: {key}")
        response = process_keyword_entry(self, key, reflected_input, visited_keys=list(), debug=debug)
        if response:
            break  # response found

    self.keystack.clear()
    return response or "I ShoULd NoT sAy tHIs;)"
