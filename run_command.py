import subprocess
import print_utils
import ollama 
import json

class RunCommandTool:
    def __init__(self):
        self.name = "get_flight_times"
        self.description = "Get the flight times between two cities. Use if the user wants to know how long a flight is."
        self.tool_template = {
            "type": "function",
            "function": {
                "name": "get_flight_times",
                "description": "Get the flight times between two cities. Use if the user wants to know how long a flight is.",
                "parameters": {
                    "type": "object",
                    "required": ["depart", "arrive"],
                    'properties': {
                        "depart": {
                            "type": "string",
                            "description": "The departure city of the flight"
                        }, 
                        "arrive": {
                            "type": "string",
                            "description": "The arrival city of the flight"
                        }
                    }
                }
            }
        }


    def run(self, args):
        # print(f"Called run command with args {args}")
        # cmd = args['cmd']
        # accept = input(f"Run Command: {cmd}?\nType 'y' to run>> ")
        # if "y" in accept.lower():
        #     print_utils.print_section_header("Output")
        #     processResults = subprocess.run(cmd.split(" "))
        #     return f"Results = {processResults.stdout}"
        # else:
        #     return "User chose to not run command"
        print(f"Called run command with args {args}")
        return json.dumps({"depart": "DEN", "arrive": "LA", "duration": "2h 30m"})
    

    def explain_runCommand(tool_cmd, stream, input):
        # prompt = f"Explain the use of the {tool_cmd} command in the MacOS terminal and how this accomplishes the task I requested in the previous prompt."
        # explain = ollama.chat(
        #     model='llama3.2',
        #     messages=[{'role': 'user', 'content': prompt}],
        #     stream=True
        # )
        prompt = f"The user is requesting an explaination for a macOS command to perform the action is square brackets. Please give a brief explaination of the related macOS terminal command and list all previous commands you have been asked to explain. [{input}]"
        stream = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
        print_utils.print_section_header("Explaination")
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
    