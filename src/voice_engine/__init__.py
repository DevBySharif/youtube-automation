"""
__init__.py
Voice Engine package init.
"""

from voice_engine.capabilities import ProviderCapabilities, VoiceMetadata, QualityProfile, QUALITY_PROFILES
from voice_engine.base_provider import BaseVoiceProvider
from voice_engine.kokoro_provider import KokoroVoiceProvider
from voice_engine.registry import VoiceProviderRegistry
from voice_engine.narration_modes import NarrationMode, HumanizationSettings, NARRATION_MODE_LABELS, NARRATION_MODE_PROFILES
from voice_engine.post_processing import PostProcessingConfig, AudioPostProcessor
from voice_engine.intelligence import NarrationIntelligenceEngine, MasterVideoAutomationJSON
from voice_engine.exporters import SubtitleExporter
from voice_engine.image_planner import ImageTimelineEngine, ImageTimelinePlan, VisualStyle

__all__ = [
    "ProviderCapabilities",
    "VoiceMetadata",
    "QualityProfile",
    "QUALITY_PROFILES",
    "BaseVoiceProvider",
    "KokoroVoiceProvider",
    "VoiceProviderRegistry",
    "NarrationMode",
    "HumanizationSettings",
    "NARRATION_MODE_LABELS",
    "NARRATION_MODE_PROFILES",
    "PostProcessingConfig",
    "AudioPostProcessor",
    "WordMetadata",
    "NarrationMetadataExport",
    "NarrationIntelligenceEngine",
    "MasterVideoAutomationJSON",
    "SubtitleExporter",
    "ImageTimelineEngine",
    "ImageTimelinePlan",
    "VisualStyle",
]
