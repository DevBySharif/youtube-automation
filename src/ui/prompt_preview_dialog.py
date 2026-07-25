"""
prompt_preview_dialog.py
UI Dialog for Prompt Preview Studio.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame,
)
from PySide6.QtCore import Qt


class PromptPreviewDialog(QDialog):
    """UI Dialog for reviewing and editing built prompts before generation."""

    def __init__(self, positive_prompt: str, negative_prompt: str, provider_id: str, model_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍  Prompt Preview Studio")
        self.setMinimumSize(680, 480)

        self._pos_prompt = positive_prompt
        self._neg_prompt = negative_prompt
        self.provider_id = provider_id
        self.model_name = model_name

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("🔍  PROMPT PREVIEW STUDIO")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        # Specs info
        spec_lbl = QLabel(f"Provider: {self.provider_id.upper()}  •  Model: {self.model_name}  •  Estimated VRAM: ~6.2 GB")
        spec_lbl.setStyleSheet("color: #9EFF00; font-weight: 700; font-size: 8.5pt;")
        layout.addWidget(spec_lbl)

        # Positive Prompt
        layout.addWidget(QLabel("POSITIVE PROMPT:"))
        self.pos_edit = QTextEdit()
        self.pos_edit.setPlainText(self._pos_prompt)
        layout.addWidget(self.pos_edit)

        # Negative Prompt
        layout.addWidget(QLabel("NEGATIVE PROMPT:"))
        self.neg_edit = QTextEdit()
        self.neg_edit.setPlainText(self._neg_prompt)
        self.neg_edit.setMaximumHeight(80)
        layout.addWidget(self.neg_edit)

        # Actions
        actions = QHBoxLayout()
        actions.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        actions.addWidget(cancel_btn)

        confirm_btn = QPushButton("▶  Proceed to Generation")
        confirm_btn.setObjectName("generateButton")
        confirm_btn.clicked.connect(self.accept)
        actions.addWidget(confirm_btn)

        layout.addLayout(actions)

    def get_prompts(self) -> tuple[str, str]:
        return self.pos_edit.toPlainText().strip(), self.neg_edit.toPlainText().strip()
