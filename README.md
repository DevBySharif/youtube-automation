# 🎙  YouTube Automation — Timestamp Script Analyzer (v1.0.0)

[![Release](https://img.shields.io/badge/Release-v1.0.0-9EFF00?style=for-the-badge&logo=github)](https://github.com/DevBySharif/youtube-automation/releases)
[![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python)](https://python.org)
[![Qt](https://img.shields.io/badge/GUI-PySide6_Qt-green?style=for-the-badge&logo=qt)](https://qt.io)
[![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)](LICENSE)

A standalone desktop application and **Voice & Image Automation Engine** designed for YouTube Automation content creators, video editors, and AI narrators. Converts voiceover scripts into neural audio, word-level timestamps, subtitle files (`SRT`, `VTT`, `ASS`), and AI image planning sequences.

---

## ⚡ Quick Start (3 Steps)

### Step 1: Paste Your Script
Open **Timestamp Script Analyzer**, paste your script into the left editor panel, or drag-and-drop any `.txt` file.

### Step 2: Choose Voice & Narration Profile
Select from **5 AI Voice Providers** (including Kokoro Offline Neural TTS) and **15 AI Narration Profiles** (*Documentary*, *YouTube Explainer*, *Finance*, *Storytelling*, *Motivation*, *Horror*, etc.).

### Step 3: Click `▶ Generate`
The 6-stage pipeline normalizes text, synthesizes neural audio, aligns word timestamps with Whisper, exports subtitles, and plans image timelines automatically!

---

## ✨ Primary Features

### 🎙 1. Offline Neural Voice Engine (Kokoro TTS)
- **82M Parameter Neural Model**: Fast offline text-to-speech with natural human intonation.
- **Bundled eSpeak NG Runtime**: Includes 64-bit portable Windows `libespeak-ng.dll`—requires 0 external system dependencies!
- **15 AI Narration Profiles**: Pre-tuned pitch, stability, energy, and pause controls for every YouTube genre.
- **Custom Pronunciation Dictionary Studio**: Override brand names, acronyms, and specialized terms with custom phonetic mappings.
- **Text Normalization Engine**: Converts numbers (`2026` → `twenty twenty-six`), currencies (`$50` → `fifty dollars`), dates, percentages, and URLs automatically.

### 🖼 2. AI Image Generation Studio & Planner
- **Modular Image Provider Registry**: Architectural plug-in layer supporting **FLUX**, **Stable Diffusion XL**, **OpenAI DALL-E 3**, **Gemini Images**, **Ideogram**, **Recraft**, **ComfyUI**, and **Automatic1111 / Forge**.
- **15 Reusable Visual Prompt Templates**: Pre-configured styles for *YouTube Documentary*, *History*, *Finance*, *Sci-Fi*, *Anime*, *Cyberpunk*, *Wildlife*, etc.
- **Persistent Memory Registries**: Maintain character appearance, location architecture, and object props across video scenes.
- **SHA256 Image Cache**: Automatically skips duplicate image generations.

### 📜 3. Subtitle & Video Automation Exporter
- Exports synchronized **`SRT`**, **`VTT`**, and **`ASS`** subtitle files automatically.
- Generates **`Master Video Automation JSON`** containing word timing curves, scene markers, keyword entities, silence maps, and camera direction plans.

---

## 🖥 System Requirements

| Component | Minimum Requirement | Recommended |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 (64-bit) | Windows 11 (64-bit) |
| **Processor** | Intel Core i5 / AMD Ryzen 5 | Intel Core i7 / AMD Ryzen 7 |
| **RAM** | 8 GB | 16 GB |
| **Graphics** | Integrated Graphics | Dedicated NVIDIA / AMD GPU |
| **Disk Space** | 2.5 GB free space | 5 GB SSD storage |

---

## 🛠 Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/DevBySharif/youtube-automation.git
cd youtube-automation

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Run application
python src/main.py
```

---

## 📌 Known Limitations

- **Cloud Image Providers**: FLUX, SDXL, OpenAI DALL-E, and ComfyUI image backends are currently exposed as architectural plug-in stubs in v1.0.0 and will receive full API integration in v1.1.
- **GPU Acceleration**: Faster-Whisper alignment defaults to CPU mode on systems without CUDA installed.

---

## 🗺 v1.1 Development Roadmap

- 🌐 **OpenRouter & OmniRouter Integration**: Support cloud TTS models via API.
- 🎨 **ComfyUI Local Workflow Execution**: Direct local execution of ComfyUI nodes for image keyframes.
- 🎙 **XTTS v2 & Fine-Tuned Voice Cloning**: Local zero-shot voice cloning engine.
- 🎬 **FFmpeg Automated Video Assembly**: One-click video rendering combining audio, subtitles, and image timelines.

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
