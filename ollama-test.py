import ollama
from termcolor import colored
from print_utils import print_bold_color
import subprocess
import ollama_output_helepers as output_helpers
from ollama_handler import OllamaHandler
from run_command import RunCommandTool
from dummy_tool import DummyTool
from api_call import ApiCallTool
from crypto_price_tool import CryptoPriceTool
from tool_handler import ToolHandler

# tool_system_message = "You are a helpful assistant trying to answer questions. Try not to use any tools first. Do not use a tool if the question you are asked is not related to the description of a tool. You may be able use a variety of tools to help answer prompts, only if a tool is necessary to provide an answer. If you have access to a tool that may be used to respond to a prompt, include the necessary tool call information in your response. If a tool with a description related to the question does not exist, answer as you normally would without including any tool call in your response."
general_sys_message = "Please answer all prompts as you normally would. If a question is related to macOS terminal commands, begin the prompt with a single line containing exactly the following text in square brackets: [TOOLCALL]. In addition to this, no matter what, ensure every response includes sufficient information to answer the question given by the user"
model_name = "deepseek-r1:7b"

def is_exit_cmd(input):
    return True if input=='exit' or input=='q' else False

def handle_input(user_input):
    if is_exit_cmd(user_input):
        exit()
    elif user_input=='chat':
       print_bold_color(f"\n\n-----------------------------------\nNow chatting with {model_name}\nType 'exit' or 'q' to exit\n-----------------------------------", "light_blue")
       chat_loop()
    elif user_input=='addrag':
        url = input("Enter URL to add to Chromadb: ")
        handler.add_web_data_to_chromadb(url)

def chat_loop():
    user_is_chatting = True
    while user_is_chatting:
        chat_input = input(f"\n\n{colored(f'{model_name}>>', 'blue')} ")
        user_is_chatting = handle_chat_cmd(chat_input)

def handle_chat_cmd(input):
    if is_exit_cmd(input):
        return False
    else:
        get_llama_output(input)
        return True


def get_llama_output(input):
    # handler.get_rag_tool_answer(input)
    handler.get_rag_answer(input)
    # tool_handler.query_tools(query_text=input)

crypto_tool = CryptoPriceTool()
tool_dict = {
    "get_flight_times": RunCommandTool(),
    "tell_me_a_joke": ApiCallTool(),
    "standard_response": DummyTool(),
    crypto_tool.name: crypto_tool
}

tool_list = []
for tool in tool_dict:
    tool_list.append(tool_dict[tool].tool_template)

handler = OllamaHandler(model_name, tool_list, tool_dict )
# handler.init_chroma_db("https://en.wikipedia.org/wiki/Large_language_model")
print("Creating Embeddings")
# handler.init_embeddings()
print("Creating Collection")
# handler.init_chroma_collection()
# tool_handler = ToolHandler()
print("Adding Tools")
# tool_handler.delete_tool_from_chromadb(tool_dict["standard_response"])
# tool_handler.add_tool_to_chromadb(tool=tool_dict["standard_response"])
# handler.tool_chromadb.add_tool(tool=crypto_tool)



while True:
    user_input = input("\n>> ")
    handle_input(user_input)