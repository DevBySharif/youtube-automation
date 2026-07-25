# YouTube Automation — Timestamp Script Analyzer

A professional, self-contained desktop application and voice engine for YouTube Automation. Converts voiceover scripts into synthesized audio, word-level timestamps, alignment data, and structured scene concepts.

## 🚀 Features

- **Portable eSpeak NG Runtime**: Bundled 64-bit Windows eSpeak NG runtime for 100% offline, plug-and-play operation.
- **Kokoro TTS Engine**: High-quality 82M parameter neural voice synthesis.
- **12 AI Narration Modes**: Customized profiles for Documentary, YouTube Explainer, Finance, Psychology, Horror, Motivation, News, Gaming, Educational, Cinematic, and Funny content.
- **Faster-Whisper Alignment**: Word-level timestamp alignment.
- **Voice Library & Voice Cloning Studio**: Browse voice options and upload reference audio for custom voice cloning architecture.
- **Rich Metadata Export**: Exports word-level timing, emotion, and emphasis data for automated video rendering pipelines (Image Prompts, Subtitles, Scene Detectors).
- **Lime Green Dark Theme**: Modern UI built with PySide6.

## 🛠 Tech Stack

- **GUI**: PySide6 (Qt for Python)
- **Speech Synthesis**: Kokoro TTS (via `misaki` & `phonemizer`)
- **Phonemizer Backend**: Portable eSpeak NG
- **Audio Alignment**: Faster-Whisper
- **Packaging**: PyInstaller + Inno Setup

## 📦 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/DevBySharif/youtube-automation.git
   cd youtube-automation
   ```

2. **Create & Activate Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**:
   ```bash
   python src/main.py
   ```

## 📄 License

MIT License
