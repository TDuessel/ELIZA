import pytest
from eliza.rules import rrule_to_fstring

@pytest.mark.parametrize("rrule, expected_fmt, expected_nums", [
    ("WHAT MAKES YOU THINK I 3", "WHAT MAKES YOU THINK I {}", [3]),
    ("DO YOU BELIEVE YOU ARE 4", "DO YOU BELIEVE YOU ARE {}", [4]),
    ("WHAT 4", "WHAT {}", [4]),
    ("DO YOU THINK IT IS LIKELY THAT 3", "DO YOU THINK IT IS LIKELY THAT {}", [3]),
    ("SUPPOSE YOU GOT 0 NOW", "SUPPOSE YOU GOT {} NOW", [0]),
    ("NO NUMBERS HERE", "NO NUMBERS HERE", []),
    ("1 2 3 4", "{} {} {} {}", [1, 2, 3, 4]),
    ("MIXED 3 with 2 and 7 again 3", "MIXED {} with {} and {} again {}", [3, 2, 7, 3]),
])
@pytest.mark.smoke
def test_rrule_to_fstring(rrule, expected_fmt, expected_nums):
    result_fmt, result_nums = rrule_to_fstring(rrule)
    assert result_fmt == expected_fmt
    assert result_nums == expected_nums
