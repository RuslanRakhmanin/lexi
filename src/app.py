# pylint: disable=line-too-long

"""Main application for the Lexi text assistant with system tray integration."""
import tkinter as tk
from tkinter import ttk
from tray_manager import TrayManager # Import TrayManager

class App(tk.Tk):
    """Main application class for the Lexi text assistant."""
    def __init__(self):
        super().__init__()

        self.tray_manager = TrayManager(self) # Create TrayManager instance
        self.tray_manager.create_icon() # Create the system tray icon

        self.title("Lexi - Gemini-Powered Text Assistant")
        # self.geometry("500x600") # Optional: set a default size

        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # 1. Language Selectors
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        from_label = ttk.Label(lang_frame, text="From:")
        from_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.source_lang_combo = ttk.Combobox(lang_frame, values=["English", "Spanish", "French", "German", "Ukrainian", "Russian"], width=15)
        self.source_lang_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.source_lang_combo.set("English")

        to_label = ttk.Label(lang_frame, text="To:")
        to_label.pack(side=tk.LEFT, padx=(0, 5))

        self.target_lang_combo = ttk.Combobox(lang_frame, values=["Ukrainian", "Russian", "English", "Spanish", "French", "German"], width=15)
        self.target_lang_combo.pack(side=tk.LEFT)
        self.target_lang_combo.set("Russian")

        # 2. Input Widget
        self.input_widget = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.input_widget.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # 3. Processing Options (Placeholder)
        self.processing_options_frame = ttk.Frame(main_frame)
        self.processing_options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        # Buttons will be added dynamically here later

        # 4. Custom Prompt Input (Initially hidden)
        self.custom_prompt_entry = ttk.Entry(main_frame)
        # self.custom_prompt_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5) # Will be shown when needed

        # 5. Output Widget
        self.output_widget = tk.Text(main_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.output_widget.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(4, weight=1) # Allow output widget to expand

        # 6. Action Buttons
        action_button_frame = ttk.Frame(main_frame)
        action_button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.E,), pady=(10, 0))

        self.copy_button = ttk.Button(action_button_frame, text="Copy")
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.copy_with_formatting_button = ttk.Button(action_button_frame, text="Copy with Formatting")
        self.copy_with_formatting_button.pack(side=tk.LEFT)

if __name__ == "__main__":
    app = App()

    # Handle closing the window via the 'X' button and hiding to tray
    def on_closing():
        app.tray_manager.toggle_window_visibility(None, None) # Hide the window instead of destroying

    app.protocol("WM_DELETE_WINDOW", on_closing)

    app.mainloop()
    app.tray_manager.stop_icon() # Ensure icon is stopped when mainloop exits
