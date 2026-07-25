"""
kokoro_provider.py
Kokoro TTS Voice Provider implementation wrapping the stable KokoroEngine.
"""

from typing import List, Dict, Any, Optional

from voice_engine.base_provider import BaseVoiceProvider
from voice_engine.capabilities import ProviderCapabilities, VoiceMetadata
from voice_engine.narration_modes import NarrationMode, HumanizationSettings
from voice_engine.post_processing import PostProcessingConfig
from tts_engines.kokoro_engine import KokoroEngine
from config import VOICES, DEFAULT_VOICE


class KokoroVoiceProvider(BaseVoiceProvider):
    """
    Offline Kokoro TTS Provider.
    """

    def __init__(self):
        self._engine = KokoroEngine()
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
        """Synthesize audio using stable KokoroEngine."""
        res_path = self._engine.generate(
            text=text,
            output_path=output_path,
            voice=voice_id or DEFAULT_VOICE,
            speed=speed,
        )
        return res_path

    def generate_preview(
        self,
        voice_id: str,
        output_path: str,
        text: str = "Hello! This is a preview of the selected voice.",
        speed: float = 1.0,
    ) -> str:
        """Generate short preview audio using KokoroEngine."""
        return self._engine.generate(
            text=text,
            output_path=output_path,
            voice=voice_id or DEFAULT_VOICE,
            speed=speed,
        )
