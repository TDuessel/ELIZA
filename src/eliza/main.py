import os
import sys
from .core import Eliza
from .utils import clean_response
from .logger import logger

def run() -> None:

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        eliza = Eliza(script_path=file_path) # returns Eliza() object
        logger.info(f"Created Eliza object with {len(eliza.dictionary)} dictionary entries.")
        logger.info(f"eliza.categories:\n{eliza.categories}")
    else:
        print ("Usage: ... file_path")
        sys.exit(1)
        
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
