"""
kokoro_engine.py
Kokoro TTS implementation with deterministic local resource validation.
NO automatic runtime downloads occur during Generate workflow.
"""

import os
import re
import time
import logging
import tempfile
from datetime import datetime
from typing import Callable, List, Optional, Tuple

import numpy as np
import soundfile as sf

from tts_engines.base import TTSEngine
from resource_manager import ResourceManager

log = logging.getLogger(__name__)

# Lazy-load KPipeline per language code
_pipeline_cache: dict = {}


def _get_kokoro_pipeline(lang_code: str):
    if lang_code not in _pipeline_cache:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log.info("[RUNTIME TRACE] %s KPipeline creation requested (lang=%s)", ts, lang_code)

        # 1. Deterministic Stage 1 (TTS) Resource Verification (NO Runtime Downloads!)
        mgr = ResourceManager.get_instance()
        mgr.verify_tts_resources()

        # 2. Bind eSpeak NG library if available
        try:
            from dependency_check import detect_espeak
            res = detect_espeak()
            if res.dll_path and os.path.isfile(res.dll_path):
                ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                log.info("[RUNTIME TRACE] %s EspeakWrapper.set_library() invoked with: %s", ts, res.dll_path)
                from phonemizer.backend.espeak.wrapper import EspeakWrapper
                EspeakWrapper.set_library(res.dll_path)
        except Exception as exc:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log.warning("[RUNTIME TRACE] %s EspeakWrapper.set_library() warning: %s", ts, exc)

        # 3. Instantiate KPipeline locally
        try:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log.info("[RUNTIME TRACE] %s Phonemizer & Kokoro initialization attempted", ts)
            log.info("Loading Kokoro KPipeline (lang=%s)…", lang_code)
            from kokoro import KPipeline
            _pipeline_cache[lang_code] = KPipeline(lang_code=lang_code)
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log.info("[RUNTIME TRACE] %s Kokoro KPipeline loaded successfully (lang=%s).", ts, lang_code)
        except Exception as exc:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log.error("[RUNTIME TRACE] %s First exception thrown in KPipeline creation: %s", ts, exc)
            raise RuntimeError(f"KPipeline Initialization Error ({type(exc).__name__}): {exc}") from exc

    return _pipeline_cache[lang_code]


def _strip_timestamps(text: str) -> str:
    clean = re.sub(r'\[\d{2}:\d{2}\]', '', text)
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    return clean.strip()


class KokoroEngine(TTSEngine):

    SAMPLE_RATE = 24_000

    @property
    def name(self) -> str:
        return "Kokoro TTS"

    @property
    def available_voices(self) -> List[Tuple[str, str]]:
        return [
            ("af_bella",   "Bella — American Female (Warm)"),
            ("af_sarah",   "Sarah — American Female (Clear)"),
            ("af_sky",     "Sky — American Female (Bright)"),
            ("am_adam",    "Adam — American Male (Deep)"),
            ("am_michael", "Michael — American Male (Natural)"),
            ("bf_emma",    "Emma — British Female (Crisp)"),
            ("bm_george",  "George — British Male (Rich)"),
        ]

    def generate(
        self,
        text:         str,
        output_path:  str,
        voice:        str                           = "af_bella",
        speed:        float                         = 1.0,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> Optional[str]:
        clean_text = _strip_timestamps(text)
        if not clean_text:
            raise ValueError("Text is empty after timestamp removal.")

        lang_code = "b" if voice.startswith("b") else "a"
        pipeline  = _get_kokoro_pipeline(lang_code)

        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log.info(
            "[RUNTIME TRACE] %s KokoroEngine.generate started — voice=%s speed=%.1f chars=%d",
            ts, voice, speed, len(clean_text),
        )

        audio_chunks = []
        chunks_generated = 0
        try:
            for _, _, chunk in pipeline(clean_text, voice=voice, speed=speed):
                if cancel_check and cancel_check():
                    log.info("KokoroEngine: cancellation detected. Stopping.")
                    return None

                if chunk is not None and len(chunk) > 0:
                    audio_chunks.append(chunk)
                    chunks_generated += 1

        except Exception as exc:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log.error("[RUNTIME TRACE] %s First exception thrown in Kokoro synthesis: %s", ts, exc)
            raise RuntimeError(f"Kokoro Synthesis Error ({type(exc).__name__}): {exc}") from exc

        if not audio_chunks:
            raise RuntimeError("Kokoro produced no audio output.")

        audio    = np.concatenate(audio_chunks, axis=0)
        duration = len(audio) / self.SAMPLE_RATE

        out_dir = os.path.dirname(output_path)
        os.makedirs(out_dir, exist_ok=True)

        tmp_fd, tmp_path = tempfile.mkstemp(dir=out_dir, suffix=".wav.tmp")
        try:
            os.close(tmp_fd)
            sf.write(tmp_path, audio, samplerate=self.SAMPLE_RATE, format="WAV")
            os.replace(tmp_path, output_path)
        except Exception as exc:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise RuntimeError(f"Failed to write audio file: {exc}") from exc

        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log.info(
            "[RUNTIME TRACE] %s KokoroEngine audio saved successfully — path=%s duration=%.2fs",
            ts, output_path, duration,
        )
        return output_path
