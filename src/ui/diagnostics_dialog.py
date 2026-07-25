"""
diagnostics_dialog.py
System diagnostics dialog with JSON export and granular pipeline checklist.

Features:
  - Granular check breakdown (Executable Exists, DLL Exists, Launch Test, Ctypes Load Test, Phonemizer Test, Kokoro Test)
  - Overall status indicator: 🟢 READY or 🔴 DEPENDENCY ISSUE
  - Export JSON report (diagnostics.json) & Copy Markdown Report (Ctrl+Shift+D)
"""

import os
import sys
import json
import platform
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QApplication, QMessageBox, QFileDialog, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui  import QFont, QShortcut, QKeySequence

from config import APP_NAME, APP_VERSION, LOGS_DIR, TEMP_DIR, MODELS_DIR
from dependency_check import detect_espeak


def generate_diagnostic_data() -> dict:
    """Gather complete diagnostic data dictionary."""
    espeak_res = detect_espeak()

    py_ver = sys.version.split()[0]
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"

    def _get_ver(mod_name):
        try:
            m = __import__(mod_name)
            return getattr(m, "__version__", "Installed")
        except ImportError:
            return "Not Installed"
        except Exception as exc:
            return f"Import Error: {exc}"

    torch_ver = _get_ver("torch")
    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        cuda_str   = f"CUDA: {cuda_avail}"
        if cuda_avail:
            cuda_str += f" ({torch.cuda.get_device_name(0)})"
    except Exception:
        cuda_str = "CUDA: N/A"

    def _check_write(path):
        t = os.path.join(path, ".diag_test")
        try:
            os.makedirs(path, exist_ok=True)
            with open(t, "w") as fh:
                fh.write("ok")
            os.remove(t)
            return "Writable"
        except Exception as exc:
            return f"Permission Error ({exc})"

    overall_ready = espeak_res.is_found and espeak_res.execution_passed

    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "overall_status": "READY" if overall_ready else "DEPENDENCY_MISSING",
        "system": {
            "node": platform.node(),
            "os": os_info,
            "python": py_ver,
            "executable": sys.executable,
        },
        "dependencies": {
            "PySide6": _get_ver("PySide6"),
            "torch": torch_ver,
            "cuda": cuda_str,
            "kokoro": _get_ver("kokoro"),
            "transformers": _get_ver("transformers"),
            "faster_whisper": _get_ver("faster_whisper"),
            "phonemizer": _get_ver("phonemizer"),
            "scipy": _get_ver("scipy"),
        },
        "espeak_ng": espeak_res.to_dict(),
        "directories": {
            "MODELS_DIR": {"path": MODELS_DIR, "status": _check_write(MODELS_DIR)},
            "LOGS_DIR": {"path": LOGS_DIR, "status": _check_write(LOGS_DIR)},
            "TEMP_DIR": {"path": TEMP_DIR, "status": _check_write(TEMP_DIR)},
        },
    }


def generate_diagnostic_markdown() -> str:
    """Format diagnostic data into Markdown report."""
    data = generate_diagnostic_data()
    espeak = data["espeak_ng"]

    status_icon = "🟢 READY" if data["overall_status"] == "READY" else "🔴 DEPENDENCY ISSUE"

    report = f"""# {data['app_name']} — System Diagnostic Report
Overall Status: **{status_icon}**
Generated: {data['system']['node']} | OS: {data['system']['os']}

## 1. Application & Python Environment
- **App Version**: v{data['app_version']}
- **Python Executable**: `{data['system']['executable']}` ({data['system']['python']})
- **PySide6**: {data['dependencies']['PySide6']}

## 2. AI & ML Dependencies
- **PyTorch**: {data['dependencies']['torch']} ({data['dependencies']['cuda']})
- **Kokoro TTS**: {data['dependencies']['kokoro']}
- **Transformers**: {data['dependencies']['transformers']}
- **Faster-Whisper**: {data['dependencies']['faster_whisper']}
- **Phonemizer**: {data['dependencies']['phonemizer']}

## 3. eSpeak NG Windows Engine Verification
- **Status**: {"Detected ✓" if espeak['is_found'] else "Missing ❌"}
- **Detection Method**: {espeak['method_used']}
- **Executable Path**: `{espeak['exe_path'] or 'Not Found'}`
- **DLL Path**: `{espeak['dll_path'] or 'Not Found'}`
- **System PATH Status**: {"In System PATH ✓" if espeak['in_path'] else "Not in PATH (Injected dynamically) ⚠️"}
- **Version Test**: {espeak['version_str'] or 'Failed'} (Passed: {espeak['version_passed']})

### Detailed Verification Checklist:
"""
    for check_name, passed in espeak["detailed_checks"].items():
        icon = "✓" if passed else "❌"
        report += f"- [{icon}] **{check_name}**: {'PASSED' if passed else 'FAILED'}\n"

    report += f"""
## 4. Directories & Permissions
- **MODELS_DIR** (`HF_HOME`): `{data['directories']['MODELS_DIR']['path']}` ({data['directories']['MODELS_DIR']['status']})
- **LOGS_DIR**: `{data['directories']['LOGS_DIR']['path']}` ({data['directories']['LOGS_DIR']['status']})
- **TEMP_DIR**: `{data['directories']['TEMP_DIR']['path']}` ({data['directories']['TEMP_DIR']['status']})
"""
    return report


class DiagnosticsDialog(QDialog):
    """Diagnostics window displaying system check list and export tools."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} — System Diagnostics")
        self.setMinimumSize(660, 540)

        self._build_ui()
        self._load_diagnostics()

        shortcut = QShortcut(QKeySequence("Ctrl+Shift+D"), self)
        shortcut.activated.connect(self._copy_report)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Header with overall status badge
        header_row = QHBoxLayout()
        self.header_label = QLabel(f"<b>{APP_NAME} v{APP_VERSION} Diagnostics</b>")
        self.header_label.setStyleSheet("font-size: 11pt;")
        header_row.addWidget(self.header_label)

        header_row.addStretch()

        self.status_badge = QLabel("🟢  READY")
        self.status_badge.setStyleSheet("""
            background-color: #1E331E;
            color: #6A9153;
            border: 1px solid #4E733E;
            border-radius: 4px;
            padding: 3px 10px;
            font-weight: bold;
            font-size: 9.5pt;
        """)
        header_row.addWidget(self.status_badge)

        layout.addLayout(header_row)

        self.report_edit = QTextEdit()
        self.report_edit.setReadOnly(True)
        self.report_edit.setFont(QFont("Consolas", 9.5))
        layout.addWidget(self.report_edit, stretch=1)

        # Button Bar
        btn_bar = QHBoxLayout()

        copy_btn = QPushButton("⎘ Copy Markdown Report")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setToolTip("Copy Markdown report to clipboard (Ctrl+Shift+D)")
        copy_btn.clicked.connect(self._copy_report)
        btn_bar.addWidget(copy_btn)

        export_json_btn = QPushButton("↓ Export JSON…")
        export_json_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_json_btn.setToolTip("Export diagnostics.json for support tickets")
        export_json_btn.clicked.connect(self._export_json)
        btn_bar.addWidget(export_json_btn)

        open_logs_btn = QPushButton("📂 Open Logs")
        open_logs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_logs_btn.clicked.connect(self._open_log_folder)
        btn_bar.addWidget(open_logs_btn)

        btn_bar.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_bar.addWidget(close_btn)

        layout.addLayout(btn_bar)

    def _load_diagnostics(self) -> None:
        data = generate_diagnostic_data()
        if data["overall_status"] == "READY":
            self.status_badge.setText("🟢  READY")
            self.status_badge.setStyleSheet("background-color: #1E331E; color: #6A9153; border: 1px solid #4E733E; border-radius: 4px; padding: 3px 10px; font-weight: bold;")
        else:
            self.status_badge.setText("🔴  DEPENDENCY MISSING")
            self.status_badge.setStyleSheet("background-color: #331E1E; color: #F14C4C; border: 1px solid #733E3E; border-radius: 4px; padding: 3px 10px; font-weight: bold;")

        report = generate_diagnostic_markdown()
        self.report_edit.setPlainText(report)

    def _copy_report(self) -> None:
        report = self.report_edit.toPlainText()
        QApplication.clipboard().setText(report)
        QMessageBox.information(self, "Report Copied", "Diagnostic report copied to clipboard!\n\nYou can paste it directly into support tickets or messages.")

    def _export_json(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Diagnostics JSON",
            "diagnostics.json",
            "JSON Files (*.json);;All Files (*)",
        )
        if path:
            data = generate_diagnostic_data()
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, indent=2)
                QMessageBox.information(self, "Export Complete", f"Diagnostics saved to:\n{path}")
            except OSError as exc:
                QMessageBox.critical(self, "Export Failed", str(exc))

    def _open_log_folder(self) -> None:
        if os.path.exists(LOGS_DIR):
            subprocess.Popen(["explorer", os.path.normpath(LOGS_DIR)])
