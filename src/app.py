# pylint: disable=line-too-long

"""Main application for the Lexi text assistant with system tray integration."""
import tkinter as tk
from tkinter import ttk
from tray_manager import TrayManager # Import TrayManager
from hotkey_manager import HotkeyListener # Import HotkeyListener
import pyperclip # Import pyperclip for clipboard access
# json import is no longer needed here as prompts loading is in config_manager
from config_manager import load_config, save_config, load_prompts # Import config manager functions
import os # Import os for path joining

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

        self.prompts_filepath = os.path.join("config", "prompts.json")
        self.prompts_config = load_prompts(self.prompts_filepath) # Load prompts using the new function

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

        # 1. Language Selectors
        lang_frame = ttk.Frame(self.main_frame)
        lang_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        from_label = ttk.Label(lang_frame, text="From:")
        from_label.pack(side=tk.LEFT, padx=(0, 5))

        self.source_lang_combo = ttk.Combobox(lang_frame, values=["English", "Spanish", "French", "German", "Ukrainian", "Russian"], width=15)
        self.source_lang_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.source_lang_combo.set("English")
        self._main_widgets.append(self.source_lang_combo)

        to_label = ttk.Label(lang_frame, text="To:")
        to_label.pack(side=tk.LEFT, padx=(0, 5))

        self.target_lang_combo = ttk.Combobox(lang_frame, values=["Ukrainian", "Russian", "English", "Spanish", "French", "German"], width=15)
        self.target_lang_combo.pack(side=tk.LEFT)
        self.target_lang_combo.set("Russian")
        self._main_widgets.append(self.target_lang_combo)

        # 2. Input Widget
        self.input_widget = tk.Text(self.main_frame, height=10, wrap=tk.WORD)
        self.input_widget.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self._main_widgets.append(self.input_widget)

        # 3. Processing Options (Placeholder)
        self.processing_options_frame = ttk.Frame(self.main_frame)
        self.processing_options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        # Buttons will be added dynamically here later
        self._main_widgets.append(self.processing_options_frame)
        self._create_processing_buttons("phrase") # Start with phrase as a default

        # 4. Custom Prompt Input (Initially hidden)
        self.custom_prompt_entry = ttk.Entry(self.main_frame)
        # self.custom_prompt_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5) # Will be shown when needed
        self._main_widgets.append(self.custom_prompt_entry)

        # 5. Output Widget
        self.output_widget = tk.Text(self.main_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.output_widget.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.main_frame.rowconfigure(4, weight=1) # Allow output widget to expand
        self._main_widgets.append(self.output_widget)

        # 6. Action Buttons
        action_button_frame = ttk.Frame(self.main_frame)
        action_button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.E,), pady=(10, 0))
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

        # Implement the actual action based on prompt_def
        print(f"Selected prompt: {prompt_def}")

        # Show/hide custom prompt entry based on selection
        if prompt_def.get("label") == "Custom Prompt":
            self.custom_prompt_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            # Populate the custom prompt entry with the default template
            # Find the custom prompt definition to get the template
            custom_prompt_template = ""
            input_text = self.input_widget.get("1.0", tk.END).strip()
            input_type = self._determine_input_type(input_text)
            prompts = self.prompts_config.get(input_type, [])
            for p in prompts:
                if p.get("label") == "Custom Prompt":
                    custom_prompt_template = p.get("prompt", "")
                    break
            self.custom_prompt_entry.delete(0, tk.END)
            self.custom_prompt_entry.insert(0, custom_prompt_template)
            self.custom_prompt_entry.focus_set() # Set focus to the custom prompt entry
        else:
            self.custom_prompt_entry.grid_forget()


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


        except tk.TclError as e:
            print(f"Error handling hotkey trigger (TclError): {e}")
        except pyperclip.PyperclipException as e:
            print(f"Error handling hotkey trigger (PyperclipException): {e}")
        # except Exception as e:
        #     # Log or handle unexpected exceptions
        #     print(f"Unexpected error handling hotkey trigger: {e}")

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


if __name__ == "__main__":
    app = App()

    # Handle closing the window via the 'X' button and hiding to tray
    def on_closing():
        app.tray_manager.toggle_window_visibility(None, None) # Hide the window instead of destroying

    app.protocol("WM_DELETE_WINDOW", on_closing)

    app.mainloop()
    app.tray_manager.stop_icon() # Ensure icon is stopped when mainloop exits
    app.hotkey_listener.stop() # Ensure hotkey listener is stopped
    app.hotkey_listener.join() # Wait for the hotkey listener thread to finish
