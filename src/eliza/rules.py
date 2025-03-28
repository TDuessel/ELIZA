import regex as re
import sexpdata
from .utils import WORD

def _parse_option_list(self, entry):
    """Parses (* foo bar) or (/TAG) entries."""
    if not isinstance(entry, list) or not entry:
        return None

    first = str(entry[0])
    rest = entry[1:]

    # Handle leading symbol in first token OR as prefix of first word
    if first == "*" or first.startswith("*"):
        options = [str(e) for e in rest] if first == "*" else [first[1:]] + [str(e) for e in rest]
        return r"\b(" + "|".join(re.escape(opt) for opt in options) + r")\b"

    if first == "/" or first.startswith("/"):
        tag = first[1:] if first.startswith("/") else str(entry[1])
        options = self.context.categories.get(tag.upper(), [])
        return r"\b(" + "|".join(re.escape(opt) for opt in options) + r")\b"

    return None

def drule_to_regex(self) -> str:
    """
    Method for ElizaRule.
    
    ElizaRule.drule_to_regex(self) -> str
    
    Converts a decomposition rule into a regex pattern for matching input text.

    Variable tokens:
    - "0" matches any number of words (non-greedy), including empty
    - "1" matches exactly one word
    - "N" matches exactly N words

    Literal tokens are treated case-insensitively and escaped.

    :param drule: Decomposition rule string like "0 YOUR 0"
    :return: Regex pattern string
    """
    regex_parts = []

    # Parse the rule using sexpdata
    try:
        parsed_data = sexpdata.loads(f"({self.pattern})")
    except Exception as e:
        raise ValueError(f"Invalid S-expression in rule: {self.pattern!r}\n{e}")
    
    for entry in parsed_data:
        if isinstance(entry, list):
            parsed = self._parse_option_list(entry)
            if parsed:
                regex_parts.append(parsed)
                continue
            
        token = str(entry) # converts int and sexpdata.symbols to str

        if re.fullmatch(r'\d+', token):
            if token == "0":
                regex_parts.append(r"({}(?:\s+{})*?)?".format(WORD, WORD))
            elif token == "1":
                regex_parts.append(r"({})".format(WORD))
            else:
                regex_parts.append(r"({}(?:\s+{}){{{}}})".format(WORD, WORD, int(token)-1))
        else:
            regex_parts.append(r"\b(" + re.escape(token) + r")\b")

    # Join with \s* between all parts
    regex_pattern =  r"\s*".join(regex_parts) 
    return regex_pattern


def rrule_to_fstring(rrule) -> str:
    """
    Replaces positive numbers in the input string with '{}' and returns the modified string
    along with a list of the numbers found.
    
    :param rrule: Input string containing positive numbers
    :return: Tuple (modified string, list of found numbers)
    """
    numbers = re.findall(r'\b(\d+)\b', rrule)  # Find all whole positive numbers
    formatted_string = re.sub(r'\b\d+\b', '{}', rrule)  # Replace numbers with '{}'
    return formatted_string, [int(num) for num in numbers]

