import pytest

@pytest.mark.smoke
def test_eliza_rule_regex_caching():
    from eliza.core import ElizaRule

    rule = ElizaRule("0 YOU 1 ME")
    first = rule.regex
    second = rule.regex
    assert first is second  # same object -> compiled only once
