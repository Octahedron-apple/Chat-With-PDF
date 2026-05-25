import os
import curses

def choose_file(stdscr):
    all_items = os.listdir('.')
    files = []
    for f in all_items:
        if os.path.isfile(f):
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

