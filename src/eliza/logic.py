import regex as re
from .utils import SPLIT_REGEX, WORD_RE
from .exceptions import ElizaScriptError
from typing import TYPE_CHECKING
if TYPE_CHECKING: from .core import Eliza

def scan_for_keywords(self: "Eliza", part_sentence: str) -> tuple[str, bool]:
    """
    Tokenizes a part sentence, scans it for keywords and applies
    alias-based substitutions to it.

    :param part_sentence: A part sentence to scan and transform.
    :return: The transformed input sentence and a flag that signals
    wheter or not a keyword was found.
    """
    #tokens = re.findall(r"\b\w+(?:'\w+)?", part_sentence.upper())
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


def resolve_redirection(self: "Eliza", entry):
    """
    Follows redirections for an dictionary entry and returns the final resolved entry.
    Raises ElizaScriptError if a circular redirection is detected
    or if a redirection target is missing.
    """
    visited = set()
    while entry and entry.redirection:
        redirection = entry.redirection
        if redirection in visited:
            path = " -> ".join(list(visited) + [redirection])
            raise ElizaScriptError(f"Circular redirection detected: {path}")
        visited.add(redirection)
        entry = self.dictionary.get(redirection)
        if not entry:
            raise ElizaScriptError(f"Redirection '{redirection}' does not exist.")
    return entry


def get_response_logic(self: "Eliza", user_input: str, debug: bool = False) -> str:
    """
    Tokenizes user input, builds keystack, and returns a response.
    """
    #part_sentences = re.split(r'[.,;:!?]+(?=\s)', user_input)
    part_sentences = SPLIT_REGEX.split(user_input)

    for part in part_sentences:
        part_clean = part.strip()
        if not part_clean:
            continue
        
        reflected_input, found = scan_for_keywords(self, part_clean)
        if found:
            break

    if not found and 'NONE' in self.dictionary:
        self.keystack.append(('NONE', 0))
        
    if debug:
        print(f"reflected_input: {reflected_input}")
        print(f"keystack: {str(self.keystack)}")
    
    response = ""   # default fallback
    while self.keystack: # means while len(self.keystack) > 0
        key, _ = self.keystack.pop()
        entry = self.dictionary.get(key)
        if debug:
            print(f" key: {key}")

        entry = resolve_redirection(self, entry)
        
        for rule in entry.response_rules:
            if debug:
                print(f"  rule.pattern: {rule.pattern}")

            if rule.pattern[0] == "=":
                redirection = rule.pattern.strip('= ')
                # entry = self.dictionary.get(redirection)
                # break # oops, that is suspect
            
            match = rule.regex.fullmatch(reflected_input)
            if match:
                groups = match.groups() # tuple
                response_format, capture_indices = rule.reassembly_list().template
                selected_groups = ([re.sub(r"\s+", " ", groups[i-1]) if groups[i-1]
                                    is not None else ""
                                   for i in capture_indices])
                if debug:
                    print(f"  selected_groups: {selected_groups}")
                response = response_format.format(*selected_groups)
                break
        else:
            continue
        break

    self.keystack.clear()
    
    return response
