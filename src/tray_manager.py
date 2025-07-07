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

        image = Image.open("config/Feather1.ico")

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
            self.hide_window()
        else:
            self.show_window()

    def show_window(self):
        """Show the main application window."""

        # TODO: The window doesn't get focus in case it was visible on the background.
        # The trick with withdrawing and deiconifying the window does not work as expected.

        if self.is_window_visible:
            self.window.withdraw()  # Temporarily hide the window.
            self.is_window_visible = False
            self.window.after(200, self.show_window)  # Delay to ensure the window is hidden before showing it again.
            return
        
        self.window.deiconify() # Show the window
        self.window.lift() # Bring window to front
        self.window.attributes('-topmost', True) # Bring window to front and give focus
        self.window.focus_force() # Explicitly request focus

        # self.window.attributes('-topmost', False) # Revert topmost attribute
        # Schedule the reversion of topmost after a short delay (e.g., 100ms)
        # This gives the window manager time to handle the focus before the state changes.
        self.window.after(100, lambda: self.window.attributes('-topmost', 0))
        
        self.is_window_visible = True

    def hide_window(self):
        """Hide the main application window."""
        self.window.withdraw() # Hide the window
        self.is_window_visible = False

    def exit_application(self, icon, item):
        icon.stop()
        self.window.quit() # Exit the tkinter application

    def stop_icon(self):
        if self.icon:
            self.icon.stop()
