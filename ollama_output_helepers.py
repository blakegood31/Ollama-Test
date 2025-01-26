import ollama
from termcolor import colored
import subprocess
from run_command import RunCommandTool
from api_call import ApiCallTool
import print_utils

tool_dict = {
    "runCommand": RunCommandTool(),
    "apiCall": ApiCallTool()
}


tool_list = []
for tool in tool_dict:
    tool_list.append(tool_dict[tool].tool_template)


def display_response(stream, input):
    collecting_bold_text = False
    called_tool = False
    toolcall_buff = ""
    for chunk in stream:
        chunk_text = chunk['message']['content']
        # Check if model marks response as requiring a tool call
        if "TO" in chunk_text or "OL" in chunk_text or "CALL" in chunk_text and not called_tool:
            toolcall_buff += chunk_text
            continue
        elif "[" == chunk_text:
            continue
        # Set toolcall variables if a toolcall will be used
        if toolcall_buff == "TOOLCALL":
            called_tool = True
            toolcall_buff = ""
            continue
        # Display text from llama response stream if necessary
        if chunk_text != '':
            collecting_bold_text = print_chunk_text(chunk_text, collecting_bold_text)
    # Call external tool if necessary
    if called_tool:
        make_tool_call(input)


def print_chunk_text(chunk_text, collecting_bold_text):
    if '**' in chunk_text and not collecting_bold_text:
        collecting_bold_text = True
    elif '**' in chunk_text and collecting_bold_text:
        collecting_bold_text = False
        print("", flush=True)
    elif collecting_bold_text:
        print_utils.print_bold_color(chunk_text, "white")
    else:
        print(chunk_text, end='', flush=True)
    # Add newline if needed
    if '\n' in chunk_text:
        if chunk_text.count('\n') == 1:
            print("", flush=True)
    return collecting_bold_text


def make_tool_call(input):
    print_utils.print_section_header("\n--- CALLING EXTERNAL TOOL ---\n")
    stream = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': input}],
        tools=tool_list,
        stream=True
    )
    for chunk in stream:
        if 'tool_calls' in chunk['message']:
                toolCalls = chunk['message']['tool_calls']
                for tool in toolCalls:
                    tool_dict[tool['function']['name']].run(tool['function']['arguments'])


def explain_tool_use(tool_func, tool_args, stream, input):
    if tool_func == 'runCommand':
        run_command_tool = RunCommandTool()
        run_command_tool.explain_runCommand(tool_args['cmd'], stream, input)