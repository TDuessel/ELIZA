import pytest
from eliza.utils import SPLIT_REGEX

@pytest.mark.parametrize("input_text, expected_parts", [
    # Basic punctuation
    ("Hello. How are you?", ["Hello", "How are you?"]),
    
    # Multiple punctuation treated as one split
    ("Well... I don't know.", ["Well", "I don't know."]),

    # Mid-sentence comma split
    ("I came, I saw, I left.", ["I came", "I saw", "I left."]),

    # Punctuation followed by multiple spaces
    ("Wait!  What?   Really.", ["Wait", "What", "Really."]),

    # Colons and semicolons
    ("Listen: I know; you told me.", ["Listen", "I know", "you told me."]),

    # Emoticons and punctuation
    ("No way! :) You can't be serious.", ["No way", ":) You can't be serious."]),

    # No punctuation
    ("Just words with no split", ["Just words with no split"]),

    # Sentence ends with punctuation
    ("Are you there?", ["Are you there?"]),

    # Sentence starts with punctuation (edge case)
    (".Beginning of time", [".Beginning of time"]),

    # Combination of punctuation
    ("What?! Are you serious?! Okay...", ["What", "Are you serious", "Okay..."]),
])
@pytest.mark.smoke
def test_sentence_splitter(input_text, expected_parts):
    parts = SPLIT_REGEX.split(input_text)
    parts = [part.strip() for part in parts if part.strip()]  # Clean up
    assert parts == expected_parts
