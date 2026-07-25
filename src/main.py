r"""
main.py
Entry point for Timestamp Script Analyzer.

Responsibilities:
  - Set up file logging to %LOCALAPPDATA%\Timestamp Script Analyzer\logs\app.log
  - Log EXE Bundle Verification parameters (sys.frozen, sys.executable, __file__, App Version)
  - Initialise QApplication with dark stylesheet
  - Clean up old temp files from previous sessions
  - Launch main window immediately (<300 ms)
"""

import sys
import os
import logging
from logging.handlers import RotatingFileHandler

# ── Bootstrap sys.path so sibling modules resolve correctly ───────────────────
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# ── Config must be imported before any other app module ───────────────────────
from config import APP_NAME, APP_VERSION, LOGS_DIR, cleanup_old_temp_files

# ── Logging ───────────────────────────────────────────────────────────────────
_log_file = os.path.join(LOGS_DIR, "app.log")

import io

# ── Ensure sys.stdout and sys.stderr are non-None streams in PyInstaller --windowed mode ──
class NullStream(io.TextIOWrapper):
    def __init__(self):
        super().__init__(io.BytesIO(), encoding="utf-8")
    def write(self, s):
        return len(s) if s else 0

if sys.stdout is None:
    sys.stdout = NullStream()
if sys.stderr is None:
    sys.stderr = NullStream()

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            _log_file,
            maxBytes=5 * 1024 * 1024,   # 5 MB
            backupCount=3,
            encoding="utf-8",
        ),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ── Log EXE Bundle Verification Parameters ─────────────────────────────────────
log.info("=" * 60)
log.info("  %s  v%s", APP_NAME, APP_VERSION)
log.info("  Log file: %s", _log_file)
log.info("  [EXE VERIFY] sys.frozen: %s", getattr(sys, "frozen", False))
log.info("  [EXE VERIFY] sys.executable: %s", sys.executable)
log.info("  [EXE VERIFY] __file__: %s", __file__)
log.info("  [EXE VERIFY] App Version: v%s", APP_VERSION)
log.info("=" * 60)

# ── Qt ────────────────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QApplication
from PySide6.QtCore    import Qt
from PySide6.QtGui     import QFont

from ui.styles      import DARK_STYLESHEET
from ui.main_window import MainWindow


def main() -> None:
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("TimestampAnalyzer")
    app.setStyleSheet(DARK_STYLESHEET)

    # Default application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Clean up temp files from previous sessions (non-blocking, fast)
    try:
        cleanup_old_temp_files()
    except Exception as exc:
        log.warning("Temp cleanup failed: %s", exc)

    # Launch main window instantly (<300 ms)
    window = MainWindow()
    window.show()

    log.info("[TIMELINE] UI shown")

    # Start background minimal check after event loop starts
    from PySide6.QtCore import QTimer
    QTimer.singleShot(0, window.start_async_dependency_check)

    log.info("QApplication event loop starting.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
