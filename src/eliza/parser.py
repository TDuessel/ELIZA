import sys
import sexpdata
from eliza.core import (
    ElizaScriptError,
    Eliza,
    ElizaRulesList,
    ElizaReassemblyList,
    ElizaRule,
    ElizaMemoryRule,
    ElizaReassembly
)

# Some special keywords are not used in input scan
# They are marked during parsing by a rank == None 
special_keys = ["DIT", "XFREMD", "NONE"]

def parse_eliza_data(data, eliza=None):
    """Parses ELIZA script data from a string."""
    parsed_data = sexpdata.loads(f'({data})')

    if eliza is None:
        eliza = Eliza()
    
    for entry in parsed_data:
        if isinstance(entry, list):
            
            # Useless keys are considered faulty
            if len(entry) == 1:
                raise ElizaScriptError(f"Malformed entry: {entry}")
            
            # Empty list stops parsing
            # This can be used to debug scripts by putting '()'
            # in the middle of suspect regions.
            if len(entry) == 0:
                break

            key = str(entry[0])  # Keyword
            alias = None  # Default alias
            rank = None  # Default rank
            redirection = None
            response_rules = None
            memory_rules = None
            
            index = 1  # Start checking from the second element
            
            # Check if the second item is "=" (indicating an alias)
            if isinstance(entry[1], sexpdata.Symbol) and str(entry[1]) == "=":
                alias = str(entry[2])  # The alias is stored in entry[2]
                index = 3  # Rules start from entry[3]

            elif isinstance(entry[1], sexpdata.Symbol) and str(entry[0]) == "MEMORY":
                # Useless memory keys are considered faulty
                if len(entry) == 2:
                    raise ElizaScriptError(f"Malformed entry: {entry}")

                key = str(entry[1])

                # ElizaRulesLists are not appendable as such.
                # They are replaced in case of duplicate key entries.
                # TODO: raise an error in case of duplicate key entries.
                memory_rules = ElizaRulesList()
                for rule in entry[2:]:
                    # Memory rules have a special syntax in the original script
                    # TODO: make regular syntax work and special syntax optional
                    drule, _, rrule = sexpdata.dumps(rule).strip('() ').partition("=")
                    reassembly_list = ElizaReassemblyList()
                    reassembly_list.append(ElizaReassembly(rrule.strip()))
                    memory_rules.append(ElizaMemoryRule(drule.strip(), reassembly_list))

                eliza.update_entry(key, memory_rules=memory_rules)
                continue

            # Check if this is a DLIST entry
            if len(entry) > index:
                if isinstance(entry[index], sexpdata.Symbol) and str(entry[index]) == "DLIST":
                    dlist_sexp = entry[index+1]
                    dlist_names = [str(item).strip('/') for item in dlist_sexp]
                    for dlist_key in dlist_names:
                        if dlist_key and dlist_key != "/":
                            eliza.update_category(dlist_key, key)
                    continue

            if len(entry) > index and isinstance(entry[index], int):
                rank = entry[index]
                index += 1  # Rules start on next index
            
            # Unpack individual rules
            if len(entry) > index:
                if isinstance(entry[index][0], list):
                    # By now ElizaRulesLists are not appendable as such.
                    # They are replaced in case of duplicate key entries.
                    response_rules = ElizaRulesList()
                    for rule in entry[index:]:
                        response_rules.append(ElizaRule(sexpdata.dumps(rule[0])[1:-1]))
                        for item in rule[1:]:
                            response_rules[-1].add_reassembly(ElizaReassembly(sexpdata.dumps(item)[1:-1]))
                else:
                    redirection = sexpdata.dumps(entry[index])[1:-1].strip('= ')
            
            # Apply default ranks for all but special keys
            if not rank and not key in special_keys:
                rank = 0
            
            # Store in dictionary as object
            eliza.update_entry(key, alias=alias, rank=rank,
                               redirection=redirection, response_rules=response_rules)
    
    return eliza

def parse_eliza_script(file_path, eliza=None):
    """Reads ELIZA script from a file and parses it."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    return parse_eliza_data(data, eliza=eliza)

# Example usage
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        eliza = parse_eliza_script(file_path)
    
    # Print parsed data for verification
    print(eliza)

