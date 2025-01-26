import subprocess
import print_utils
import ollama 
import requests
from tool_interface import Tool
import json

class ApiCallTool(Tool):
    @property
    def description(self):
        return "Retrieve a joke to tell the user. Only use this tool if the user specifically requests a joke to be told. If the user asks anything unrelated to a joke, do not call this tool"
    
    @property
    def name(self):
        return "tell_me_a_joke"
    
    @property
    def tool_template(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "required": ["joke"],
                    'properties': {
                        "joke": {
                            "type": "string",
                            "description": "The type of joke being requested by the user"
                        }
                    }
                }
            }
        }

    def run(self, args) -> str:
        return json.dumps({"joke": "Knock knock. Who's there? Boo. Boo who? Don't cry, it's just a joke"})

    
    
    # def explain_runCommand(tool_cmd, stream, input):
    #     # prompt = f"Explain the use of the {tool_cmd} command in the MacOS terminal and how this accomplishes the task I requested in the previous prompt."
    #     # explain = ollama.chat(
    #     #     model='llama3.2',
    #     #     messages=[{'role': 'user', 'content': prompt}],
    #     #     stream=True
    #     # )
    #     prompt = f"The user is requesting an explaination for a macOS command to perform the action is square brackets. Please give a brief explaination of the related macOS terminal command and list all previous commands you have been asked to explain. [{input}]"
    #     stream = ollama.chat(
    #         model='llama3.2',
    #         messages=[{'role': 'user', 'content': prompt}],
    #         stream=True
    #     )
    #     print_utils.print_section_header("Explaination")
    #     for chunk in stream:
    #         print(chunk['message']['content'], end='', flush=True)
    