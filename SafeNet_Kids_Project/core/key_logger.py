import keyboard
import threading

class KeyLogger:
    def __init__(self, callback):
        self.callback = callback
        self.current_sentence = ""
        self.is_logging = False

    def start(self):
        if not self.is_logging:
            self.is_logging = True
            keyboard.on_release(self._on_key_release)

    def stop(self):
        self.is_logging = False
        keyboard.unhook_all()

    def _on_key_release(self, event):
        if not self.is_logging:
            return

        if event.name == 'space':
            self.current_sentence += " "
        elif event.name == 'enter':
            if self.current_sentence.strip():
                self.callback(self.current_sentence.strip())
            self.current_sentence = ""
        elif event.name == 'backspace':
            self.current_sentence = self.current_sentence[:-1]
        elif len(event.name) == 1:
            self.current_sentence += event.name