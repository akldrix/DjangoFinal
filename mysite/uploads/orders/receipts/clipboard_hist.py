#!/usr/bin/env python3

import pyperclip
import time
from datetime import datetime
from pathlib import Path


def run_clipboard_history(log_file="clipboard_hist.txt", poll_interval=1.0):
    log_path = Path.home() / Path(log_file)
    previous = ""
    entry_count = 0

    print("Clipboard monitor is running. Press Ctrl + C to stop")

    try:
        while True:
            current = pyperclip.paste()
            if current != previous and current.strip():
                previous = current
                entry_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entry = f"[{timestamp}] Entry #{entry_count}\n{current}\n{'=' * 50}\n"
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(entry)
                preview = current[:80].replace("\n", " ")
                print(f"  #{entry_count} [{timestamp}] {preview}...")
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print(f"\nStopped. Logged {entry_count} entries to {log_path}")


if __name__ == "__main__":
    run_clipboard_history()
