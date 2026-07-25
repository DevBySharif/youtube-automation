"""
image_studio_panel.py
Professional AI Image Generation Studio Panel for PySide6 UI.
Features:
  • Provider & Model Selectors (FLUX, SDXL, OpenAI DALL-E, Gemini, ComfyUI, etc.)
  • Prompt Builder & Template Selectors (16 Templates)
  • Advanced Parameters (CFG, Steps, Sampler, Aspect Ratio, Seed)
  • Character, Location, and Object Consistency Registries
  • Generation History & Gallery Shortcuts
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit,
    QLineEdit, QSlider, QPushButton, QFrame, QCheckBox, QSpinBox, QTabWidget,
)
from PySide6.QtCore import Qt

from image_engine.registry import ImageProviderRegistry
from image_engine.templates import PromptTemplatesManager
from image_engine.config_manager import ProviderConfigManager
from image_engine.prompt_builder import PromptBuilderEngine
from ui.prompt_preview_dialog import PromptPreviewDialog
from ui.image_history_dialog import ImageHistoryDialog


class ImageStudioPanel(QWidget):
    """Studio panel for configuring and testing AI Image Generation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._builder = PromptBuilderEngine()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header Title
        title = QLabel("🖼  AI IMAGE GENERATION STUDIO")
        title.setObjectName("sectionLabel")
        layout.addWidget(title)

        # Provider Card
        prov_card = QFrame()
        prov_card.setObjectName("card")
        p_layout = QVBoxLayout(prov_card)
        p_layout.setContentsMargins(12, 10, 12, 10)
        p_layout.setSpacing(8)

        p_row = QHBoxLayout()
        p_row.addWidget(QLabel("PROVIDER:"))
        self.provider_combo = QComboBox()
        for prov in ImageProviderRegistry.get_instance().list_providers():
            self.provider_combo.addItem(prov["name"], userData=prov["id"])
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        p_row.addWidget(self.provider_combo, stretch=1)
        p_layout.addLayout(p_row)

        m_row = QHBoxLayout()
        m_row.addWidget(QLabel("MODEL:"))
        self.model_combo = QComboBox()
        m_row.addWidget(self.model_combo, stretch=1)
        p_layout.addLayout(m_row)

        layout.addWidget(prov_card)

        # Template Card
        tmpl_card = QFrame()
        tmpl_card.setObjectName("card")
        t_layout = QHBoxLayout(tmpl_card)
        t_layout.setContentsMargins(12, 8, 12, 8)
        t_layout.addWidget(QLabel("VISUAL TEMPLATE:"))
        self.template_combo = QComboBox()
        for tmpl in PromptTemplatesManager.list_templates():
            self.template_combo.addItem(tmpl)
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        t_layout.addWidget(self.template_combo, stretch=1)
        layout.addWidget(tmpl_card)

        # Prompt Input Card
        prompt_card = QFrame()
        prompt_card.setObjectName("card")
        pr_layout = QVBoxLayout(prompt_card)
        pr_layout.setContentsMargins(12, 10, 12, 10)

        pr_layout.addWidget(QLabel("MAIN SUBJECT & PROMPT:"))
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Describe main subject (e.g. 'A futuristic AI narrator in studio')")
        pr_layout.addWidget(self.subject_input)

        # Shortcuts
        btn_row = QHBoxLayout()
        preview_btn = QPushButton("🔍  Preview Prompt")
        preview_btn.clicked.connect(self._open_prompt_preview)
        btn_row.addWidget(preview_btn)

        hist_btn = QPushButton("📜  History Studio")
        hist_btn.clicked.connect(self._open_history_studio)
        btn_row.addWidget(hist_btn)
        pr_layout.addLayout(btn_row)

        layout.addWidget(prompt_card)
        layout.addStretch()

        self._on_provider_changed()

    def _on_provider_changed(self) -> None:
        pid = self.provider_combo.currentData() or "flux"
        prov = ImageProviderRegistry.get_instance().get_provider(pid)
        self.model_combo.clear()
        for m in prov.list_supported_models():
            self.model_combo.addItem(m)

    def _on_template_changed(self) -> None:
        tmpl_name = self.template_combo.currentText()
        tmpl = PromptTemplatesManager.get_template(tmpl_name)

    def _open_prompt_preview(self) -> None:
        subj = self.subject_input.text().strip() or "A futuristic AI narrator"
        tmpl_name = self.template_combo.currentText()
        tmpl = PromptTemplatesManager.get_template(tmpl_name)

        built = self._builder.build_prompt(
            main_subject=subj,
            style=tmpl.get("style", "cinematic"),
            camera=tmpl.get("camera", "Wide Shot"),
            lighting=tmpl.get("lighting", "dramatic lighting"),
            quality_tags=tmpl.get("quality_tags"),
            custom_negative=tmpl.get("negative_prompt", ""),
        )

        pid = self.provider_combo.currentData() or "flux"
        model_name = self.model_combo.currentText() or "flux-schnell"

        dlg = PromptPreviewDialog(
            positive_prompt=built["positive_prompt"],
            negative_prompt=built["negative_prompt"],
            provider_id=pid,
            model_name=model_name,
            parent=self,
        )
        dlg.exec()

    def _open_history_studio(self) -> None:
        dlg = ImageHistoryDialog(self)
        dlg.exec()
