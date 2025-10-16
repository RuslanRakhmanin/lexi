# The app TODO list

## Features

- [ ] Add Ollama as possible LLM provider
- [x] Make the app work on Linux
- [ ] Make the app work on MacOS

## Interface

- [ ] add a separator between the input and output frames so it makes possible to change the input widget size without changing the window size
- [ ] Read available languages from Genimi API and use them to fill the language combo boxes

## Markdown rendering

- [x] Add support for ~~strikethrough~~
- [x] Add support for ==highlight==

## System tray

- [ ] Handle double-click (pystray doesn't have a direct double-click event, but we can simulate it or rely on the menu for show/hide)

## Settings

- [ ] Read available model names from Genimi API and use a current flash light model

## Bugfixes

- [ ] When the window popups after double Ctrl+C, the previous mode is ignored and default translate mode is used.
- [ ] After some time, the output widget stops coping text to the clipboard by Ctrl+C.