import os
import curses
import argparse

try:
    from pdf_chat.engine import ChatEngine
except ImportError:
    from engine import ChatEngine

try:
    from pdf_chat.embedder import Embedder, Database
except ImportError:
    from embedder import Embedder, Database

try:
    from pdf_chat.loader import load_pdf
except ImportError:
    from loader import load_pdf

def choose_file(stdscr):
    all_items = os.listdir('.')
    files = []
    for f in all_items:
        if os.path.isfile(f) and f.lower().endswith('.pdf'):
            files.append(f)
    if len(files) == 0:
        return None
    selected = 0
    num_files = len(files)
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        start_y = (max_y - num_files) // 2
        if start_y < 0:
            start_y = 0
        for idx in range(num_files):
            filename = files[idx]
            if idx == selected:
                prefix = "> "
            else:
                prefix = "  "
            line = prefix + filename
            line_len = len(line)
            diff_x = max_x - line_len
            x = diff_x // 2
            if x < 0:
                x = 0
            y = start_y + idx
            stdscr.addstr(y, x, line)

        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = selected - 1
            if selected < 0:
                selected = num_files - 1
        elif key == curses.KEY_DOWN:
            selected = selected + 1
            if selected >= num_files:
                selected = 0
        elif key == 10 or key == 13:
            chosen_file = files[selected]
            return chosen_file

def get_api_key(stdscr):
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key

def parse_args():
    parser = argparse.ArgumentParser(description="Chat with PDF CLI")
    parser.add_argument("--provider", type=str, default="ollama", help="LLM Provider (ollama, open_router)")
    parser.add_argument("--model", type=str, default="qwen3.5:2b", help="Model name to use")
    parser.add_argument("--embed_model", type=str, default=None, help="Embedding model to use")
    args = parser.parse_args()
    if args.embed_model is None:
        if args.provider == "open_router":
            args.embed_model = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
        else:
            args.embed_model = "qwen3-embedding:0.6b"  
    if args.provider == "open_router" and args.model == "qwen3.5:2b":
        args.model = "arcee-ai/trinity-large-thinking:free"
    return args
def main():
    args = parse_args()
    curses.wrapper(lambda stdscr: run_chat(stdscr, args))
    