# -*- mode: python ; coding: utf-8 -*-
#
# Timestamp Script Analyzer.spec
# PyInstaller spec file — --onedir build (recommended for torch + PySide6)
#
# Build command:
#   pyinstaller -y "Timestamp Script Analyzer.spec"
#
# Output:
#   dist\Timestamp Script Analyzer\Timestamp Script Analyzer.exe

import sys
sys.setrecursionlimit(5000)

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

# ── Collect large & dynamic packages ──────────────────────────────────────────

kokoro_datas,        kokoro_binaries,        kokoro_hiddenimports        = collect_all('kokoro')
misaki_datas,        misaki_binaries,        misaki_hiddenimports        = collect_all('misaki')
phonemizer_datas,    phonemizer_binaries,    phonemizer_hiddenimports    = collect_all('phonemizer')
language_tags_datas, language_tags_binaries, language_tags_hiddenimports = collect_all('language_tags')
transformers_datas,  transformers_binaries,  transformers_hiddenimports  = collect_all('transformers')
spacy_datas,         spacy_binaries,         spacy_hiddenimports         = collect_all('spacy')
spacy_model_datas,   spacy_model_binaries,   spacy_model_hiddenimports   = collect_all('en_core_web_sm')
num2words_datas,     num2words_binaries,     num2words_hiddenimports     = collect_all('num2words')
loguru_datas,        loguru_binaries,        loguru_hiddenimports        = collect_all('loguru')

fw_hiddenimports = collect_submodules('faster_whisper')
fw_datas         = collect_data_files('faster_whisper')
sf_datas, sf_binaries, sf_hiddenimports = collect_all('soundfile')

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=(
        kokoro_binaries
        + misaki_binaries
        + phonemizer_binaries
        + language_tags_binaries
        + transformers_binaries
        + spacy_binaries
        + spacy_model_binaries
        + num2words_binaries
        + loguru_binaries
        + sf_binaries
    ),
    datas=(
        [('resources/espeak', 'espeak')]
        + kokoro_datas
        + misaki_datas
        + phonemizer_datas
        + language_tags_datas
        + transformers_datas
        + spacy_datas
        + spacy_model_datas
        + num2words_datas
        + loguru_datas
        + fw_datas
        + sf_datas
    ),
    hiddenimports=(
        kokoro_hiddenimports
        + misaki_hiddenimports
        + phonemizer_hiddenimports
        + language_tags_hiddenimports
        + transformers_hiddenimports
        + spacy_hiddenimports
        + spacy_model_hiddenimports
        + num2words_hiddenimports
        + loguru_hiddenimports
        + fw_hiddenimports
        + sf_hiddenimports
        + [
            'config',
            'dependency_check',
            'resource_manager',
            'tts_engine',
            'aligner',
            'concept_grouper',
            'pipeline.pipeline',
            'pipeline.worker',
            'tts_engines',
            'tts_engines.base',
            'tts_engines.kokoro_engine',
            'voice_engine',
            'voice_engine.capabilities',
            'voice_engine.base_provider',
            'voice_engine.kokoro_provider',
            'voice_engine.registry',
            'voice_engine.narration_modes',
            'voice_engine.post_processing',
            'voice_engine.metadata',
            'voice_engine.favorites',
            'voice_engine.history',
            'voice_engine.text_normalizer',
            'voice_engine.dictionary',
            'voice_engine.presets',
            'voice_engine.audio_validator',
            'voice_engine.intelligence',
            'voice_engine.exporters',
            'ui.voice_cloning_dialog',
            'ui.voice_library_dialog',
            'ui.advanced_voice_panel',
            'ui.history_dialog',
            'ui.dictionary_dialog',
            'ui.main_window',
            'ui.script_panel',
            'ui.controls_panel',
            'ui.output_tabs',
            'ui.audio_player',
            'ui.styles',
            'ui.notification_banner',
            'ui.settings_dialog',
            'ui.error_dialog',
            'ui.diagnostics_dialog',
            'ui.resource_manager_dialog',
            'PySide6.QtMultimedia',
            'PySide6.QtMultimediaWidgets',
            'torch',
            'torch.jit',
            'torchaudio',
            'scipy',
            'scipy.io',
            'scipy.signal',
            'numpy',
            'numpy.core',
            'soundfile',
            'cffi',
        ]
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'IPython',
        'notebook',
        'jupyter',
        'PIL',
        'cv2',
        'sklearn',
        'pandas',
        'tensorflow',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Timestamp Script Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Timestamp Script Analyzer',
)
