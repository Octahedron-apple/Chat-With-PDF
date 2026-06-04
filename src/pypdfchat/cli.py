import os
import sys
import curses
import argparse
try:
    import pypdfchat.engine as engine
except ImportError:
    import engine

try:
    import pypdfchat.embedder as embedder
except ImportError:
    import embedder

try:
    import pypdfchat.loader as loader
except ImportError:
    import loader

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
                line = f"> {filename} <"
            else:
                line = f"  {filename}  "
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
def run_chat(chosen_file, args):
    if not chosen_file:
        print("No file selected. Exiting.")
        sys.exit(0)
        
    print(f"\n[+] Selected File: {chosen_file}")
    print(f"[+] Provider: {args.provider.upper()} | Model: {args.model} | Embeddings: {args.embed_model}")
    
    print("\n[~] Reading and chunking PDF...")
    pdf_loader = loader.pdfloader(file_path=chosen_file)
    pdf_loader.load_pdf()
    pdf_loader.chunk_maker()
    docs = pdf_loader.docs_maker()
    
    print("[~] Generating Embeddings and building Vector Database...")
    embedder_factory = embedder.Embedder()
    embeddings = embedder_factory.get_embedder(provider=args.provider, model_name=args.embed_model)
    
    db_manager = embedder.Database()
    faiss_index = db_manager.create_and_save(documents=docs, embedder=embeddings)
    
    retriever = faiss_index.as_retriever(search_kwargs={"k": 3})
    
    print("[~] Booting up Chat Engine...")
    bot = engine.ChatEngine(
        retriever=retriever,
        provider=args.provider,
        model=args.model
    )
    
    print("\n" + "="*50)
    print(" READY! Type 'exit', 'quit', or 'clear' (to wipe memory).")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'clear':
                bot.clear_memory()
                continue
            elif not user_input.strip():
                continue
                
            print("AI: ", end="", flush=True)
            for chunk in bot.ask(user_input):
                print(chunk, end="", flush=True)
            print("\n")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def main():
    args = parse_args()
    chosen_file = curses.wrapper(choose_file)
    run_chat(chosen_file, args)

if __name__ == "__main__":
    main()