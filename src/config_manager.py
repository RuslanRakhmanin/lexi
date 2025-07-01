import json
import os

DEFAULT_CONFIG = {
    "api_key": "",
    "source_language": "English",
    "target_language": "Ukrainian",
    "last_processing_option": "Translate",
    "window_geometry": "800x600"
}

def load_config(filepath):
    """
    Loads configuration from a JSON file.

    Args:
        filepath (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration dictionary, or a default configuration
              if the file is not found or has a JSON decode error.

    Raises:
        ValueError: If a JSONDecodeError occurs during file reading.
    """
    if not os.path.exists(filepath):
        print(f"Configuration file not found: {filepath}. Using default configuration.")
        save_config(filepath, DEFAULT_CONFIG)  # Save default config if file doesn't exist
        return DEFAULT_CONFIG

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filepath}. Using default configuration.")
        raise ValueError(f"Invalid JSON format in configuration file: {filepath}")
    except Exception as e:
        print(f"An unexpected error occurred while loading config from {filepath}: {e}")
        return DEFAULT_CONFIG


def save_config(filepath, data):
    """
    Saves configuration data to a JSON file.

    Args:
        filepath (str): The path to save the configuration file.
        data (dict): The configuration data to save.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Configuration saved to {filepath}")
    except Exception as e:
        print(f"An error occurred while saving config to {filepath}: {e}")
