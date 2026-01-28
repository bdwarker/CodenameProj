# CodenameProj - Cyra

> *"Cyra at your service."*

An intelligent, voice-enabled AI assistant built with local LLMs, designed to be your personal companion for productivity, automation, and beyond. Now featuring a modern GUI and powerful file system capabilities.

## 🌟 Overview

CodenameProj (Cyra) is a modular AI assistant system that combines voice interaction, computer vision, and intelligent action execution. Built with privacy in mind, it runs entirely on local models with no reliance on cloud services (except optional ElevenLabs TTS).

### Key Features

- 🎨 **Modern GUI**: Sleek, dark-themed interface built with CustomTkinter.
- 🎤 **Async Voice Interaction**: Continuous, non-blocking speech recognition using Faster Whisper.
- 🛑 **Interruptible Output**: Stop the assistant mid-sentence or mid-action instantly.
- 📂 **File System Control**: Read, write, list, and delete files directly through voice commands.
- ✍️ **Content Generation**: Ask Cyra to write code, poems, or emails, and she'll generate the content and save it to a file.
- 🧠 **Dual AI Models**: Separate models for fast JSON parsing (Gemma 3:4b) and natural conversations (Llama 3.1).
- 👁️ **Screen Vision**: OCR-powered screen reading with docTR for visual assistance.
- 💾 **Smart Memory**: Persistent memory system for context-aware conversations.
- 🎯 **Action System**: Execute browser actions, launch apps, web searches, and more.
- 🔊 **Multiple TTS Options**: Local TTS and ElevenLabs integration.

## 🏗️ Architecture

```
CodenameProj/
├── actions/              # Action handlers and brain logic
│   ├── actions.py        # Core action implementations (File system, Browser, etc.)
│   ├── actions.txt       # Action definitions for AI
│   ├── brain.py          # Ollama model interactions & Content Generation
│   ├── image.py          # Screen capture & OCR
│   └── launchApp.py      # Application launcher
├── database/             # Persistent storage
│   └── memory.json       # Long-term memory
├── utils/                # Utility modules
│   ├── config_manager.py # Configuration management
│   ├── elevenlabsAPI.py  # ElevenLabs TTS integration
│   ├── log.py            # Logging utilities
│   ├── memory.py         # Memory management
│   ├── speechRecog.py    # Async Speech recognition
│   └── tts.py            # Interruptible Local TTS
├── images/               # Screenshot storage (debug mode)
├── outputs/              # OCR text outputs
├── logs/                 # Application logs
├── config.json           # Configuration settings
├── gui.py                # Main Modern GUI Application
├── main.py               # CLI Application (Legacy)
└── requirements.txt      # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Ollama models: `gemma3:4b` and `llama3.1`

### Installation

1. Clone the repository
```bash
git clone <your-repo-url>
cd CodenameProj
```

2. Create and activate virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies
```bash
pip install -r requirements.txt
pip install mss python-doctr customtkinter  # Additional requirements
```

4. Set up environment variables
Create a `.env` file:
```env
OLLAMA_PROMPT="Your system prompt here"
JSON_MODEL=gemma3:4b
CONVERSATION_MODEL=llama3.1
ELEVENLABS_API_KEY=your_key_here  # Optional
```

5. Configure settings
Edit `config.json` or use the **Settings** tab in the GUI.

6. Pull required Ollama models
```bash
ollama pull gemma3:4b
ollama pull llama3.1
```

### Running Cyra

Launch the modern GUI:
```bash
python gui.py
```

## 💬 Usage

### Voice & Chat
- **Talk**: Use the microphone button or enable "Voice Mode" to talk naturally.
- **Chat**: Type messages in the chat input field.
- **Interrupt**: Press the "Stop / Interrupt" button to halt speaking or listening immediately.

### File System Actions
- **Write File**: "Write a python script to `C:/Users/Name/Documents/script.py`" (Cyra will generate the code).
- **Read File**: "Read `C:/Users/Name/Documents/note.txt`".
- **List Directory**: "What files are in `C:/Users/Name/Documents`?".
- **Delete File**: "Delete `C:/Users/Name/Documents/old.txt`".

### Other Actions
- **Open Browser**: "Open my browser" or "Launch Firefox".
- **Search**: "Search for machine learning algorithms".
- **Launch Apps**: "Open Spotify" or "Launch VS Code".
- **See Screen**: "Look at my screen" or "What's on my monitor?".
- **Remember**: "Remember that my favorite color is blue".

## 🔧 Configuration

Use the **Settings** tab in the GUI to change:
- **Assistant Name**: Customize how Cyra refers to herself.
- **Ollama Model**: Switch between available local models.
- **Conversation Model**: Choose the model for chat responses.

## 🛠️ Future Development

- [ ] Client-server architecture for distributed deployment
- [ ] Raspberry Pi integration for smart home control
- [ ] Wake word detection for hands-free operation
- [ ] WebSocket support for real-time communication
- [ ] Advanced context-aware memory with vector embeddings
- [ ] Voice cloning for personalized TTS

## 📋 Requirements

Core dependencies:
```
customtkinter
faster-whisper
sounddevice
numpy
python-dotenv
ollama
elevenlabs
pyautogui
TTS
pandas
mss
python-doctr
```

---

**Note**: This project is under active development. Features and architecture may change as it evolves toward the ultimate goal: a distributed, voice-activated AI assistant system running across multiple devices.