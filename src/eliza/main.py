import os
import sys
from eliza.core import Eliza

def run() -> None:
    debug_env = os.getenv("ELIZA_DEBUG", "").lower() in ("1", "true", "yes", "on")
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        eliza = Eliza(script_path=file_path) # returns Eliza() object
    else:
        print ("Usage: ... file_path")
        sys.exit(1)
        
    print("HOW DO YOU DO. PLEASE TELL ME YOUR PROBLEM")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "bye", "quit"]:
            print("ELIZA: GOODBYE! TAKE CARE.")
            break
        response = eliza.get_response(user_input, debug=debug_env)
        print("ELIZA:", response)

if __name__ == "__main__":
    run()
