# Pytest-style test functions
import pytest
import regex as re
from eliza.core import ElizaRule

@pytest.mark.parametrize("rule,text,should_match", [
    ("0 YOUR 0", "YOUR", True),
    ("0 YOUR 0", "YOUR NAME", True),
    ("0 YOUR 0", "MY YOUR NAME", True),
    ("0 YOUR 0", "MYYOUR", False),
    ("0 YOUR 0", "    YOUR    ", True),

    ("HELLO", "HELLO", True),
    ("HELLO", "hello", True),
    ("HELLO", "HELLOTHERE", False),
    ("HELLO", "OH HELLO THERE", False),

    ("MAY DAY", "MAY DAY", True),
    ("MAY DAY", "MAY     DAY", True),
    ("MAY DAY", "MAYDAY", False),
    ("MAY DAY", "SOME MAY DAY PARADE", False),

    ("0 YOU 0 I 0", "YOU SEE I KNOW", True),
    ("0 YOU 0 I 0", "I KNOW YOU SEE", False),
    ("0 YOU 0 I 0", "WITH YOU I LEARN A LOT", True),

    ("0", "", True),
    ("0", "SOMETHING", True),
    ("0", "I HAVE SOMETHING TO SAY", True),

    ("1", "ONEWORD", True),
    ("1", "TWO WORDS", False),
    ("1", "", False),

    ("YOU 1 ME", "YOU LOVE ME", True),
    ("YOU 1 ME", "YOU DONT LOVE ME", False),
    
    ("YOU WANT 1", "YOU WANT ME", True),
    ("YOU WANT 1", "YOU WANT ME NOT", False),
    
    ("2", "TWO WORDS", True),
    ("2", "JUST THREE WORDS", False),
    ("2", "ONE", False),

    ("YOU 2 ME", "YOU REALLY LOVE ME", True),
    ("YOU 2 ME", "YOU HATE ME", False),

    ("2 YOU WANT", "WHAT DO YOU WANT", True),
    ("2 YOU WANT", "SO WHAT DO YOU WANT", False),
])
@pytest.mark.smoke
def test_drule_matches(rule, text, should_match):
    rule_obj = ElizaRule(pattern=rule)
    pattern = rule_obj.to_regex()
    regex = re.compile(pattern, re.IGNORECASE)
    result = regex.fullmatch(text)
    assert bool(result) == should_match

@pytest.mark.parametrize("rule,text,expected_groups", [
    ("0 I 0", "What did I say", ["What did", "I", "say"]),
    ("0 I 0", "I tell you", [None, "I", "tell you"]),
    ("0 ARE 0", "You ARE nice", ["You", "ARE", "nice"]),
    ("0 HELLO", "Well HELLO", ["Well", "HELLO"]),
    ("HELLO 0", "HELLO again friend", ["HELLO", "again friend"]),
])
@pytest.mark.smoke
def test_drule_capture_groups(rule, text, expected_groups):
    rule_obj = ElizaRule(pattern=rule)
    pattern = rule_obj.to_regex()
    regex = re.compile(pattern, re.IGNORECASE)
    match = regex.fullmatch(text)
    assert match, f"Pattern did not match: {pattern}"
    assert list(match.groups()) == expected_groups
