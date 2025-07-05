import tkinter as tk
from tkinter import ttk
import os
from state_manager import StateManager # Import StateManager

class ApiKeyManager:
    """Manages the API key checking and input process."""

    def __init__(self, root, state_manager, ui_manager):
        """
        Initializes the ApiKeyManager.

        Args:
            root: The root Tkinter window (the App instance).
            state_manager: The StateManager instance.
            ui_manager: The UIManager instance.
        """
        self.root = root
        self.state_manager = state_manager
        self.ui_manager = ui_manager

    def check_api_key(self):
        """Checks if the API key is present and prompts the user if missing."""
        config = self.state_manager.get_config()
        api_key = config.get("api_key")

        if not api_key:
            print("API key missing. Prompting user.")
            self.ui_manager.toggle_main_widgets_state(tk.DISABLED) # Disable UI
            self.ui_manager.show_api_key_input(self.save_api_key) # Show API key input using UI manager
        else:
            print("API key found. UI is unlocked.")
            # UI is already unlocked by default, nothing to do here
            # Ensure main frame is visible if it was hidden previously
            self.ui_manager.hide_api_key_input()
            self.ui_manager.toggle_main_widgets_state(tk.NORMAL)


    def save_api_key(self, event=None):
        """Saves the entered API key to settings.json and unlocks the UI."""
        api_key = self.ui_manager.api_key_entry.get().strip() # Get key from UI manager's entry
        if api_key:
            self.state_manager.update_config('api_key', api_key) # Update config via StateManager
            self.ui_manager.hide_api_key_input() # Hide API key input using UI manager
            self.ui_manager.toggle_main_widgets_state(tk.NORMAL) # Unlock UI
            print("API key saved and UI unlocked.")
        else:
            print("API key cannot be empty.")
