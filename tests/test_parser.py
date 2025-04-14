import pytest
from eliza.utils import clean_response
from eliza.core import Eliza
from eliza.exceptions import ElizaScriptError

@pytest.mark.parametrize("good_script", [
    "STOP (BADRULE...)",  # eval stop
    "() HONK",  # eval stop
    "(DOG MEMORY ((DOG 0)(WAU)))",  # simple memory rule
    "(MEMORY DOG ((DOG 0)(WUFF)))",  # simple memory rule (legacy syntax)
    "(MEMORY MEMORY ((0)(MOO)))",  # simple memory rule for key MEMORY
    "(DOG MEMORY ((DOG 0)(WAU))((0)(WUFF)))",  # two simple memory rules
    "(I = YOU)", # Simple alias definition
    "(YOU = I 1)", # Simple alias definition with rank
    "(CAT = ANIMAL 7 ((CAT 0)(MEOW)))",  # simple response rule
    "(KEYWORD DLIST ())",  # No category, but hey..
    "(DOG DLIST (PET ANIMAL))",  # category list
    "(DOG DLIST (/ PET ANIMAL))",  # category list (legacy syntax)
    "(CAT 1 ((0)(PUSSY)))", # rank & rule
    "(PUSSY (=CAT))",  # rule-based redirection
    "(CAT (= PUSSY))",  # rule-based redirection
    "(PUSSY ((0)(NEWKEY)))",  # rule-based redirection
    "(MOUSE ((MICKY MOUSE)(=HERO)))", # reassembly-based redirection
    "(MOUSE ((0 MOUSE 0)(PRE (MOUSE 3)(=CAT))))", # pre-formatted redirection
])
@pytest.mark.smoke
def test_parsing_success(good_script):
    eliza = Eliza(script_data=good_script)
    assert isinstance(eliza, Eliza)

@pytest.mark.parametrize("bad_script", [
    "(FOO", # Not a valid sexp expression
    "BAR)", # Not a valid sexp expression
])
@pytest.mark.smoke
def test_parsing_failure_cases(bad_script):
    with pytest.raises(Exception):
        Eliza(script_data=bad_script)

@pytest.mark.parametrize("bad_script", [
    "HONK", # Not a list
    "0", # Not a list
    "(KEYWORD)",  # Too short, missing rule structure
    "(() ABC)",  # First item not a symbol
    "(123 ABC)",  # Invalid keyword type
    "(KEYWORD HONK)", # Not a rule
    "(KEYWORD = ())", # Alias expected but...
    "(KEYWORD MEMORY)",  # No rule at all
    "(KEYWORD MEMORY NOPE)",  # Rule is not a list
    "(KEYWORD MEMORY ((0)(NOPE)) KING)",  # Subsequent rule is not a list
    "(KEYWORD MEMORY (KING))",  # Memory rule redirection
    "(KEYWORD DLIST)",  # Missing actual list in DLIST
    "(KEYWORD DLIST 7)",  # Missing actual list in DLIST
    "(KEYWORD DLIST (0))",  # Missing Symbol in DLIST
    "(KEYWORD MEMORY (0)(NOT_A_LIST))",  # Reassembly not in a list
    "(KEYWORD (=KING HENRY))",  # Rule redirection ambigous
    "(KEYWORD ((0) KING))",  # Reassembly not a list
    "(KEYWORD ((0)(BLAH)) KING)", # Invalid decomposition rule
    "(KEYWORD (()(BLAH)))", # Invalid decomposition rule
    "(KEYWORD ((1.0)(BLAH)))", # Invalid decomposition rule
    "(KEYWORD ((0 1)(BLAH)))", # Invalid decomposition rule
    "(KEYWORD ((WORD 0 1)(BLAH)))", # Invalid decomposition rule
])
@pytest.mark.smoke
def test_parsing_failure_cases(bad_script):
    with pytest.raises(ElizaScriptError):
        Eliza(script_data=bad_script)
