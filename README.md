# Lexi: Your Instant, LLM-Powered Text Assistant

The Lexi Project is a lightweight, responsive desktop utility designed to seamlessly integrate advanced text processing into your daily workflow. Leveraging the power of LLM (the Google Gemini API is available at the moment), Lexi provides instant translation, proofreading, and custom text manipulation, all accessible via a convenient global hotkey.

---

## ✨ Key Features

* **Instant Activation**: Summon Lexi by highlighting text and pressing `Ctrl+C` twice. It's fast, seamless, and designed to keep you in the flow.
* **Powerful Text Tools**:
  * 🌐 **Translate**: Instantly translate words or phrases.
  * ✍️ **Proofread**: Correct grammar and spelling with AI-powered suggestions.
  * 📚 **Full Analysis**: Get a deep-dive into any word, including definitions, synonyms, and example sentences.
* **Seamless Integration**: Runs quietly in your system tray, staying out of your way until you need it.
* **Fully Customizable**: Define your own prompts and actions via a simple [`config/prompts.json`](config/prompts.json:1) file to tailor Lexi to your exact needs.
* **Lightweight**: Built with Python and `tkinter` for a minimal memory footprint and responsive feel.

## 🚀 How It Works

1. **Highlight** any text in any application.
2. **Press `Ctrl+C` twice** in quick succession.
3. The Lexi window appears with your text pre-loaded.
4. Choose your desired action (e.g., "Translate").
5. Get an instant, AI-generated response.

## 🛠️ Tech Stack

* **Language**: Python 3
* **AI Engine**: Google Gemini API via [`google-generativeai`](https://pypi.org/project/google-generativeai/)
* **GUI**: [`tkinter`](https://docs.python.org/3/library/tkinter.html)
* **System Integration**: [`pystray`](https://pystray.readthedocs.io/) for system tray functionality and [`pynput`](https://pynput.readthedocs.io/) for global hotkey listening.
