"""
kokoro_provider.py
Kokoro TTS Voice Provider implementation wrapping the stable KokoroEngine.
Includes Text Normalization, Custom Pronunciation Dictionary, Audio Quality Validation,
and Professional Stage Timing Logging.
"""

import time
import logging
from typing import List, Dict, Any, Optional

from voice_engine.base_provider import BaseVoiceProvider
from voice_engine.capabilities import ProviderCapabilities, VoiceMetadata
from voice_engine.narration_modes import NarrationMode, HumanizationSettings
from voice_engine.post_processing import PostProcessingConfig
from voice_engine.text_normalizer import TextNormalizer
from voice_engine.dictionary import PronunciationDictionaryManager
from voice_engine.audio_validator import AudioQualityValidator
from tts_engines.kokoro_engine import KokoroEngine
from config import VOICES, DEFAULT_VOICE

log = logging.getLogger(__name__)


class KokoroVoiceProvider(BaseVoiceProvider):
    """
    Offline Kokoro TTS Provider.
    """

    def __init__(self):
        self._engine = KokoroEngine()
        self._normalizer = TextNormalizer()
        self._capabilities = ProviderCapabilities(
            supports_offline=True,
            supports_preview=True,
            supports_streaming=False,
            supports_speed=True,
            supports_word_pause=True,
            supports_sentence_pause=True,
            supports_paragraph_pause=True,
            supports_emotion=True,
            supports_expressiveness=True,
            supports_style_presets=True,
            supports_narration_modes=True,
            supports_cloning=False,
            supports_custom_voices=False,
            supports_voice_search=True,
            supports_seed=False,
            supports_audio_formats=["wav", "mp3", "flac"],
            supports_sample_rates=[24000],
            supports_word_level_metadata=True,
        )

    @property
    def provider_id(self) -> str:
        return "kokoro"

    @property
    def name(self) -> str:
        return "Kokoro TTS (Offline)"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    def list_voices(self) -> List[VoiceMetadata]:
        voices = []
        for voice_id, label in VOICES:
            if voice_id.startswith("bf_") or voice_id.startswith("bm_"):
                accent = "English (UK)"
            else:
                accent = "English (US)"

            if voice_id.startswith("af_") or voice_id.startswith("bf_"):
                gender = "Female"
            else:
                gender = "Male"

            voices.append(
                VoiceMetadata(
                    voice_id=voice_id,
                    name=label,
                    language="en-us" if accent == "English (US)" else "en-gb",
                    gender=gender,
                    accent=accent,
                    provider_id=self.provider_id,
                    description=f"Kokoro 82M {gender} voice ({accent})",
                    naturalness_rating=5,
                    recommended_uses=["Documentary", "YouTube Explainer", "Storytelling"],
                    tags=["offline", "fast", "natural"],
                )
            )
        return voices

    def synthesize(
        self,
        text: str,
        output_path: str,
        voice_id: str,
        speed: float = 1.0,
        pitch: float = 1.0,
        narration_mode: Optional[NarrationMode] = None,
        humanization: Optional[HumanizationSettings] = None,
        post_processing: Optional[PostProcessingConfig] = None,
        **kwargs,
    ) -> str:
        """Synthesize text to audio using stable KokoroEngine with professional stage logging."""
        t_start = time.monotonic()
        log.info("========== STAGE 1: TEXT NORMALIZATION ==========")
        norm_text = self._normalizer.normalize(text)
        t_norm = time.monotonic() - t_start
        log.info("  Text normalized in %.3fs", t_norm)

        log.info("========== STAGE 2: PRONUNCIATION DICTIONARY ==========")
        t2 = time.monotonic()
        final_text = PronunciationDictionaryManager.get_instance().apply_dictionary(norm_text)
        t_dict = time.monotonic() - t2
        log.info("  Pronunciation dictionary applied in %.3fs", t_dict)

        log.info("========== STAGE 3: KOKORO TTS SYNTHESIS ==========")
        t3 = time.monotonic()
        res_path = self._engine.generate(
            text=final_text,
            output_path=output_path,
            voice=voice_id or DEFAULT_VOICE,
            speed=speed,
        )
        t_synth = time.monotonic() - t3
        log.info("  Kokoro synthesis completed in %.3fs", t_synth)

        log.info("========== STAGE 4: AUDIO QUALITY VALIDATION ==========")
        val_res = AudioQualityValidator.validate_wav(res_path)
        if not val_res.is_valid:
            log.warning("  Audio validation failed: %s", val_res.error_message)
        else:
            log.info("  Audio validation PASSED (Duration: %.2fs, Sample Rate: %d Hz)", val_res.duration_sec, val_res.sample_rate)

        total_time = time.monotonic() - t_start
        log.info("========== TOTAL SYNTHESIS TIME: %.3fs ==========", total_time)
        return res_path

    def generate_preview(
        self,
        voice_id: str,
        output_path: str,
        text: str = "Hello! This is a preview of the selected voice.",
        speed: float = 1.0,
    ) -> str:
        """Generate short preview audio using full normalization & synthesis pipeline."""
        norm_text = self._normalizer.normalize(text)
        final_text = PronunciationDictionaryManager.get_instance().apply_dictionary(norm_text)
        return self._engine.generate(
            text=final_text,
            output_path=output_path,
            voice=voice_id or DEFAULT_VOICE,
            speed=speed,
        )
