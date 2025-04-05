import pytest
from eliza.utils import clean_response
from eliza.core import Eliza

eliza_script_redirections = """
(YES
((0)
(POSITIVE)))

(NO
((0)
(NEGATIVE)))

(CERTAINLY
(=YES))

(NOPE
((0)
(=NO)))

(GREEN
((0)
(=CERTAINLY)))

(RED
(=NOPE))
"""

@pytest.mark.parametrize("user_input, expected_response", [
    ("CERTAINLY", "POSITIVE"),
    ("NOPE", "NEGATIVE"),
    ("GREEN", "POSITIVE"),
    ("RED", "NEGATIVE"),
])
@pytest.mark.smoke
def test_redirections(user_input, expected_response):
    eliza_obj = Eliza(script_data=eliza_script_redirections)
    eliza_response = eliza_obj.get_response(user_input)
    assert clean_response(eliza_response) == expected_response


eliza_script_counting = """
(COUNT
((0)
(ONE)
(TWO)
(THREE)))
"""

@pytest.fixture(scope="module")
def eliza_instance():
    return Eliza(script_data=eliza_script_counting)

@pytest.mark.parametrize("user_input, expected_response", [
    ("COUNT", "ONE"),
    ("COUNT", "TWO"),
    ("COUNT", "THREE"),
    ("COUNT", "ONE"),
])
@pytest.mark.smoke
def test_counting(eliza_instance, user_input, expected_response):
    eliza_response = eliza_instance.get_response(user_input)
    assert clean_response(eliza_response) == expected_response
