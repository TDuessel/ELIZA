import regex as re
import sexpdata # type: ignore
from .utils import WORD
from .exceptions import ElizaScriptError

from typing import TYPE_CHECKING, List, cast
if TYPE_CHECKING:
    from .model import ElizaRule, ElizaContext, ElizaReassembly

    
def normalize_subrule(subrule: List[str], prefixes: str = "*/=") -> List[str]:
    if not subrule:
        return subrule  # empty, return as-is

    first = str(subrule[0])
    rest = subrule[1:]

    if first and first[0] in prefixes and len(first) > 1:
        return [first[0], first[1:], *map(str, rest)]

    return list(map(str, subrule))


def drule_to_regex(self: "ElizaRule") -> str:
    """
    Method for ElizaRule:
    Converts the decomposition pattern into regex.

    Variable tokens:
    - "0" matches any number of words (non-greedy), including empty
    - "1" matches exactly one word
    - "N" matches exactly N words

    Literal tokens are treated case-insensitively and escaped.

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
            subrule = normalize_subrule(entry)

            if len(subrule) > 2 and subrule[0] == "*":
                options = [str(e) for e in subrule[1:]]
                regex_parts.append(r"\b(" + "|".join(re.escape(opt) for opt in options) + r")\b")
            elif len(subrule) == 2 and subrule[0] == "/":
                tag = subrule[1]
                context = cast("ElizaContext", self.context) # self.context is not None!
                options = context.categories.get(tag.upper()) or []
                regex_parts.append(r"\b(" + "|".join(re.escape(opt) for opt in options) + r")\b")
            else:
                raise ElizaScriptError(f"Invalid subrule syntax: {self.pattern!r}")
            
        elif isinstance(entry, int):
            if entry == 0:
                regex_parts.append(r"({}(?:\s+{})*?)?".format(WORD, WORD))
            elif entry == 1:
                regex_parts.append(r"({})".format(WORD))
            else:
                regex_parts.append(r"({}(?:\s+{}){{{}}})".format(WORD, WORD, entry-1))
            
        else: # Symbol a.k.a. str
            regex_parts.append(r"\b(" + re.escape(entry) + r")\b")

    regex_pattern =  r"\s*".join(regex_parts) 
    return regex_pattern


def rrule_to_template(self: "ElizaReassembly") -> tuple[str, list[int]]:
    """
    Replaces positive numbers in the input string with '{}' and returns the modified string
    along with a list of the numbers found.
    
    :param rrule: Input string containing positive numbers
    :return: Tuple (modified string, list of found numbers)
    """
    numbers = re.findall(r'\b(\d+)\b', self.reassembly)  # Find all whole positive numbers
    formatted_string = re.sub(r'\b\d+\b', '{}', self.reassembly)  # Replace numbers with '{}'
    return formatted_string, [int(num) for num in numbers]

