# pylint: disable=line-too-long
# pylint: disable=broad-except

import asyncio
import threading
import tkinter as tk # Import tkinter for state constants
import pyperclip # Import pyperclip for clipboard access
from gemini_client import get_llm_response # Import the LLM function
from markdown_renderer import render_markdown_to_html, _markdown_to_plain_text # Import the markdown renderer and plain text converter
from clipboard_manager import ClipboardManager # Import the new ClipboardManager

class AppLogic:
    """Contains the core application logic for Lexi."""

    def __init__(self, ui_manager, state_manager, tray_manager):
        """
        Initializes the AppLogic.

        Args:
            ui_manager: The UIManager instance.
            state_manager: The StateManager instance.
        """
        self.ui_manager = ui_manager
        self.state_manager = state_manager
        self.tray_manager = tray_manager
        self.css_content = "" # Will be loaded from state_manager
        self._last_raw_llm_response = "" # Store the raw LLM response (Markdown)
        self._last_rendered_html = "" # Store the last rendered HTML output

        # Initialize the ClipboardManager
        self.clipboard_manager = ClipboardManager()

        # Bind UI actions to logic methods
        self.ui_manager.bind_copy_button(self.copy_output)
        self.ui_manager.bind_copy_with_formatting_button(self.copy_output_with_formatting)
        # Bind input widget text change to update processing buttons
        self.ui_manager.bind_input_widget_change(self._on_input_text_change)


    def load_css(self, css_filepath):
        """Loads CSS content from a file."""
        try:
            with open(css_filepath, "r", encoding="utf-8") as f:
                self.css_content = f.read()
            print(f"Loaded CSS from {css_filepath}")
        except FileNotFoundError:
            print(f"Error: {css_filepath} not found.")
            self.css_content = "" # Ensure it's empty if file not found
        except Exception as e:
            print(f"Error reading {css_filepath}: {e}")
            self.css_content = "" # Ensure it's empty on error

    def _determine_input_type(self, text):
        """Determines if the input text is a 'word' or 'phrase'."""
        return "word" if len(text.strip().split()) == 1 else "phrase"

    def _on_prompt_button_click(self, clicked_button, prompt_def):
        """Handles a prompt button click, updates visual state, and triggers action."""
        print(f"Prompt button clicked: {prompt_def.get('label')}")

        # Update visual state of buttons using states via UI manager
        self.ui_manager.set_prompt_button_pressed_state(prompt_def.get('label'))

        # Get input text from UI manager
        input_text = self.ui_manager.get_input_text()
        if not input_text:
            print("Input widget is empty. Aborting LLM call.")
            return # Don't proceed if input is empty

        # Determine the final prompt
        if prompt_def.get("label") == "Custom Prompt":
            # Show custom prompt entry and get text from it via UI manager
            self.ui_manager.show_custom_prompt_entry()
            # Populate the custom prompt entry with the default template if empty
            if not self.ui_manager.get_custom_prompt_text():
                 # Find the custom prompt definition to get the template
                custom_prompt_template = ""
                input_type = self._determine_input_type(input_text)
                prompts = self.state_manager.get_prompts_config().get(input_type, [])
                for p in prompts:
                    if p.get("label") == "Custom Prompt":
                        custom_prompt_template = p.get("prompt", "")
                        break
                self.ui_manager.set_custom_prompt_text(custom_prompt_template)

            from_language = self.ui_manager.get_source_language()
            to_language = self.ui_manager.get_target_language()
            final_prompt = self.ui_manager.get_custom_prompt_text().replace("{text}", input_text).replace("{from_language}", from_language).replace("{to_language}", to_language)
            # Focus is set in show_custom_prompt_entry
        else:
            self.ui_manager.hide_custom_prompt_entry()
            # Use the prompt template from prompts.json and replace the placeholder
            prompt_template = prompt_def.get("prompt", "{text}")
            from_language = self.ui_manager.get_source_language()
            to_language = self.ui_manager.get_target_language()
            final_prompt = prompt_template.replace("{text}", input_text).replace("{from_language}", from_language).replace("{to_language}", to_language)


        print(f"Final prompt sent to LLM: {final_prompt}")

        # Get API key and model name from state manager
        config = self.state_manager.get_config()
        api_key = config.get("api_key")
        model_name = config.get("llm_model", "")

        if not api_key:
            print("API key is missing. Cannot call LLM.")
            # Optionally show an error message in the UI
            self._update_ui_after_llm("Error: API key is missing. Please go to settings.json to add it.")
            return

        # Disable UI while processing via UI manager
        self.ui_manager.toggle_main_widgets_state(tk.DISABLED)
        # Use load_html to display "Processing..." as HtmlFrame doesn't have insert/delete
        self.ui_manager.update_output_html("<p>Processing...</p>")

        # Run the async LLM call in a separate thread
        def run_llm_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(get_llm_response(api_key, model_name, final_prompt))
                # Schedule UI update on the main thread
                self.ui_manager.root.after(0, self._update_ui_after_llm, response)
            except Exception as e:
                self.ui_manager.root.after(0, self._update_ui_after_llm, f"An unexpected error occurred: {e}")
            finally:
                loop.close()

        llm_thread = threading.Thread(target=run_llm_async)
        llm_thread.start()


    def _on_hotkey_triggered(self):
        """Handles actions when the global hotkey is triggered."""
        try:
            # Read content from the clipboard
            clipboard_content = pyperclip.paste()

            # Handle edge cases: empty or non-text clipboard
            if not clipboard_content or not isinstance(clipboard_content, str):
                print("Hotkey triggered, but clipboard is empty or not text. Ignoring.")
                return # Ignore silently as per spec

            # Display the main window and bring it into focus via TrayManager (handled in App)
            self.tray_manager.show_window()

            # Populate the input widget with the captured text via UI manager
            self.ui_manager.set_input_text(clipboard_content)

            # Determine input type and create processing buttons via UI manager
            input_text = self.ui_manager.get_input_text()
            input_type = self._determine_input_type(input_text)
            # Pass the button click handler callback
            self.ui_manager.create_processing_buttons(input_type, self._on_prompt_button_click)

            # Trigger the click event for the first button (the default one)
            # This logic needs to be handled carefully to ensure the button exists and the callback is correct
            # It might be better to trigger the logic directly rather than simulating a button click
            if getattr(self.ui_manager, '_prompt_buttons', []):
                 # Get the corresponding prompt definition
                prompts = self.state_manager.get_prompts_config().get(input_type, [])
                if prompts:
                    default_prompt_def = prompts[0]
                    # Call the button click handler directly with the first button and its definition
                    self._on_prompt_button_click(self.ui_manager._prompt_buttons[0], default_prompt_def)

        except pyperclip.PyperclipException as e:
            print(f"Error handling hotkey trigger (PyperclipException): {e}")
        # except Exception as e:
        #     # Log or handle unexpected exceptions
        #     print(f"Unexpected error handling hotkey trigger: {e}")
        
    def process_input_from_enter(self):
        """Triggers processing based on the currently selected prompt option when Enter is pressed."""
        print("Enter key pressed. Initiating processing.")
        # Get the label of the currently pressed prompt button
        selected_prompt_label = self.ui_manager.get_pressed_prompt_button_label()
        if not selected_prompt_label:
            print("No prompt button selected. Cannot process.")
            return

        # Determine input type to get the correct prompt configuration
        input_text = self.ui_manager.get_input_text()
        input_type = self._determine_input_type(input_text)
        prompts = self.state_manager.get_prompts_config().get(input_type, [])

        # Find the corresponding prompt definition
        selected_prompt_def = None
        for p in prompts:
            if p.get("label") == selected_prompt_label:
                selected_prompt_def = p
                break

        if selected_prompt_def:
            # Call the existing button click handler with a dummy button and the found definition
            # The _on_prompt_button_click method doesn't strictly need a real button object
            # for its logic, only the prompt_def.
            self._on_prompt_button_click(None, selected_prompt_def)
        else:
            print(f"Error: Could not find prompt definition for label '{selected_prompt_label}'")


    def _on_input_text_change(self):
        """Handles changes in the input widget text to update processing buttons."""
        input_text = self.ui_manager.get_input_text()
        input_type = self._determine_input_type(input_text)
        # Recreate processing buttons based on the new input type
        self.ui_manager.create_processing_buttons(input_type, self._on_prompt_button_click)


    def _update_ui_after_llm(self, response_text):
        """Updates the UI with the LLM response (rendered Markdown) and re-enables widgets."""
        # Use the CSS content loaded via load_css
        css_content = self.css_content

        # Store the raw LLM response
        self._last_raw_llm_response = response_text

        # Render Markdown to HTML
        html_content = render_markdown_to_html(response_text, css_content)

        # Store the rendered HTML
        self._last_rendered_html = html_content

        # Update the HtmlFrame widget via UI manager
        self.ui_manager.update_output_html(html_content)

        # Re-enable UI via UI manager
        self.ui_manager.toggle_main_widgets_state(tk.NORMAL)
        print("LLM call finished. UI re-enabled.")

    def copy_output(self):
        """Copies the plain text output to the clipboard."""
        if not self._last_raw_llm_response:
            print("No output to copy.")
            return

        try:
            plain_text = _markdown_to_plain_text(self._last_raw_llm_response)
            pyperclip.copy(plain_text)
            print("Plain text copied to clipboard.")
        except pyperclip.PyperclipException as e:
            print(f"Error copying to clipboard: {e}")

    def copy_output_with_formatting(self):
        """Copies the HTML output to the clipboard using the ClipboardManager."""
        if not self._last_rendered_html:
            print("No formatted output to copy.")
            return

        success = self.clipboard_manager.copy_html_with_formatting(_markdown_to_plain_text(self._last_raw_llm_response) ,self._last_rendered_html)
        if success:
            print("Formatted output copied to clipboard.")
        else:
            print("Failed to copy formatted output.")
