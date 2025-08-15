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
* **Configurable Settings**: Adjust LLM model, API key, language preferences, and more through the [`config/settings.json`](config/settings.json:1) file.
* **Lightweight**: Built with Python and `tkinter` for a minimal memory footprint and responsive feel.

## 🚀 How It Works

1. **Highlight** any text in any application.
2. **Press `Ctrl+C` twice** in quick succession.
3. The Lexi window appears with your text pre-loaded.
4. Choose your desired action (e.g., "Translate").
5. Get an instant, AI-generated response.

## ⚙️ Configuration

Lexi can be customized through configuration files in the `config/` directory:

### Settings Configuration ([`config/settings.json`](config/settings.json:1))

Configure core application settings including:

* **LLM Model**: Change the AI model (e.g., "gemini-2.5-flash-lite")
* **API Key**: Set your Google Gemini API key for authentication
* **Language Preferences**: Define source and target languages for translation
* **Window Settings**: Adjust window geometry and positioning
* **Default Processing**: Set the default text processing option

### Custom Prompts ([`config/prompts.json`](config/prompts.json:1))

Create custom text processing actions by defining your own prompts and commands.

## 🔑 Getting Your Free Gemini API Key

See [docs/get_api_key.md](docs/get_api_key.md) for detailed instructions on obtaining your free Google Gemini API key.

## 🛠️ Tech Stack

* **Language**: Python 3
* **AI Engine**: Google Gemini API via [`python-genai`](https://github.com/googleapis/python-genai)
* **GUI**: [`tkinter`](https://docs.python.org/3/library/tkinter.html)
* **System Integration**: [`pystray`](https://pystray.readthedocs.io/) for system tray functionality and [`pynput`](https://pynput.readthedocs.io/) for global hotkey listening.
