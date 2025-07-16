# pylint: disable=line-too-long

import tkinter as tk
from tkinter import ttk
import tkinterweb

class UIManager:
    """Manages the Tkinter user interface elements for the Lexi application."""

    def __init__(self, root, prompts_config, css_content, config):
        """
        Initializes the UIManager.

        Args:
            root: The root Tkinter window (the App instance).
            prompts_config: The loaded prompts configuration.
            css_content: The loaded CSS content for HTML rendering.
            config: The loaded application configuration.
        """
        self.root = root
        self.prompts_config = prompts_config
        self.css_content = css_content
        self.config = config

        self._input_widget_modified_proxy = None  # Proxy for input widget modification events

        # Widgets that need to be disabled/enabled
        self._main_widgets = []
        self._prompt_buttons = [] # Store references to prompt buttons

        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        """Creates all the main UI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")

        # 1. Language Selectors
        self.lang_frame = ttk.Frame(self.main_frame)
        self.from_label = ttk.Label(self.lang_frame, text="From:")
        self.source_lang_combo = ttk.Combobox(self.lang_frame, values=self.config.get("source_languages", []), width=15)
        self.to_label = ttk.Label(self.lang_frame, text="To:")
        self.target_lang_combo = ttk.Combobox(self.lang_frame, values=self.config.get("target_languages", []), width=15)

        self._main_widgets.extend([self.source_lang_combo, self.target_lang_combo])

        # 2. Input Widget
        self.input_widget = tk.Text(self.main_frame, height=5, wrap=tk.WORD)
        self._main_widgets.append(self.input_widget)

        # 3. Processing Options Frame (Buttons added dynamically)
        self.processing_options_frame = ttk.Frame(self.main_frame)
        self._main_widgets.append(self.processing_options_frame) # Add the frame containing buttons

        # 4. Custom Prompt Input (Initially hidden)
        self.custom_prompt_entry = ttk.Entry(self.main_frame)
        self._main_widgets.append(self.custom_prompt_entry)

        # 5. Output Widget (HtmlFrame)
        self.output_widget = tkinterweb.HtmlFrame(self.main_frame, height=10, messages_enabled = False)
        # HtmlFrame does not have a 'state' option, so we don't add it to _main_widgets.

        # 6. Action Buttons Frame
        self.action_button_frame = ttk.Frame(self.main_frame)
        self._main_widgets.append(self.action_button_frame) # Add the frame containing buttons

        self.copy_button = ttk.Button(self.action_button_frame, text="Copy")
        self.copy_with_formatting_button = ttk.Button(self.action_button_frame, text="Copy with Formatting")

        # API Key Frame (Initially hidden)
        self.api_key_frame = ttk.Frame(self.root, padding="10")
        self.api_key_label = ttk.Label(self.api_key_frame, text="Please enter your Gemini API key:")
        self.api_key_entry = ttk.Entry(self.api_key_frame, width=50)
        self.save_button = ttk.Button(self.api_key_frame, text="Save Key")


    def _setup_layout(self):
        """Sets up the grid layout for the main UI elements."""
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Configure columns and rows within main_frame for responsiveness
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=0) # Language selectors row
        self.main_frame.rowconfigure(1, weight=0) # Input widget row - make this resizable
        self.main_frame.rowconfigure(2, weight=0) # Separator row (not used currently, but kept for structure)
        self.main_frame.rowconfigure(3, weight=0) # Custom prompt entry / Sizegrip row (Sizegrip commented out)
        self.main_frame.rowconfigure(4, weight=0) # Processing options row
        self.main_frame.rowconfigure(5, weight=1) # Output widget row - make this resizable
        self.main_frame.rowconfigure(6, weight=0) # Action buttons row

        # 1. Language Selectors
        self.lang_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.from_label.pack(side=tk.LEFT, padx=(0, 5))
        self.source_lang_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.to_label.pack(side=tk.LEFT, padx=(0, 5))
        self.target_lang_combo.pack(side=tk.LEFT)

        # 2. Input Widget
        self.input_widget.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # 3. Processing Options Frame
        self.processing_options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        # 4. Custom Prompt Input (Initially hidden)
        # self.custom_prompt_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5) # Will be shown when needed

        # 5. Output Widget
        self.output_widget.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # 6. Action Buttons Frame
        self.action_button_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.E, tk.W), pady=(10, 0))
        self.copy_button.pack(side=tk.LEFT, padx=5)
        self.copy_with_formatting_button.pack(side=tk.LEFT)

    def create_processing_buttons(self, input_type, on_button_click_callback):
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
            # Use the provided callback for the command
            button.config(command=lambda b=button, p=prompt_def: on_button_click_callback(b, p))
            button.pack(side=tk.LEFT, padx=2)
            self._prompt_buttons.append(button) # Add button to the list

        # Set the first button as initially pressed by adding the 'pressed' state
        if self._prompt_buttons:
            self._prompt_buttons[0].state(['pressed'])

    def toggle_main_widgets_state(self, state):
        """Enables or disables the main application widgets."""
        for widget in self._main_widgets:
            try:
                widget.config(state=state)
            except tk.TclError:
                # Some widgets like Frames don't have a 'state' option
                pass

    def show_api_key_input(self, save_api_key_callback):
        """Shows the API key input frame and hides the main frame."""
        self.main_frame.grid_forget() # Hide main frame
        self.api_key_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.api_key_label.pack(pady=(0, 5))
        self.api_key_entry.pack(pady=(0, 10))
        self.api_key_entry.focus_set() # Set focus to the entry field

        # Bind the Enter key to save the API key
        self.api_key_entry.bind("<Return>", save_api_key_callback)

        # Optional: Add a save button
        self.save_button.config(command=save_api_key_callback)
        self.save_button.pack()

    def hide_api_key_input(self):
        """Hides the API key input frame and shows the main frame."""
        self.api_key_frame.grid_forget() # Hide the API key input
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S)) # Show main frame

    def get_input_text(self):
        """Gets the text from the input widget."""
        return self.input_widget.get("1.0", tk.END).strip()

    def set_input_text(self, text):
        """Sets the text in the input widget."""
        self.input_widget.delete("1.0", tk.END)
        self.input_widget.insert("1.0", text)

    def get_source_language(self):
        """Gets the selected source language."""
        return self.source_lang_combo.get()

    def set_source_language(self, lang):
        """Sets the selected source language."""
        if lang and lang in self.source_lang_combo['values']:
            self.source_lang_combo.set(lang)
        else:
            self.source_lang_combo.set("English") # Default

    def get_target_language(self):
        """Gets the selected target language."""
        return self.target_lang_combo.get()

    def set_target_language(self, lang):
        """Sets the selected target language."""
        if lang and lang in self.target_lang_combo['values']:
            self.target_lang_combo.set(lang)
        else:
            self.target_lang_combo.set("Ukrainian") # Default

    def get_custom_prompt_text(self):
        """Gets the text from the custom prompt entry."""
        return self.custom_prompt_entry.get()

    def set_custom_prompt_text(self, text):
        """Sets the text in the custom prompt entry."""
        self.custom_prompt_entry.delete(0, tk.END)
        self.custom_prompt_entry.insert(0, text)

    def show_custom_prompt_entry(self):
        """Shows the custom prompt entry."""
        self.custom_prompt_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.custom_prompt_entry.focus_set() # Set focus to the custom prompt entry

    def hide_custom_prompt_entry(self):
        """Hides the custom prompt entry."""
        self.custom_prompt_entry.grid_forget()

    def update_output_html(self, html_content):
        """Updates the output widget with HTML content."""
        self.output_widget.load_html(html_content)

    def get_pressed_prompt_button_label(self):
        """Returns the label of the currently pressed prompt button, or None."""
        for button in self._prompt_buttons:
            if button.instate(['pressed']):
                return button.cget('text')
        return None # Should not happen if buttons are created and one is always pressed

    def set_prompt_button_pressed_state(self, button_label):
        """Sets the 'pressed' state for the button with the given label."""
        found_button = False
        for button in getattr(self, '_prompt_buttons', []):
            if button.cget('text') == button_label:
                button.state(['pressed'])
                found_button = True
            else:
                button.state(['!pressed']) # Ensure others are not pressed
        # If the saved option is not found among the current buttons,
        # ensure the first button is still pressed as a fallback.
        if not found_button and getattr(self, '_prompt_buttons', []):
            self._prompt_buttons[0].state(['pressed'])
            print("Saved processing option not found. Defaulting to first option.")

    def bind_copy_button(self, command):
        """Binds a command to the Copy button."""
        self.copy_button.config(command=command)

    def bind_copy_with_formatting_button(self, command):
        """Binds a command to the Copy with Formatting button."""
        self.copy_with_formatting_button.config(command=command)

    def bind_input_widget_change(self, callback):
        """Binds a callback function to the input widget's text change event."""
        # Create a proxy to manage the <<Modified>> event flag
        self._input_widget_modified_proxy = self.input_widget.bind("<<Modified>>", lambda e: self._input_widget_modified(callback))
        # Reset the flag initially
        self.input_widget.edit_modified(False)

    def _input_widget_modified(self, callback):
        """Internal handler for the <<Modified>> event."""
        # Check the modified flag
        if self.input_widget.edit_modified():
            # Call the provided callback
            callback()
            # Reset the modified flag
            # self.input_widget.edit_reset()
            self.input_widget.edit_modified(False)

    def bind_escape_key(self, callback):
        """Binds a callback function to the Escape key press event on the root window."""
        self.root.bind('<Escape>', lambda event: callback())

    def bind_input_key_press(self, process_callback):
        """Binds key press events to the input widget."""
        self.input_widget.bind('<Return>', lambda event: self._on_input_key_press(event, process_callback))
        self.input_widget.bind('<Shift-Return>', lambda event: self._on_input_key_press(event, process_callback))

    def _on_input_key_press(self, event, process_callback):
        """Handles key press events in the input widget."""
        if event.state & 0x1:  # Check if Shift key is pressed (event.state is a bitmask)
            # Shift + Enter: Insert a newline character
            self.input_widget.insert(tk.INSERT, "\n")
            return "break"  # Prevent default Tkinter behavior (which would add another newline)
        else:
            # Enter: Trigger processing
            process_callback()
            return "break"  # Prevent default Tkinter behavior (which would add a newline)
