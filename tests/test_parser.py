import pytest
from eliza.utils import clean_response
from eliza.core import Eliza
from eliza.exceptions import ElizaScriptError

@pytest.mark.parametrize("good_script", [
    "STOP (BADRULE...)",  # parser stop
    "() HONK",  # parser stop
    "(DOG DLIST (PET ANIMAL))",  # category list
    "(DOG MEMORY ((DOG 0)(WAU))((0)(WUFF)))",  # simple memory rule
    "(CAT = ANIMAL 7 ((CAT 0)(MEOW))((0)(CHAW)))",  # simple response rule
    "(PUSSY (=CAT))",  # rule-based redirection
    "(PUSSY ((0)(NEWKEY)))",  # rule-based redirection
    "(MOUSE ((MICKY MOUSE)(=HERO)))", # reassembly-based redirection
    "(MOUSE ((0 MOUSE 0)(PRE (MOUSE 3)(=CAT))))", # pre-formatted redirection
])
@pytest.mark.smoke
def test_parsing_success(good_script):
    eliza = Eliza(script_data=good_script)
    assert isinstance(eliza, Eliza)

@pytest.mark.parametrize("bad_script", [
    "(KEYWORD)",  # Too short, missing rule structure
    "(123 ABC)",  # Invalid keyword type
    "(KEYWORD DLIST)",  # Missing actual list in DLIST
    "(KEYWORD MEMORY (0)(NOT_A_LIST))",  # Reassembly not in a list
])
@pytest.mark.smoke
def test_parsing_failure_cases(bad_script):
    with pytest.raises(ElizaScriptError):
        Eliza(script_data=bad_script)
