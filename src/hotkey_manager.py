# pylint: disable=broad-except

import threading
import time
from pynput import keyboard

class HotkeyManager:
    """
    Manages the global hotkey listener for double Ctrl+C presses.
    """
    def __init__(self, callback, window_ms=400):
        self.callback = callback
        self.window_s = window_ms / 1000.0
        self._last_press_time = 0
        self._ctrl_pressed = False
        self._c_pressed = False
        self._listener = None
        self._running = False # Renamed from _running to reflect manager state

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

        except Exception as e:
            # Log any exception to prevent the listener thread from crashing silently
            print(f"Error in hotkey listener on_press: {e}")

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

    def start(self):
        """Starts the keyboard listener in a separate daemon thread."""
        if not self._running:
            self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
            self._listener.daemon = True # Allow the program to exit even if the listener is still running
            self._listener.start()
            self._running = True
            print("Hotkey listener started.")

    def stop(self):
        """Stops the keyboard listener."""
        if self._running and self._listener:
            self._listener.stop()
            self._running = False
            print("Hotkey listener stopped.")

    def join(self):
        """Waits for the listener thread to terminate."""
        if self._listener and self._listener.is_alive():
            self._listener.join()

if __name__ == '__main__':
    # Example Usage:
    def my_callback():
        print("Ctrl+C double-press detected!")

    print("Listening for double Ctrl+C press (within 400ms)... Press Esc to exit.")
    hotkey_manager = HotkeyManager(my_callback)
    hotkey_manager.start()

    # Keep the main thread alive for a bit to allow the listener to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        hotkey_manager.stop()
        print("Listener stopped.")