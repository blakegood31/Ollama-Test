import subprocess
import print_utils
import ollama 
import json
import requests

class DummyTool:
    def __init__(self):
        self.name = "standard_response"
        self.description = "Return information about the ChromaDB database system (also shown as chromadb). Use if the user asks about ChromaDB (or chromadb)"
        self.tool_template = {
            "type": "function",
            "function": {
                "name": "standard_response",
                "description": self.description,
            }
        }


    def run(self, args):
       data = {"chromadb_description": "ChromaDB is a vector database that can be easily integrated with LLMs to perform retrieval-augmented generation. It has python packages that make it easy to integrate with your application"}
       return json.dumps(data)

    
    
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
    