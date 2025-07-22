# pylint: disable=broad-except

import sys

# Attempt to import klembord, which is needed for Windows HTML clipboard support
try:
    import klembord
except ImportError:
    klembord = None
    # print("Warning: klembord library not found. HTML clipboard copying may not work on Windows.")

class ClipboardManager:
    """Manages clipboard operations, including formatted text."""

    def __init__(self):
        """Initializes the ClipboardManager."""
        pass # Currently no specific initialization needed

    def _copy_html_windows(self, text_content, html_content):
        """Copies HTML content to the clipboard on Windows using klembord."""
        if klembord is None:
            print("Error: klembord library is not available. Cannot copy HTML on Windows.")
            return False
        try:
            # klembord expects a dictionary with 'text' and 'html' keys
            klembord.set_with_rich_text(
                text = text_content, # Provide a plain text fallback
                html = html_content
            )
            print("HTML content copied to clipboard (Windows).")
            return True
        except Exception as e:
            print(f"Error copying HTML to clipboard on Windows: {e}")
            return False

    def copy_html_with_formatting(self, text_content, html_content):
        """
        Copies HTML content to the clipboard based on the operating system.

        Args:
            html_content: The HTML content to copy.

        Returns:
            True if copying was successful, False otherwise.
        """
        if not html_content:
            print("No HTML content provided to copy.")
            return False

        if sys.platform == 'win32':
            return self._copy_html_windows(text_content, html_content)
        elif sys.platform == 'darwin':
            # TODO: Implement macOS support using richxerox or similar
            print("Copy with formatting not yet implemented for macOS.")
            return False
        elif sys.platform.startswith('linux'):
            # TODO: Implement Linux support (klembord might work, or other methods)
            return self._copy_html_windows(text_content, html_content)
            # print("Copy with formatting not yet implemented for Linux.")
            # return False
        else:
            print(f"Unsupported operating system for formatted copy: {sys.platform}")
            return False
