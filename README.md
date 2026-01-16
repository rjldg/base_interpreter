# 🗣️ Speech Interpreter

A beginner-friendly language interpreter powered by Azure Speech SDK! This project captures audio in one language, translates it, and speaks it back in another language—all in real-time.

**Perfect for:** Learning real-time speech processing, building multilingual applications, or just having fun with language translation! 🌍

---

## 📋 Table of Contents

- [How It Works](#-how-it-works)
- [What You'll Need](#-what-youll-need)
- [Quick Start Guide](#-quick-start-guide)
- [Usage Examples](#-usage-examples)
- [Troubleshooting](#-troubleshooting)
- [Learn More](#-learn-more)

---

## 🎯 How It Works

Here's the magic behind your Speech Interpreter:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPEECH INTERPRETER FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🎤 Microphone          Your voice in any language              │
│    ▼                                                              │
│  📝 Speech-to-Text      Converts audio to written text          │
│    ▼                                                              │
│  🌐 Translation         Translates text to target language       │
│    ▼                                                              │
│  🔊 Text-to-Speech      Converts translated text back to voice  │
│    ▼                                                              │
│  🎧 Speaker             Hear your message in a new language!    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Step by step:**
1. 🎤 **Capture** - Speak into your microphone
2. 📝 **Recognize** - The app converts your speech to text
3. 🌐 **Translate** - Your text is translated to the target language
4. 🔊 **Synthesize** - The translation is converted back to speech
5. 🎧 **Listen** - Enjoy your translated message!

---

## 🛠️ What You'll Need

### Prerequisites

Before you start, make sure you have:

- ✅ **Python** (version 3.7 or newer)
  - [Download Python](https://www.python.org/downloads/)
  - On Windows, check "Add Python to PATH" during installation

- ✅ **An Azure Account** (free tier is fine!)
  - [Create a free Azure account](https://azure.microsoft.com/en-us/free/)

- ✅ **Azure Speech Service**
  - This is the service that powers the speech recognition, translation, and text-to-speech
  - [Create a Speech Service resource in Azure](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices)

- ✅ **Your Speech Service Credentials**
  - You'll need:
    - **Subscription Key** (found in Azure Portal)
    - **Region** (e.g., `eastus`, `westus2`, `uksouth`)

### Getting Your Azure Credentials

1. Go to [Azure Portal](https://portal.azure.com/)
2. Find your Speech Service resource
3. In the left menu, click **Keys and Endpoint**
4. Copy your **Key 1** (subscription key) and **Region** (location)
5. Keep these safe! You'll need them in the next step

---

## 🚀 Quick Start Guide

### Step 1: Install Required Python Packages

Open your terminal (Command Prompt or PowerShell on Windows) and run:

```bash
pip install azure-cognitiveservices-speech
```

This downloads the Azure Speech SDK for Python.

### Step 2: Set Up Your Credentials

Create a file in your project folder called `.env` (or edit `interpreter.py` directly).

**Option A: Using a `.env` file (recommended)**
```
SPEECH_KEY=your_subscription_key_here
SPEECH_REGION=your_region_here
```

**Option B: Directly in Python**
Add these lines near the top of `interpreter.py`:
```python
SPEECH_KEY = "your_subscription_key_here"
SPEECH_REGION = "your_region_here"
```

### Step 3: Run the Interpreter

```bash
python interpreter.py
```

That's it! 🎉 Speak into your microphone and watch the magic happen!

---

## 💡 Usage Examples

### Example 1: Translate English to Spanish

```python
from interpreter import SpeechInterpreter

# Create an interpreter instance
interpreter = SpeechInterpreter(
    source_language="en-US",      # Listen for English (US)
    target_language="es-ES",      # Translate to Spanish (Spain)
    output_voice="es-ES-AlonsoMultilingualNeural"
)

# Speak into your microphone!
result = interpreter.interpret()
print(f"You said: {result['original_text']}")
print(f"Translation: {result['translated_text']}")
```

### Example 2: Multi-Language Journey

```python
# Start in French, end in German
interpreter = SpeechInterpreter(
    source_language="fr-FR",
    target_language="de-DE",
    output_voice="de-DE-KlausNeural"
)

interpreter.interpret()
```

### Example 3: Customize Everything

```python
interpreter = SpeechInterpreter(
    source_language="ja-JP",       # Japanese input
    target_language="pt-BR",       # Portuguese (Brazil)
    output_voice="pt-BR-ThalitaNeural",
    speech_recognition_language="ja-JP",
    timeout_seconds=10
)

result = interpreter.interpret()
```

---

## 🐛 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'azure'"

**Solution:** You need to install the Azure SDK. Run:
```bash
pip install azure-cognitiveservices-speech
```

### ❌ "Invalid subscription key or wrong API endpoint"

**Solution:** Your credentials might be wrong. Check:
1. Are you using the correct **Subscription Key**? (Copy-paste, don't type manually)
2. Is the **Region** spelled correctly? (e.g., `eastus`, not `East US`)
3. Is your Azure subscription still active?

### ❌ "No microphone detected" or "No audio input"

**Solution:**
1. Make sure your microphone is plugged in and turned on
2. Check your system volume isn't muted
3. Try: `Run audio troubleshooter` (Windows) or `System Preferences > Sound` (Mac)
4. Test your microphone with another app (Voice Memos, Discord, etc.)

### ❌ "I said something but nothing happened"

**Solution:**
1. Check your microphone is not muted
2. Speak clearly and a bit louder than normal
3. The app waits about 5 seconds of silence, then processes
4. Try increasing the `timeout_seconds` parameter

### ❌ "Translation is not working"

**Solution:**
1. Make sure you've selected a valid language pair (e.g., `en-US` → `es-ES`)
2. Some language combinations might not be supported
3. Check [supported languages here](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)

### ❌ "No audio output / Can't hear the translation"

**Solution:**
1. Check your speakers are plugged in and volume is up
2. Test speakers with another app (YouTube, music, etc.)
3. Check Windows volume mixer (might have silenced the app)
4. Make sure the voice name is valid for your target language

---

## 📚 Learn More

### Official Azure Documentation

- 🎤 [Speech-to-Text Docs](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-to-text)
- 🗣️ [Text-to-Speech Docs](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech)
- 🌐 [Translation Service Docs](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-translation)
- 🌍 [Supported Languages](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)

### Python SDK Reference

- 📖 [Azure Speech SDK for Python](https://learn.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/)
- 💻 [Quickstart Guide](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/quickstarts/speech-to-text-from-microphone)

### Popular Languages & Locales

**Need help picking a language code?** Here are common ones:

| Language | Code | Voice Example |
|----------|------|---|
| English (US) | `en-US` | `en-US-AriaNeural` |
| Spanish (Spain) | `es-ES` | `es-ES-AlonsoNeural` |
| French (France) | `fr-FR` | `fr-FR-DeniseNeural` |
| German | `de-DE` | `de-DE-KlausNeural` |
| Japanese | `ja-JP` | `ja-JP-NanamiNeural` |
| Portuguese (Brazil) | `pt-BR` | `pt-BR-ThalitaNeural` |
| Mandarin Chinese | `zh-CN` | `zh-CN-XiaoxiaoNeural` |

---

## 🎓 Next Steps

1. ✅ Get your Azure credentials set up
2. ✅ Run the quick start
3. ✅ Try different language pairs
4. ✅ Customize voices and settings
5. ✅ Build something cool! 🚀

---

## ❓ Have Questions?

- 📖 Read the [Azure Speech Service FAQ](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/faq-speech-services)
- 💬 Check out [GitHub Discussions](https://github.com/Azure/cognitive-services-speech-sdk-js/discussions)
- 🆘 [Azure Support](https://azure.microsoft.com/en-us/support/)

---

**Happy translating! 🌍✨**
