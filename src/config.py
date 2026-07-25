"""
config.py
Centralized configuration, paths, and constants.

All model downloads (HuggingFace/Kokoro and Faster-Whisper) are forced to cache
permanently inside:
    %LOCALAPPDATA%\\Timestamp Script Analyzer\\models\\
Model weights are NEVER stored in TEMP.
"""

import os
import sys

# ── Application Metadata ──────────────────────────────────────────────────────
APP_NAME    = "Timestamp Script Analyzer"
APP_VERSION = "1.0.0"

# ── Directory Layout ──────────────────────────────────────────────────────────
LOCALAPPDATA = os.environ.get(
    "LOCALAPPDATA",
    os.path.expanduser(r"~\AppData\Local"),
)

# Root application directory in LocalAppData
APP_DATA_DIR = os.path.join(LOCALAPPDATA, APP_NAME)

# Permanent subdirectories
MODELS_DIR = os.path.join(APP_DATA_DIR, "models")
LOGS_DIR   = os.path.join(APP_DATA_DIR, "logs")
TEMP_DIR   = os.path.join(os.environ.get("TEMP", os.path.expanduser(r"~\AppData\Local\Temp")), APP_NAME)

# Ensure directories exist
for _dir in (APP_DATA_DIR, MODELS_DIR, LOGS_DIR, TEMP_DIR):
    os.makedirs(_dir, exist_ok=True)

# ── Force Model Caching into LOCALAPPDATA/Timestamp Script Analyzer/models ──
os.environ["HF_HOME"]               = os.path.join(MODELS_DIR, "huggingface")
os.environ["HUGGINGFACE_HUB_CACHE"] = os.path.join(MODELS_DIR, "huggingface")
os.environ["TORCH_HOME"]            = os.path.join(MODELS_DIR, "torch")

# ── Pipeline Defaults ─────────────────────────────────────────────────────────
DEFAULT_VOICE         = "af_bella"
DEFAULT_SPEED         = 1.0
DEFAULT_WHISPER_MODEL = "base"

# ── Enriched Voices Catalog ───────────────────────────────────────────────────
# Format: (voice_id, display_label, details_tuple)
VOICES = [
    ("af_bella",   "Bella — American Female (Warm, Natural, 24 kHz)"),
    ("af_sarah",   "Sarah — American Female (Clear, Expressive, 24 kHz)"),
    ("af_sky",     "Sky — American Female (Bright, Energetic, 24 kHz)"),
    ("am_adam",    "Adam — American Male (Deep, Professional, 24 kHz)"),
    ("am_michael", "Michael — American Male (Natural, Conversational, 24 kHz)"),
    ("bf_emma",    "Emma — British Female (Crisp, Clear, 24 kHz)"),
    ("bm_george",  "George — British Male (Rich, Narrative, 24 kHz)"),
]

# ── Whisper Models Catalog ────────────────────────────────────────────────────
WHISPER_MODELS = [
    ("tiny",  "Tiny — Fastest (~75 MB, lower accuracy)"),
    ("base",  "Base — Balanced (~145 MB, Recommended)"),
    ("small", "Small — High Accuracy (~485 MB, slower)"),
]

# ── Temp File Policy ──────────────────────────────────────────────────────────
TEMP_MAX_AGE_SECONDS = 24 * 60 * 60  # 24 hours


def make_run_dir() -> str:
    """
    Create and return a unique timestamped directory for a single generation run.

    Example:
        %TEMP%\\Timestamp Script Analyzer\\2026-07-24_21-15-34\\
    """
    from datetime import datetime
    stamp   = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(TEMP_DIR, stamp)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def cleanup_old_temp_files(exclude_paths: set | None = None) -> None:
    """Delete run directories older than TEMP_MAX_AGE_SECONDS."""
    import time
    import shutil
    now         = time.time()
    exclude_set = exclude_paths or set()
    for name in os.listdir(TEMP_DIR):
        entry_path = os.path.join(TEMP_DIR, name)
        if entry_path in exclude_set:
            continue
        try:
            age = now - os.path.getmtime(entry_path)
            if age <= TEMP_MAX_AGE_SECONDS:
                continue
            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path, ignore_errors=True)
            elif name.endswith((".wav", ".txt")):
                os.remove(entry_path)
        except OSError:
            pass
