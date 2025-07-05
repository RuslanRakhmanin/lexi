# **Lexi Project Specification: Gemini-Powered Text Assistant**

This document is an enhanced version of the original specification, incorporating feedback to provide a more robust and developer-ready blueprint.

## **1. Project Vision**

To create a lightweight and responsive desktop utility that leverages the Google Gemini API for advanced text processing. The application will be instantly accessible via a global hotkey, providing users with quick translation, proofreading, and custom text manipulation, seamlessly integrated into their workflow.

---

## **2. Core Functional Requirements**

### **2.1. System Integration & Accessibility**

* **System Tray Operation:**
  * The application must run primarily in the background, represented by an icon in the system tray (or menu bar on macOS).
  * **Context Menu:** A right-click on the tray icon will display a menu with: `Show/Hide Window` and `Exit`.
  * **Double-Click:** A double-click on the tray icon will show the main application window and bring it to the foreground.

* **Global Hotkey Activation:**
  * The application must listen globally for the hotkey combination **Ctrl+C, Ctrl+C**.
  * The detection logic should register two presses of `Ctrl+C` within a **400ms time window**.
  * The activation sequence must be deterministic to avoid race conditions:

    1. Upon successful detection, the application will programmatically **simulate a single `Ctrl+C` keypress** to ensure the currently highlighted text is copied to the system clipboard.
    2. A brief, fixed delay (e.g., 100ms) must be introduced to allow the OS to complete the copy operation.
    3. The application will then read the content from the clipboard.
    4. The main window will be displayed and brought into focus.
    5. The input widget will be populated with the captured text.
    6. The analysis to select the appropriate processing options ("word" vs. "phrase") will be triggered automatically.

  * **Edge Case Handling:**:
    * If the clipboard is empty after the copy action, the application window must **not** be displayed. The hotkey trigger will be ignored silently.
    * If the clipboard content is not text-based (e.g., an image file), the trigger will also be ignored silently.

* **First-Run & API Key Management:**
  * On the first launch (or if the API key is missing from `settings.json`), the application will show the main window.
  * In this state, a welcome message and a dedicated input field for the Gemini API key will be displayed. All other widgets (e.g., input/output areas, processing options) must be disabled.
  * Once a user enters a key and confirms, it must be saved to `settings.json`, and the UI will unlock into its fully functional state.

### **2.2. User Interface (UI)**

The main window shall be composed of the following vertically arranged widgets:

1. **Language Selectors:** `Label("From:")`, `Dropdown(Source Language)`, `Label("To:")`, `Dropdown(Target Language)`. Defaults: Source = "English", Target = "Russian".
2. **Input Widget:** A multiline text area for user input.
3. **Processing Options:**
   * A horizontal row of buttons or tabs, dynamically displayed based on the input.
   * **Detection Rule:** The input is a **"word"** if `len(text.strip().split()) == 1`. Otherwise, it is a **"phrase"**. This correctly handles single words with leading/trailing whitespace or attached punctuation.
4. **Custom Prompt Input:** A single-line text entry field, visible **only** when the "Custom Prompt" option is selected.
5. **Output Widget:**
   * A read-only, multiline text area for Gemini API results.
   * **Crucially, this widget must render basic Markdown:** It needs to correctly display bold text (e.g., `**text**`) and strikethrough text (e.g., `~~text~~`).
6. **Action Buttons:**
    * `Copy`: Copies the raw text content (including Markdown characters) from the output widget to the clipboard.
      * *Example Clipboard Content:* `This is **bold** and this is ~~strikethrough~~.`
    * `Copy with Formatting`: Copies the output as rich text, preserving the visual formatting for pasting into other applications.
      * *Example Clipboard Content (HTML):* `This is <b>bold</b> and this is <s>strikethrough</s>.`

### **2.2.1. UI State Management**

The UI must provide clear feedback to the user during API interactions.

* **Idle State:** The application is ready for input. All widgets are active.
* **Loading State:** When an API request is sent, the `Input Widget` and `Action Buttons` must be disabled. The `Output Widget` should display a clear status message (e.g., "Thinking...").
* **Error State**: If an API call fails, the `Output Widget` must display a user-friendly and specific error message. The error text should be visually distinct (e.g., coloured red). Examples include:
"Error: Invalid API Key. Please verify your key and try again."
"Error: API quota exceeded. Please try again later."
"Error: Network connection failed. Please check your internet connection."
"Error: The request was blocked by the API's safety filter."

### **2.3. Text Processing & Gemini Integration**

* All text processing will be done by sending prompts to the Google Gemini API.
* The application must use the definitions in `prompts.json` to build the final prompt sent to the API.
* Placeholders (`{text}`, `{from_language}`, etc.) must be replaced before sending.
* API requests must be **asynchronous** to keep the UI responsive.

---

## **3. Configuration & State Persistence**

### **3.1. `prompts.json` - Prompt Definitions**

* The application must load its text processing capabilities from an external `prompts.json` file. This file defines UI labels, the input type they apply to ("word" or "phrase"), and the Gemini prompt template.
* **Example `prompts.json` structure:**

    ```json
    {
      "word": [
        {
          "label": "Full Analysis",
          "prompt": "Provide a comprehensive analysis for the word '{text}' in {from_language}. Include its definition, synonyms, antonyms, and three example sentences.",
          "default": false
        },
        {
          "label": "Translate",
          "prompt": "Translate the word '{text}' from {from_language} to {to_language}.",
          "default": true
        },
        {
            "label": "Custom Prompt",
            "prompt": "{custom_prompt}. The text to process is: '{text}'",
            "default": false
        }

      ],
      "phrase": [
        {
          "label": "Proofread",
          "prompt": "Proofread and correct the following text, keeping the original meaning. Explain the corrections. The original text is in {from_language}. Use Markdown for your corrections: **new text** for additions and ~~old text~~ for deletions. Original text: '{text}'",
          "default": false
        },
        {
          "label": "Translate",
          "prompt": "Translate the following text from {from_language} to {to_language}. Text: '{text}'",
          "default": true
        },
        {
            "label": "Custom Prompt",
            "prompt": "{custom_prompt}. The text to process is: '{text}'",
            "default": false
        }

      ]
    }
    ```

### **3.2. `settings.json` - User Preferences**

* The application must save user preferences to `settings.json` upon closing and load them on startup.
* The following settings must be persisted:
  * User's Gemini API key.
  * Last selected source language.
  * Last selected target language.
  * Last used processing option (e.g., "Full Analysis", "Translate").
  * `window_geometry` (the main window's last known size and position).

### 3.3. Configuration File Integrity

* The application must handle potential issues with its configuration files gracefully.
* If `prompts.json` is missing, contains invalid JSON, or is otherwise unparseable on startup, the application must display a clear, user-friendly error message detailing the problem and then use default values given in the 3.1 section.
* If `settings.json` is missing, contains invalid JSON, or is otherwise unparseable on startup, the application must display a clear, user-friendly error message detailing the problem and use default values given in the 3.1 section.

---

## **4. Technology Stack & Implementation Notes**

* **Language:** Python 3.x
* **GUI Framework:** `tkinter` and `tkinter.ttk`.
* **System Tray:** **`pystray`** library.
* **Global Hotkey:** **`pynput`** library.
* **API Interaction:** **`google-generativeai`** library.
* **Markdown Rendering:** This must be implemented by converting Markdown to HTML (via the **`markdown`** library) and displaying it in an embedded browser frame (via the **`tkinterweb`** library). Custom CSS should be used for styling.
* **Rich Text Clipboard Handling:** This is a platform-dependent task. A fallback mechanism is required.
  * Implementation may require libraries like `win32clipboard` (Windows) or `pyobjc` (macOS).
  * **Fallback:** If rich text copy is not implemented for the user's platform or fails, the `Copy with Formatting` button must perform the same action as the standard `Copy` button.
* The code should be broken into multiple modules and well-organized. The main application logic should be in a single file, while other modules should be named accordingly.
* The project files should be organised in folders for better organization and maintainability.

---

## **5. Future Enhancements (Optional - Post-MVP)**

* Allow user customization of the global hotkey combination.
* Implement a full settings window for managing the API key, hotkey, and other preferences.
* Add a "History" feature to view and reuse recent requests.
* Build a user-friendly editor for managing the prompts in `prompts.json`.
* Live API Key Validation: On first run, after the user enters their API key, the application should make a test call to the API to validate the key before saving it and unlocking the UI.
* Streaming API Responses: For longer-running requests, implement streaming to display the Gemini API's response word-by-word as it's generated, greatly improving perceived responsiveness.
* Re-evaluating the Markdown Renderer:
    **Concern**: The `tkinterweb` library is a heavy dependency as it essentially embeds a full web browser engine into a `tkinter` app. This conflicts with the "lightweight" project vision.
    **Recommendation**: For the specified requirements (bold and strikethrough), a native `tkinter.Text` widget is perfectly capable and vastly more lightweight. You can achieve this using the widget's built-in `tag_config()` method. However, it cannot use custom CSS and render tables.
    **Example**: Create a "bold" tag with `font=('Helvetica', '10', 'bold')` and a "strikethrough" tag with `overstrike=True`. Then, parse the Markdown from the API response and apply these tags to the relevant text ranges. This eliminates a heavy dependency and keeps the application snappy.
    