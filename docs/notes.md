# Notes

## left mouse click on the tray icon with pystray

To handle a left mouse click on the system tray icon using the pystray library on Windows, you should use a menu and specify a **default action**. The default menu item will be triggered on a left-click.

```python
menu = pystray.Menu(
    item('Default Action', on_left_click, default=True)
)
icon = pystray.Icon("test", image, "Tooltip", menu=menu)
```

## How to get selected text from tkinterweb.HtmlFrame?

HtmlFrame does not directly expose a method to get the currently selected (highlighted) text.
However, Ctrl+C works wor selected text to be copied to the clipboard.

## If the window is visible on background it jumps on top but doesn't get focus

The "Why" - Focus Stealing Prevention
Modern operating systems (especially Windows) have rules to prevent applications from "stealing focus." If you are actively typing in a web browser or a document, it would be incredibly disruptive and a security risk if another background application could suddenly pop up and start receiving your keystrokes.

Maybe this is the reason why the Reverso app uses another small window to pop up on Ctrl+C double click.

## Building the project into a single executable

Debug build with a console
```bash
pyinstaller --onefile --console --icon "src\icons\Feather1.ico" --add-data="src/icons/Feather1.ico;icons" --name "Lexi_debug"  src\app.py
```
I have to add `import markdown_del_ins` call explicitly into markdown_renderer.py. Otherwise the pyinstaller ignored it even with `--hidden-import markdown_del_ins` and `--collect-submodules "markdown"`