"""
tts_engines package

Available engines:
  KokoroEngine  — default, local, 82M parameter model
  TTSEngine     — abstract base class for custom engines

Usage:
  from tts_engines import KokoroEngine
  engine = KokoroEngine()
  engine.generate(text, output_path, voice="af_bella", speed=1.0)

Adding a new engine:
  1. Create tts_engines/your_engine.py
  2. Implement TTSEngine (generate, name, available_voices)
  3. Pass it to Pipeline(tts_engine=YourEngine())
  4. No other files need changing.
"""

from tts_engines.base import TTSEngine
from tts_engines.kokoro_engine import KokoroEngine

__all__ = ["TTSEngine", "KokoroEngine"]
