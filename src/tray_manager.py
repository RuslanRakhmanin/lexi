"""This module manages the system tray icon and its interactions with the main application window."""

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
        """Create system tray icon with graceful fallback for Linux/WSL."""
        # Check if running in WSL
        is_wsl = False
        try:
            with open('/proc/version', 'r') as f:
                is_wsl = 'microsoft' in f.read().lower()
        except:
            pass
            
        if is_wsl:
            print("Info: Running in WSL environment - system tray functionality is not available")
            print("Application will run in windowed mode only")
            self.icon = None
            return
            
        try:
            # Create a dummy image for the icon
            image = Image.open(self.window.icon_filepath)

            menu = (
                pystray.MenuItem('Show/Hide Window', self.toggle_window_visibility, default=True),
                pystray.MenuItem('Exit', self.exit_application)
            )

            self.icon = pystray.Icon("lexi_app", image, "Lexi App", menu)
            self.icon.run_detached() # Run the icon in a separate thread
        except Exception as e:
            print(f"Warning: Could not create system tray icon: {e}")
            print("This is expected in headless environments like WSL or some Linux setups")
            print("Application will continue without system tray functionality")
            self.icon = None

        # Handle double-click (pystray doesn't have a direct double-click event,
        # but we can simulate it or rely on the menu for show/hide)
        # For simplicity, we'll rely on the menu item for now.
        # A more advanced implementation might involve platform-specific hooks.

    def toggle_window_visibility(self, icon=None, item=None):
        """Toggle window visibility, works with or without system tray."""
        if self.is_window_visible:
            self.hide_window()
        else:
            self.show_window()

    def show_window(self):
        """Show the main application window."""
        if not hasattr(self, 'icon') or self.icon is None:
            # No system tray, just show the window directly
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            self.is_window_visible = True
            return

        # Original logic for when system tray is available
        if self.is_window_visible:
            self.window.withdraw()
            self.is_window_visible = False
            self.window.after(200, self.show_window)
            return
        
        self.window.deiconify()
        self.window.lift()
        self.window.attributes('-topmost', True)
        self.window.focus_force()
        self.window.after(100, lambda: self.window.attributes('-topmost', 0))
        self.is_window_visible = True

    def hide_window(self):
        """Hide the main application window."""
        self.window.withdraw()
        self.is_window_visible = False

    def exit_application(self, icon=None, item=None):
        """Exit the application, works with or without system tray."""
        if hasattr(self, 'icon') and self.icon:
            self.icon.stop()
        self.window.after(0, self.window.destroy)

    def stop_icon(self):
        """Stop the system tray icon if it exists."""
        if hasattr(self, 'icon') and self.icon:
            self.icon.stop()
