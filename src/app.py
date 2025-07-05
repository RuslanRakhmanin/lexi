# pylint: disable=line-too-long

"""Main application for the Lexi text assistant with system tray integration."""
import os # Import os for path joining
import asyncio
import threading
import tkinter as tk
from tkinter import ttk
from hotkey_manager import HotkeyListener # Import HotkeyListener
import pyperclip # Import pyperclip for clipboard access
from config_manager import load_config, save_config, load_prompts # Import config manager functions
from gemini_client import get_llm_response # Import the LLM function
import tkinterweb # Import tkinterweb
from markdown_renderer import render_markdown_to_html # Import the markdown renderer
from tray_manager import TrayManager # Import TrayManager

class App(tk.Tk):
    """Main application class for the Lexi text assistant."""
    def __init__(self):
        super().__init__()

        self.config_filepath = os.path.join("config", "settings.json")
        try:
            self.config = load_config(self.config_filepath)
        except ValueError as e:
            print(f"Fatal Error loading settings.json: {e}")
            print("Application will exit.")
            self.destroy() # Exit the application
            return # Stop initialization

        # Restore window geometry if available in config
        window_geometry = self.config.get("window_geometry")
        if window_geometry:
            try:
                self.geometry(window_geometry)
                print(f"Restored window geometry: {window_geometry}")
            except tk.TclError as e:
                print(f"Error restoring window geometry '{window_geometry}': {e}")
                # Optionally set a default size if restoration fails
                # self.geometry("800x600")

        # Restore selected languages if available in config
        source_language = self.config.get("source_language")
        target_language = self.config.get("target_language")

        self.prompts_filepath = os.path.join("config", "prompts.json")
        self.prompts_config = load_prompts(self.prompts_filepath) # Load prompts using the new function

        # Load CSS content once at startup
        self.css_content = ""
        css_filepath = os.path.join("config", "styles.css")
        try:
            with open(css_filepath, "r", encoding="utf-8") as f:
                self.css_content = f.read()
        except FileNotFoundError:
            print(f"Error: {css_filepath} not found.")
        except Exception as e:
            print(f"Error reading {css_filepath}: {e}")

        # Widgets that need to be disabled/enabled
        self._main_widgets = []

        self.tray_manager = TrayManager(self) # Create TrayManager instance
        self.tray_manager.create_icon() # Create the system tray icon

        # Initialize and start the HotkeyListener
        self.hotkey_listener = HotkeyListener(self._on_hotkey_triggered)
        self.hotkey_listener.start()

        self.title("Lexi - Gemini-Powered Text Assistant")
        # self.geometry("500x600") # Optional: set a default size

        # Main frame
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Configure columns and rows within main_frame for responsiveness
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=0) # Language selectors row
        self.main_frame.rowconfigure(1, weight=0) # Input widget row - make this resizable
        self.main_frame.rowconfigure(2, weight=0) # Separator row
        self.main_frame.rowconfigure(3, weight=0) # Custom prompt entry / Sizegrip row
        self.main_frame.rowconfigure(4, weight=0) # Processing options row
        self.main_frame.rowconfigure(5, weight=1) # Output widget row - make this resizable
        self.main_frame.rowconfigure(6, weight=0) # Action buttons row

        # 1. Language Selectors
        lang_frame = ttk.Frame(self.main_frame)
        lang_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        from_label = ttk.Label(lang_frame, text="From:")
        from_label.pack(side=tk.LEFT, padx=(0, 5))

        self.source_lang_combo = ttk.Combobox(lang_frame, values=["English", "Spanish", "French", "German", "Ukrainian", "Russian"], width=15)
        self.source_lang_combo.pack(side=tk.LEFT, padx=(0, 10))
        # Set initial value from config or default
        if source_language and source_language in self.source_lang_combo['values']:
            self.source_lang_combo.set(source_language)
        else:
            self.source_lang_combo.set("English")
        self._main_widgets.append(self.source_lang_combo)

        to_label = ttk.Label(lang_frame, text="To:")
        to_label.pack(side=tk.LEFT, padx=(0, 5))

        self.target_lang_combo = ttk.Combobox(lang_frame, values=["Ukrainian", "Russian", "English", "Spanish", "French", "German"], width=15)
        self.target_lang_combo.pack(side=tk.LEFT)
        # Set initial value from config or default
        if target_language and target_language in self.target_lang_combo['values']:
            self.target_lang_combo.set(target_language)
        else:
            self.target_lang_combo.set("Ukrainian")
        self._main_widgets.append(self.target_lang_combo)

        # 2. Input Widget
        self.input_widget = tk.Text(self.main_frame, height=5, wrap=tk.WORD)
        self.input_widget.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self._main_widgets.append(self.input_widget)

        # # Add a Separator below the input widget
        # self.input_output_separator = ttk.Separator(self.main_frame, orient=tk.HORIZONTAL)
        # self.input_output_separator.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # # Add a Sizegrip for resizing
        # self.sizegrip = ttk.Sizegrip(self.main_frame)
        # # Place the sizegrip in the bottom-right corner of the resizable area
        # self.sizegrip.grid(row=3, column=1, sticky=(tk.S, tk.E)) # Placed in row 3, column 1

        # 3. Processing Options (Placeholder) - This is now in row 4
        self.processing_options_frame = ttk.Frame(self.main_frame)
        self.processing_options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        # Buttons will be added dynamically here later
        self._main_widgets.append(self.processing_options_frame)

        # Determine initial input type based on potential saved input or default
        initial_input_text = self.input_widget.get("1.0", tk.END).strip() # Get initial text (might be empty)
        initial_input_type = self._determine_input_type(initial_input_text) if initial_input_text else "phrase" # Default to "phrase" if no text

        self._create_processing_buttons(initial_input_type) # Create buttons based on initial input type

        # Restore last selected processing option if available in config
        last_processing_option = self.config.get("last_processing_option")
        if last_processing_option and getattr(self, '_prompt_buttons', []):
            found_button = False
            for button in self._prompt_buttons:
                if button.cget('text') == last_processing_option:
                    button.state(['pressed'])
                    found_button = True
                    print(f"Restored last processing option: {last_processing_option}")
                    break
            # If the saved option is not found among the current buttons,
            # ensure the first button is still pressed as a fallback.
            if not found_button and self._prompt_buttons:
                self._prompt_buttons[0].state(['pressed'])
                print("Saved processing option not found. Defaulting to first option.")


        # 4. Custom Prompt Input (Initially hidden)
        self.custom_prompt_entry = ttk.Entry(self.main_frame)
        # self.custom_prompt_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5) # Will be shown when needed
        self._main_widgets.append(self.custom_prompt_entry)

        # 5. Output Widget
        # 5. Output Widget - This is now in row 5
        # Use tkinterweb.HtmlFrame for Markdown rendering
        self.output_widget = tkinterweb.HtmlFrame(self.main_frame, height=10)
        self.output_widget.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        # The rowconfigure for row 5 is moved up to the main_frame configuration section
        # Note: HtmlFrame does not have a 'state' option like tk.Text,
        # so we won't add it to _main_widgets for state toggling.
        # We will manage its content directly.

        # 6. Action Buttons - This is now in row 6
        action_button_frame = ttk.Frame(self.main_frame)
        action_button_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.E, tk.W), pady=(10, 0))
        self._main_widgets.append(action_button_frame) # Add the frame containing buttons

        self.copy_button = ttk.Button(action_button_frame, text="Copy")
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.copy_with_formatting_button = ttk.Button(action_button_frame, text="Copy with Formatting")
        self.copy_with_formatting_button.pack(side=tk.LEFT)

        self.check_api_key() # Check API key on startup

    def _determine_input_type(self, text):
        """Determines if the input text is a 'word' or 'phrase'."""
        return "word" if len(text.strip().split()) == 1 else "phrase"

    def _create_processing_buttons(self, input_type):
        """Creates buttons on the processing_options_frame based on input type."""
        # Clear existing buttons
        for widget in self.processing_options_frame.winfo_children():
            widget.destroy()

        prompts = self.prompts_config.get(input_type, []) # Get prompts for the type, default to empty list

        self._prompt_buttons = [] # Store references to prompt buttons

        for prompt_def in prompts:
            label = prompt_def.get("label", "Unknown Prompt")
            # Correctly capture button and prompt_def in the lambda and apply the custom style
            button = ttk.Button(self.processing_options_frame, text=label, style="Prompt.TButton")
            button.config(command=lambda b=button, p=prompt_def: self._on_prompt_button_click(b, p))
            button.pack(side=tk.LEFT, padx=2)
            self._prompt_buttons.append(button) # Add button to the list

        # Set the first button as initially pressed by adding the 'pressed' state
        if self._prompt_buttons:
            self._prompt_buttons[0].state(['pressed'])


    def _on_prompt_button_click(self, clicked_button, prompt_def):
        """Handles a prompt button click, updates visual state, and triggers action."""
        print(f"Prompt button clicked: {prompt_def.get('label')}")

        # Update visual state of buttons using states
        for button in self._prompt_buttons:
            if button == clicked_button:
                button.state(['pressed']) # Set the clicked button to the 'pressed' state
            else:
                button.state(['!pressed']) # Remove the 'pressed' state from other buttons

        # Get input text
        input_text = self.input_widget.get("1.0", tk.END).strip()
        if not input_text:
            print("Input widget is empty. Aborting LLM call.")
            return # Don't proceed if input is empty

        # Determine the final prompt
        if prompt_def.get("label") == "Custom Prompt":
            # Show custom prompt entry and get text from it
            self.custom_prompt_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            # Populate the custom prompt entry with the default template if empty
            if not self.custom_prompt_entry.get():
                 # Find the custom prompt definition to get the template
                custom_prompt_template = ""
                input_type = self._determine_input_type(input_text)
                prompts = self.prompts_config.get(input_type, [])
                for p in prompts:
                    if p.get("label") == "Custom Prompt":
                        custom_prompt_template = p.get("prompt", "")
                        break
                self.custom_prompt_entry.delete(0, tk.END)
                self.custom_prompt_entry.insert(0, custom_prompt_template)

            from_language = self.source_lang_combo.get()
            to_language = self.target_lang_combo.get()
            final_prompt = self.custom_prompt_entry.get().replace("{text}", input_text).replace("{from_language}", from_language).replace("{to_language}", to_language)
            self.custom_prompt_entry.focus_set() # Set focus to the custom prompt entry
        else:
            self.custom_prompt_entry.grid_forget()
            # Use the prompt template from prompts.json and replace the placeholder
            prompt_template = prompt_def.get("prompt", "{text}")
            from_language = self.source_lang_combo.get()
            to_language = self.target_lang_combo.get()
            final_prompt = prompt_template.replace("{text}", input_text).replace("{from_language}", from_language).replace("{to_language}", to_language)


        print(f"Final prompt sent to LLM: {final_prompt}")

        # Get API key and model name
        api_key = self.config.get("api_key")
        model_name = self.config.get("llm_model", "")

        if not api_key:
            print("API key is missing. Cannot call LLM.")
            # Optionally show an error message in the UI
            self._update_ui_after_llm("Error: API key is missing. Please go to settings.json to add it.")
            return

        # Disable UI while processing
        self.toggle_main_widgets_state(tk.DISABLED)
        # Use load_html to display "Processing..." as HtmlFrame doesn't have insert/delete
        self.output_widget.load_html("<p>Processing...</p>")
        # HtmlFrame doesn't have a 'state' option, so we don't need to toggle it here.

        # Run the async LLM call in a separate thread
        def run_llm_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(get_llm_response(api_key, model_name, final_prompt))
                # Schedule UI update on the main thread
                self.after(0, self._update_ui_after_llm, response)
            except Exception as e:
                self.after(0, self._update_ui_after_llm, f"An unexpected error occurred: {e}")
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

            # Display the main window and bring it into focus
            self.tray_manager.show_window()

            # Populate the input widget with the captured text
            self.input_widget.delete("1.0", tk.END)
            self.input_widget.insert("1.0", clipboard_content)

            # Determine input type and create processing buttons
            input_text = self.input_widget.get("1.0", tk.END).strip()
            input_type = self._determine_input_type(input_text)
            self._create_processing_buttons(input_type)

            # Trigger the click event for the first button (the default one)
            if self._prompt_buttons:
                # Get the corresponding prompt definition
                prompts = self.prompts_config.get(input_type, [])
                if prompts:
                    default_prompt_def = prompts[0]
                    # Call the button click handler directly
                    self._on_prompt_button_click(self._prompt_buttons[0], default_prompt_def)


        except tk.TclError as e:
            print(f"Error handling hotkey trigger (TclError): {e}")
        except pyperclip.PyperclipException as e:
            print(f"Error handling hotkey trigger (PyperclipException): {e}")
        # except Exception as e:
        #     # Log or handle unexpected exceptions
        #     print(f"Unexpected error handling hotkey trigger: {e}")

    def _update_ui_after_llm(self, response_text):
        """Updates the UI with the LLM response (rendered Markdown) and re-enables widgets."""
        # Use the CSS content loaded at startup
        css_content = self.css_content

        # Render Markdown to HTML
        html_content = render_markdown_to_html(response_text, css_content)

        # Update the HtmlFrame widget
        self.output_widget.load_html(html_content)

        # Re-enable UI
        self.toggle_main_widgets_state(tk.NORMAL)
        print("LLM call finished. UI re-enabled.")

    def toggle_main_widgets_state(self, state):
        """Enables or disables the main application widgets."""
        for widget in self._main_widgets:
            try:
                widget.config(state=state)
            except tk.TclError:
                # Some widgets like Frames don't have a 'state' option
                pass

    def save_api_key(self, event=None):
        """Saves the entered API key to settings.json and unlocks the UI."""
        api_key = self.api_key_entry.get().strip()
        if api_key:
            self.config['api_key'] = api_key
            save_config(self.config_filepath, self.config)
            self.api_key_frame.destroy() # Hide the API key input
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S)) # Show main frame
            self.toggle_main_widgets_state(tk.NORMAL) # Unlock UI
            print("API key saved and UI unlocked.")
        else:
            print("API key cannot be empty.")


    def check_api_key(self):
        """Checks if the API key is present and prompts the user if missing."""
        api_key = self.config.get("api_key")

        if not api_key:
            print("API key missing. Prompting user.")
            self.main_frame.grid_forget() # Hide main frame
            self.toggle_main_widgets_state(tk.DISABLED) # Disable UI

            # Create a frame for API key input
            self.api_key_frame = ttk.Frame(self, padding="10")
            self.api_key_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=1)

            api_key_label = ttk.Label(self.api_key_frame, text="Please enter your Gemini API key:")
            api_key_label.pack(pady=(0, 5))

            self.api_key_entry = ttk.Entry(self.api_key_frame, width=50)
            self.api_key_entry.pack(pady=(0, 10))
            self.api_key_entry.focus_set() # Set focus to the entry field

            # Bind the Enter key to save the API key
            self.api_key_entry.bind("<Return>", self.save_api_key)

            # Optional: Add a save button
            save_button = ttk.Button(self.api_key_frame, text="Save Key", command=self.save_api_key)
            save_button.pack()

        else:
            print("API key found. UI is unlocked.")
            # UI is already unlocked by default, nothing to do here


    def save_window_state(self):
        """Saves the current window state (geometry, languages, processing option) to settings.json."""
        try:
            # Save window geometry
            current_geometry = self.geometry()
            self.config['window_geometry'] = current_geometry

            # Save selected languages
            self.config['source_language'] = self.source_lang_combo.get()
            self.config['target_language'] = self.target_lang_combo.get()

            # Save last selected processing option
            last_processing_option = None
            for button in getattr(self, '_prompt_buttons', []): # Use getattr with default to handle cases before buttons are created
                if button.instate(['pressed']):
                    last_processing_option = button.cget('text') # Get the button text (label)
                    break
            if last_processing_option:
                self.config['last_processing_option'] = last_processing_option
                print(f"Saved last processing option: {last_processing_option}")
            else:
                 # If no button is pressed (e.g., on initial startup before any button is clicked)
                 # try to get the default from the first button if available
                if getattr(self, '_prompt_buttons', []):
                    last_processing_option = self._prompt_buttons[0].cget('text')
                    self.config['last_processing_option'] = last_processing_option
                    print(f"Saved default processing option: {last_processing_option}")


            # Save the updated config
            save_config(self.config_filepath, self.config)
            print(f"Saved window geometry: {current_geometry}, source: {self.config['source_language']}, target: {self.config['target_language']}")

        except Exception as e:
            print(f"Error saving window state: {e}")


if __name__ == "__main__":
    app = App()

    # Handle closing the window via the 'X' button and hiding to tray
    def on_closing():
        app.tray_manager.toggle_window_visibility(None, None) # Hide the window instead of destroying

    app.protocol("WM_DELETE_WINDOW", on_closing)

    app.mainloop()

    # Save window state and stop threads when mainloop exits
    app.save_window_state() # Save window state before exiting
    app.tray_manager.stop_icon() # Ensure icon is stopped when mainloop exits
    app.hotkey_listener.stop() # Ensure hotkey listener is stopped
    app.hotkey_listener.join() # Wait for the hotkey listener thread to finish
