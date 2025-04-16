# helpers.py
def get_dictionary_statistics(dictionary) -> tuple[int, int]:
    """Return a tuple (n_rules, n_reassemblies) from an ElizaDictionary."""
    n_rules = 0
    n_reassemblies = 0

    for entry in dictionary.values():
        for ruleset in (entry.response_rules, entry.memory_rules):
            n_rules += len(ruleset)
            for rule in ruleset:
                n_reassemblies += len(rule.reassembly_list)

    return n_rules, n_reassemblies
