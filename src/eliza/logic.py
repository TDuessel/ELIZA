import regex as re
from typing import Optional
from .utils import SPLIT_REGEX, WORD_RE, PRE_RE
from .exceptions import ElizaScriptError
from .logger import logger
from .model import ElizaEntry, ElizaRule, ElizaReassemblyList

def process_keyword_entry(self: "Eliza",
                          key: str,
                          reflected_input: str,
                          use_memory: bool,
                          visited_keys: list[str]) -> Optional[str]:
    
    if key in visited_keys:
        path = " -> ".join(visited_keys + [key])
        raise ElizaScriptError(f"Circular rule-level redirection detected: {path}")
    visited_keys.append(key)

    entry = self.dictionary.get(key)
    if not entry:
        raise ElizaScriptError(f"No dictionary entry found for key: {key}")

    if use_memory:
        rules = entry.memory_rules
    else:
        rules = entry.response_rules
    
    for rule in rules:
        
        if rule.redirection:
            logger.info(f"  rule.redirection: {rule.redirection}")
            return process_keyword_entry(self, rule.redirection,
                                         reflected_input, use_memory, visited_keys)

        logger.info(f"  rule.pattern: {rule.pattern}")
        match = rule.regex.fullmatch(reflected_input)
        if match:
            groups = match.groups()
            reassembly = rule.reassembly_list()

            response = None
            
            if reassembly.pattern:
                logger.info(f"   reassembly.pattern: {reassembly.pattern}")
                response_format, capture_indices = reassembly.template
                selected = [
                    re.sub(r"\s+", " ", groups[i - 1]) if groups[i - 1] else ""
                    for i in capture_indices
                ]
                response = response_format.format(*selected)

            if reassembly.redirection:
                logger.info(f"   reassembly.redirection: {reassembly.redirection}")
                if response:
                    reflected_input = response
                return process_keyword_entry(self, reassembly.redirection,
                                             reflected_input, use_memory, visited_keys)
                
            return response
                
    return None

def get_response_logic(self, user_input: str) -> str:
    part_sentences = SPLIT_REGEX.split(user_input)
    reflected_input = ""
    found_keyword = False

    # 1) Tokenize user input, look up keywords, fill keystack
    for part in part_sentences:
        part_clean = part.strip()
        if not part_clean:
            continue
        tokens = WORD_RE.findall(part_clean.upper())
        toprank = 0
        for i, token in enumerate(tokens):
            entry = self.dictionary.get(token)
            if entry and entry.rank is not None:
                rank = entry.rank
                if entry.alias:
                    tokens[i] = entry.alias
                found_keyword = True
                if rank >= toprank:
                    self.keystack.push((token, rank))
                    toprank = rank
                else:
                    self.keystack.append((token, rank))
        reflected_input = " ".join(tokens)
        if found_keyword:
            break
    
    logger.info(f"reflected_input: {reflected_input}")
    logger.info(f"keystack: {str(self.keystack)}")

    response_text = None
    memory_text = None

    # 2) Pop from keystack until we got both or keystack exhausted
    while self.keystack and (not response_text or not memory_text):
        key, _ = self.keystack.pop()
        logger.info(f" key: {key}")
        if not response_text:
            response_text = process_keyword_entry(self, key, reflected_input,
                                                  use_memory=False, visited_keys=[])

        if not memory_text:
            memory_text = process_keyword_entry(self, key, reflected_input,
                                                use_memory=True, visited_keys=[])
        
    self.keystack.clear()

    # 3) If we got a memory_text, append it to memory
    if memory_text:
        self.context.memory_queue.append(memory_text)

    # 4) If still nothing, try memory
    if not response_text and self.context.memory_queue:
        response_text = self.context.memory_queue.popleft()
        logger.info(f"memory_queue.popleft: {response_text}")

    # 5) If still nothing, fallback to 'NONE' entry
    if not response_text and 'NONE' in self.dictionary:
        logger.info(" key: NONE")
        response_text = process_keyword_entry(self, 'NONE', reflected_input,
                                              use_memory=False, visited_keys=[])

    return response_text or "I ShoULd NoT sAy tHIs;)"
