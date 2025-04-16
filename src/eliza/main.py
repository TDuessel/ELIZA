import os
import sys
import argparse
import logging

from .core import Eliza
from .utils import clean_response
from .logger import logger, setup_logger

def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", type=int, default=0, help="verbosity level for logging")
    parser.add_argument("--log-color", type=str, default=None, help="log color if rich is installed")
    parser.add_argument("file_path", nargs='?', help="Path to ELIZA script")
    args = parser.parse_args()

    setup_logger(args.debug, color=args.log_color)

    if not args.file_path:
        print("Usage: ... file_path")
        sys.exit(1)

    eliza = Eliza(script_path=args.file_path)
    logger.info(f"Created Eliza object with {len(eliza.dictionary)} dictionary entries.")
    n_rules, n_reassemblies = eliza.dictionary.get_statistics()
    logger.info(f"Rules: {n_rules} | Reassemblies: {n_reassemblies}", v=2)
    logger.info(f"eliza.categories:\n{eliza.categories}", v=3)
    
    print("HOW DO YOU DO. PLEASE TELL ME YOUR PROBLEM")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "bye", "quit"]:
            print("ELIZA: GOODBYE! TAKE CARE.")
            break
        response = eliza.get_response(user_input)
        print("ELIZA:", clean_response(response))

if __name__ == "__main__":
    run()
