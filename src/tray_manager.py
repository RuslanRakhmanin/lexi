# This module manages the system tray icon and its interactions with the main application window."""
import tkinter as tk
import pystray
from PIL import Image


class TrayManager:
    """The class manages the system tray icon and interactions with the main application window."""
    def __init__(self, window: tk.Tk):
        self.window = window
        self.icon = None
        self.is_window_visible = True

    def create_icon(self):
        # Create a dummy image for the icon

        image = Image.new('RGB', (64, 64), color = 'green')

        menu = (
            pystray.MenuItem('Show/Hide Window', self.toggle_window_visibility),
            pystray.MenuItem('Exit', self.exit_application)
        )

        self.icon = pystray.Icon("lexi_app", image, "Lexi App", menu)
        self.icon.run_detached() # Run the icon in a separate thread

        # Handle double-click (pystray doesn't have a direct double-click event,
        # but we can simulate it or rely on the menu for show/hide)
        # For simplicity, we'll rely on the menu item for now.
        # A more advanced implementation might involve platform-specific hooks.

    def toggle_window_visibility(self, icon, item):
        if self.is_window_visible:
            self.window.withdraw() # Hide the window
            self.is_window_visible = False
        else:
            self.window.deiconify() # Show the window
            self.window.lift() # Bring window to front
            self.is_window_visible = True

    def exit_application(self, icon, item):
        icon.stop()
        self.window.quit() # Exit the tkinter application

    def stop_icon(self):
        if self.icon:
            self.icon.stop()
