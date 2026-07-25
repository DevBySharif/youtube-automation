"""
app.py
Flask server for Timestamp Script Analyzer.

Endpoints:
    GET  /                      Serve the frontend
    GET  /api/voices            Return available voices list
    POST /api/generate          Run full pipeline: TTS → Whisper → Grouper → Timestamp Script
    GET  /api/audio/<filename>  Stream a generated WAV file

Pipeline (POST /api/generate):
    1. Receive: { script, voice, speed }
    2. Kokoro TTS  → voice.wav         (tts_engine.py)
    3. Whisper     → word timestamps   (aligner.py)
    4. Grouper     → timestamp script  (concept_grouper.py)
    5. Return:     { timestamp_script, audio_url }
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

from tts_engine import generate_audio, AVAILABLE_VOICES
from aligner import get_word_timestamps
from concept_grouper import group_into_scenes

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # Allow browser requests from same origin

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Serve the single-page frontend."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/voices")
def get_voices():
    """Return the list of available Kokoro voices."""
    return jsonify({"voices": AVAILABLE_VOICES})


@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Full pipeline endpoint.

    Request JSON:
        {
            "script": "Plain voiceover script text...",
            "voice":  "af_bella",
            "speed":  1.0
        }

    Response JSON (success):
        {
            "status": "ok",
            "timestamp_script": "[00:00]\nThere is a stranger...\n\n[00:04]\nSomeone you saw once.",
            "audio_url": "/api/audio/voiceover.wav"
        }

    Response JSON (error):
        {
            "status": "error",
            "stage":   "tts" | "whisper" | "grouper",
            "message": "Human-readable error description"
        }
    """
    data = request.get_json(force=True, silent=True) or {}

    script = (data.get("script") or "").strip()
    voice  = data.get("voice", "af_bella")
    speed  = float(data.get("speed", 1.0))

    # Basic validation
    if not script:
        return jsonify({"status": "error", "stage": "input", "message": "Script is empty."}), 400

    speed = max(0.5, min(2.0, speed))  # clamp to safe range

    # -------------------------------------------------------------------
    # Stage 1: Kokoro TTS → voice.wav
    # -------------------------------------------------------------------
    log.info("Stage 1/3 — Generating audio with Kokoro TTS (voice=%s, speed=%.1f)", voice, speed)
    try:
        audio_path = generate_audio(
            script=script,
            voice=voice,
            speed=speed,
            output_dir=OUTPUT_DIR,
        )
        log.info("Audio saved to: %s", audio_path)
    except (ValueError, RuntimeError) as e:
        log.error("TTS failed: %s", e)
        return jsonify({"status": "error", "stage": "tts", "message": str(e)}), 500

    # -------------------------------------------------------------------
    # Stage 2: Faster-Whisper → word-level timestamps
    # -------------------------------------------------------------------
    log.info("Stage 2/3 — Aligning audio with Faster-Whisper...")
    try:
        words = get_word_timestamps(audio_path)
        log.info("Whisper returned %d words", len(words))
    except (FileNotFoundError, RuntimeError) as e:
        log.error("Whisper alignment failed: %s", e)
        return jsonify({"status": "error", "stage": "whisper", "message": str(e)}), 500

    # -------------------------------------------------------------------
    # Stage 3: Concept Grouper → timestamp script
    # -------------------------------------------------------------------
    log.info("Stage 3/3 — Building timestamp script...")
    try:
        timestamp_script = group_into_scenes(
            original_script=script,
            words=words,
        )
        log.info("Timestamp script generated (%d characters)", len(timestamp_script))
    except Exception as e:
        log.error("Concept grouper failed: %s", e)
        return jsonify({"status": "error", "stage": "grouper", "message": str(e)}), 500

    # -------------------------------------------------------------------
    # Success
    # -------------------------------------------------------------------
    audio_filename = os.path.basename(audio_path)
    return jsonify({
        "status": "ok",
        "timestamp_script": timestamp_script,
        "audio_url": f"/api/audio/{audio_filename}",
    })


@app.route("/api/audio/<filename>")
def serve_audio(filename: str):
    """
    Stream the generated audio file for playback and download.
    Only serves files from the OUTPUT_DIR to prevent directory traversal.
    """
    # Security: only allow alphanumeric + underscore + dot filenames
    import re
    if not re.match(r'^[\w\-. ]+$', filename):
        return jsonify({"error": "Invalid filename"}), 400

    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Audio file not found"}), 404

    return send_file(
        file_path,
        mimetype="audio/wav",
        as_attachment=False,        # Allows browser to play inline
        download_name="voiceover.wav",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    log.info("=" * 60)
    log.info("  Timestamp Script Analyzer")
    log.info("  http://localhost:5000")
    log.info("=" * 60)
    log.info("Models will download automatically on first use.")
    app.run(host="0.0.0.0", port=5000, debug=False)
