# Getting Your Free Gemini API Key

Lexi uses Google's Gemini API for AI-powered text processing. Here's how to get your free API key:

## Step-by-Step Guide

1. **Visit Google AI Studio**: Go to [https://aistudio.google.com](https://aistudio.google.com)
2. **Sign in** with your Google account
3. **Click "Get API Key"** in the left sidebar
4. **Create a new project** or select an existing one
5. **Generate your API key** - it's completely free with generous usage limits
6. **Copy the key** and add it to your [`config/settings.json`](config/settings.json:1) file

## Free Usage Limits
- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per day**
- Perfect for personal use and testing

## 🔐 API Key Safety & Best Practices

> ⚠️ **Important Security Notice**: Your API key is like a password - keep it secure!

### Key Safety Recommendations

1. **One Key Per Purpose**: Create separate API keys for different applications
   - Use one key specifically for Lexi
   - Don't reuse keys across different projects

2. **Never Share Your Key**:
   - Don't post it on GitHub, forums, or social media
   - Don't include it in screenshots or code snippets
   - Don't share it with others, even friends

3. **Secure Storage**:
   - Store it in your [`config/settings.json`](config/settings.json:1) file
   - Add `config/settings.json` to your [`.gitignore`](.gitignore:1) to prevent accidental commits
   - Never hardcode it directly in source files

4. **Monitor Usage**: Regularly check your usage in [Google AI Studio](https://aistudio.google.com) to detect any unauthorized use

5. **Rotate Keys**: If you suspect your key has been compromised, generate a new one immediately and update your configuration

### Quick Security Checklist
- [ ] API key stored in `config/settings.json`
- [ ] `config/settings.json` added to `.gitignore`
- [ ] Key not shared with anyone
- [ ] Separate key created for Lexi only