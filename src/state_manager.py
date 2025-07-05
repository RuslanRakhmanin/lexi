import os
from config_manager import load_config, save_config, load_prompts # Import config manager functions

class StateManager:
    """Manages the application's state, including configuration and prompts."""

    def __init__(self, config_filepath, prompts_filepath):
        """
        Initializes the StateManager.

        Args:
            config_filepath (str): The path to the settings configuration file.
            prompts_filepath (str): The path to the prompts configuration file.
        """
        self.config_filepath = config_filepath
        self.prompts_filepath = prompts_filepath
        self.config = {}
        self.prompts_config = {}

    def load_state(self):
        """Loads the application configuration and prompts."""
        try:
            self.config = load_config(self.config_filepath)
            print("Settings loaded successfully.")
        except ValueError as e:
            print(f"Fatal Error loading {self.config_filepath}: {e}")
            print("Application will exit.")
            # In a real app, you might signal the main app to exit here
            raise # Re-raise the exception to stop initialization

        self.prompts_config = load_prompts(self.prompts_filepath) # Load prompts using the new function
        print("Prompts loaded successfully.")

    def save_window_state(self, ui_manager):
        """
        Saves the current window state (geometry, languages, processing option) to settings.json.

        Args:
            ui_manager: The UIManager instance to get current UI state from.
        """
        try:
            # Save window geometry
            # Assuming ui_manager has access to the root window geometry
            current_geometry = ui_manager.root.geometry()
            self.config['window_geometry'] = current_geometry

            # Save selected languages
            self.config['source_language'] = ui_manager.get_source_language()
            self.config['target_language'] = ui_manager.get_target_language()

            # Save last selected processing option
            last_processing_option = ui_manager.get_pressed_prompt_button_label()
            if last_processing_option:
                self.config['last_processing_option'] = last_processing_option
                print(f"Saved last processing option: {last_processing_option}")
            else:
                 # If no button is pressed (e.g., on initial startup before any button is clicked)
                 # try to get the default from the first button if available
                 # This logic might need refinement depending on UI initialization
                 pass # Or handle default saving in UIManager or AppLogic

            # Save the updated config
            save_config(self.config_filepath, self.config)
            print(f"Saved window state: geometry={current_geometry}, source={self.config.get('source_language')}, target={self.config.get('target_language')}")

        except Exception as e:
            print(f"Error saving window state: {e}")

    def get_config(self):
        """Returns the loaded configuration dictionary."""
        return self.config

    def get_prompts_config(self):
        """Returns the loaded prompts configuration dictionary."""
        return self.prompts_config

    def update_config(self, key, value):
        """Updates a specific key in the configuration and saves it."""
        self.config[key] = value
        save_config(self.config_filepath, self.config)
        print(f"Updated config: {key} = {value}")
