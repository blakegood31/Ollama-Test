from termcolor import colored

def bold(text):
    return "\033[1m" + text + "\033[0;0m"

def print_section_header(text):
    print_bold_color(f"\n--- {text} ---\n", "green")

def print_bold_color(text, color):
    print(colored(bold(text), color), end='', flush=True)