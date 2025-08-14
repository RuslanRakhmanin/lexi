# pylint: disable=line-too-long

"""Main application for the Lexi text assistant with system tray integration."""
import os
import sys
import tkinter as tk
from hotkey_manager import HotkeyManager
from tray_manager import TrayManager
from state_manager import StateManager
from ui_manager import UIManager
from api_key_manager import ApiKeyManager
from app_logic import AppLogic

class App(tk.Tk):
    """Main application class for the Lexi text assistant."""
    def __init__(self):
        super().__init__()

        # Get the absolute path to a resource, works for dev and PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # Running in PyInstaller bundle
            self.base_path = sys._MEIPASS
        else:
            # Running in normal Python environment
            self.base_path = os.path.dirname(__file__)

        self.config_filepath = os.path.join("config", "settings.json")
        self.prompts_filepath = os.path.join("config", "prompts.json")
        

        self.icon_filepath = os.path.join(self.base_path, "icons", "Feather1.ico")
        css_filepath = os.path.join("config", "styles.css")

        # Initialize StateManager and load state
        self.state_manager = StateManager(self.config_filepath, self.prompts_filepath)
        try:
            self.state_manager.load_state()
        except ValueError:
            self.destroy() # Exit if config loading fails
            return

        config = self.state_manager.get_config()
        prompts_config = self.state_manager.get_prompts_config()

        # Initialize UIManager
        self.ui_manager = UIManager(self, prompts_config, "", config) # CSS content loaded later by AppLogic

        # Initialize AppLogic
        self.tray_manager = TrayManager(self)
        self.app_logic = AppLogic(self.ui_manager, self.state_manager, self.tray_manager)
        self.app_logic.load_css(css_filepath) # Load CSS via AppLogic

        # Initialize ApiKeyManager
        self.api_key_manager = ApiKeyManager(self, self.state_manager, self.ui_manager)

        # Initialize TrayManager and HotkeyListener
        self.tray_manager.create_icon()
        self.hotkey_manager = HotkeyManager(self.app_logic._on_hotkey_triggered) # Pass AppLogic method
        self.hotkey_manager.start()

        # Bind Escape key to hide window
        self.ui_manager.bind_escape_key(self._on_escape_pressed)

        # Bind Enter and Shift+Enter to the input widget
        self.ui_manager.bind_input_key_press(self.app_logic.process_input_from_enter)

        self.title("Lexi - Gemini-Powered Text Assistant")
        # self.iconbitmap(os.path.join("config", "Feather1.ico"))
        self.iconbitmap(self.icon_filepath)

        # Restore window geometry if available in config
        window_geometry = config.get("window_geometry")
        if window_geometry:
            try:
                self.geometry(window_geometry)
                print(f"Restored window geometry: {window_geometry}")
            except tk.TclError as e:
                print(f"Error restoring window geometry '{window_geometry}': {e}")

        # Set initial language selections in UI
        self.ui_manager.set_source_language(config.get("source_language"))
        self.ui_manager.set_target_language(config.get("target_language"))

        # Determine initial input type and create processing buttons
        initial_input_text = self.ui_manager.get_input_text()
        initial_input_type = self.app_logic._determine_input_type(initial_input_text) if initial_input_text else "phrase"
        # Pass the AppLogic button click handler callback
        self.ui_manager.create_processing_buttons(initial_input_type, self.app_logic._on_prompt_button_click)

        # Restore last selected processing option in UI
        last_processing_option = config.get("last_processing_option")
        if last_processing_option:
            self.ui_manager.set_prompt_button_pressed_state(last_processing_option)
            print(f"Restored last processing option: {last_processing_option}")


        # Check API key on startup
        self.api_key_manager.check_api_key()

    def _on_escape_pressed(self):
        """Hides the application window when the Escape key is pressed."""
        print("Escape key pressed. Hiding window.")
        self.tray_manager.toggle_window_visibility(None, None) # Hide the window

if __name__ == "__main__":
    app = App()

    # Handle closing the window via the 'X' button and hiding to tray
    def on_closing():
        # Save window state before hiding/exiting
        app.state_manager.save_window_state(app.ui_manager)
        app.tray_manager.toggle_window_visibility(None, None) # Hide the window instead of destroying

    app.protocol("WM_DELETE_WINDOW", on_closing)

    app.mainloop()

    # Save window state and stop threads when mainloop exits
    # app.state_manager.save_window_state(app.ui_manager) # Save window state before exiting
    app.tray_manager.stop_icon() # Ensure icon is stopped when mainloop exits
    app.hotkey_manager.stop() # Ensure hotkey listener is stopped
    app.hotkey_manager.join() # Wait for the hotkey listener thread to finish
