# pylint: disable=line-too-long

import json
import os

DEFAULT_SETTINGS = {
    "api_key": "",
    "llm_model": "gemini-2.5-flash-lite",
    "source_language": "English",
    "target_language": "Ukrainian",
    "last_processing_option": "Translate",
    "window_geometry": "800x600",
    "source_languages": ["English", "British English", "Spanish", "French", "German", "Ukrainian", "Russian"],
    "target_languages": ["Ukrainian", "Russian", "English", "British English", "Spanish", "French", "German"]
}

DEFAULT_PROMPTS = {
  "word": [
    {
      "label": "Full Analysis",
      "prompt": "Provide a comprehensive analysis for the word '{text}' in {from_language}. Include its definition, synonyms, antonyms, and three example sentences.",
      "default": False
    },
    {
      "label": "Translate",
      "prompt": "Translate the word '{text}' from {from_language} to {to_language}.",
      "default": True
    },
    {
      "label": "Custom Prompt",
      "prompt": "'{text}'. Make a fairy tail about this word in {from_language}. Include a moral lesson.",
      "default": False
    }
  ],
  "phrase": [
    {
      "label": "Proofread",
      "prompt": "Proofread and correct the following text, keeping the original meaning. Explain the corrections. The original text is in {from_language}. Use Markdown for your corrections: **new text** for additions and ~~old text~~ for deletions. Original text: '{text}'",
      "default": False
    },
    {
      "label": "Translate",
      "prompt": "Translate the following text from {from_language} to {to_language}. Text: '{text}'",
      "default": True
    },
    {
      "label": "Custom Prompt",
      "prompt": "'{text}'. Make a fairy tail about this word in {from_language}. Include a moral lesson.",
      "default": False
    }
  ]
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
        print(f"Settings file not found: {filepath}. Using default settings.")
        save_config(filepath, DEFAULT_SETTINGS)  # Save default settings if file doesn't exist
        return DEFAULT_SETTINGS

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Add default values for new keys if they don't exist
        config.setdefault("source_languages", DEFAULT_SETTINGS["source_languages"])
        config.setdefault("target_languages", DEFAULT_SETTINGS["target_languages"])

        return config
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filepath}. Invalid format.")
        save_config(filepath, DEFAULT_SETTINGS)  # Save default settings if JSON is invalid
        return DEFAULT_SETTINGS
        # raise ValueError(f"Invalid JSON format in settings file: {filepath}")
    except Exception as e:
        print(f"An unexpected error occurred while loading settings from {filepath}: {e}")
        # Re-raise the exception to be handled by the caller (app.py)
        # raise e
        save_config(filepath, DEFAULT_SETTINGS)  # Save default settings on error
        return DEFAULT_SETTINGS


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
        print(f"Settings saved to {filepath}")
    except Exception as e:
        print(f"An error occurred while saving settings to {filepath}: {e}")

def load_prompts(filepath):
    """
    Loads prompts configuration from a JSON file.

    Args:
        filepath (str): The path to the prompts file.

    Returns:
        dict: The loaded prompts dictionary, or a default configuration
              if the file is not found or has a JSON decode error.
    """
    if not os.path.exists(filepath):
        print(f"Prompts file not found: {filepath}. Using default prompts.")
        # Do NOT save default prompts here, as per spec section 3.3 (use defaults but continue)
        return DEFAULT_PROMPTS

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        # Basic validation: check for 'word' and 'phrase' keys
        if "word" not in prompts or "phrase" not in prompts:
            print(f"Invalid prompts.json structure: missing 'word' or 'phrase' keys in {filepath}. Using default prompts.")
            return DEFAULT_PROMPTS

        return prompts
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filepath}. Invalid format. Using default prompts.")
        return DEFAULT_PROMPTS
    except Exception as e:
        print(f"An unexpected error occurred while loading prompts from {filepath}: {e}")
        return DEFAULT_PROMPTS
