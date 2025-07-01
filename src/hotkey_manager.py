import threading
import time
from pynput import keyboard

class HotkeyListener(threading.Thread):
    """
    Listens for a double press of Ctrl+C within a specified time window
    and calls a callback function when detected.
    """
    def __init__(self, callback, window_ms=400):
        super().__init__()
        self.callback = callback
        self.window_s = window_ms / 1000.0
        self._last_press_time = 0
        self._ctrl_pressed = False
        self._c_pressed = False
        self._listener = None
        self._running = True

    def _on_press(self, key):
        try:
            # Update state of individual keys (useful for other combinations or future features)
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self._ctrl_pressed = True
            elif hasattr(key, 'char') and key.char == '\x03': # Check for Ctrl+C character
                self._c_pressed = True
            # print(f"Key pressed: {key}")  # Debugging output
            # Check for the specific Ctrl+C combination event
            # Check for Ctrl+C combination using individual key states
            if self._ctrl_pressed and self._c_pressed:
                # print("Ctrl+C detected")  # Debugging output
                current_time = time.time()
                if current_time - self._last_press_time < self.window_s:
                    # Double press detected, call the callback
                    if self._running: # Ensure callback is only called if listener is running
                        self.callback()
                    self._last_press_time = 0 # Reset to prevent triple/quadruple presses
                else:
                    self._last_press_time = current_time

        except AttributeError:
            # Ignore special keys
            pass

    def _on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self._ctrl_pressed = False
                self._c_pressed = False
            elif key.char == 'c':
                self._c_pressed = False
        except AttributeError:
            # Ignore special keys other than Ctrl
            pass

        if key == keyboard.Key.esc:
            # Optional: Stop listener with Esc key
            return False

    def run(self):
        """Starts the keyboard listener."""
        with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as self._listener:
            self._listener.join()

    def stop(self):
        """Stops the keyboard listener."""
        self._running = False
        if self._listener:
            self._listener.stop()

if __name__ == '__main__':
    # Example Usage:
    def my_callback():
        print("Ctrl+C double-press detected!")

    print("Listening for double Ctrl+C press (within 400ms)... Press Esc to exit.")
    hotkey_listener = HotkeyListener(my_callback)
    hotkey_listener.start()

    # Keep the main thread alive until the listener stops
    hotkey_listener.join()
    print("Listener stopped.")