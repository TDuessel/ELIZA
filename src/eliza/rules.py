import regex as re
from .utils import WORD

# Match any word, even with apostrophes and Unicode letters
#WORD = r"\p{L}+(?:'\p{L}+)?"
#WORD = r"[^\s.,!?;:]+"
#WORD = r"\S+"

def drule_to_regex(drule: str) -> str:
    """
    Converts a decomposition rule into a regex pattern for matching input text.

    Variable tokens:
    - "0" matches any number of words (non-greedy), including empty
    - "1" matches exactly one word
    - "N" matches exactly N words

    Literal tokens are treated case-insensitively and escaped.

    :param drule: Decomposition rule string like "0 YOUR 0"
    :return: Regex pattern string
    """
    tokens = drule.strip().split()
    regex_parts = []

    for token in tokens:
        if re.fullmatch(r'\d+', token):
            if token == "0":
                #regex_parts.append(r"(\w+(?:\s+\w+)*?)?")
                regex_parts.append(r"({}(?:\s+{})*?)?".format(WORD, WORD))
            elif token == "1":
                #regex_parts.append(r"(\w+)")
                regex_parts.append(r"({})".format(WORD))
            else:
                #regex_parts.append(r"(\w+(?:\s+\w+){{{}}})".format(int(token)-1))
                regex_parts.append(r"({}(?:\s+{}){{{}}})".format(WORD, WORD, int(token)-1))
        else:
            #regex_parts.append(r"\b(" + re.escape(token) + r")\b")
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

