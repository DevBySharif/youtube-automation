"""
dependency_check.py
Minimal startup dependency verification, eSpeak NG runtime discovery, and binding engine.

Detection Priority:
  1. Bundled PyInstaller runtime (_internal/espeak)
  2. Project portable resources folder (resources/espeak)
  3. System Program Files installation
  4. System PATH
"""

import os
import sys
import shutil
import logging
import winreg
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

from PySide6.QtCore import QThread, Signal

log = logging.getLogger(__name__)

MIN_ESPEAK_VERSION = (1, 48)


@dataclass
class EspeakDetectionResult:
    is_found: bool = False
    method_used: str = "None"
    exe_path: str = ""
    dll_path: str = ""
    dir_path: str = ""
    in_path: bool = False
    execution_passed: bool = False
    version_str: str = ""
    version_tuple: Tuple[int, ...] = (0, 0)
    version_passed: bool = False
    diagnostic_message: str = "eSpeak NG not detected."
    detailed_checks: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_found": self.is_found,
            "method_used": self.method_used,
            "exe_path": self.exe_path,
            "dll_path": self.dll_path,
            "dir_path": self.dir_path,
            "in_path": self.in_path,
            "execution_passed": self.execution_passed,
            "version_str": self.version_str,
            "version_passed": self.version_passed,
            "diagnostic_message": self.diagnostic_message,
            "detailed_checks": self.detailed_checks,
        }


def _get_candidate_espeak_dirs() -> List[Tuple[str, str]]:
    """Return priority-ordered list of candidate eSpeak directories with labels."""
    candidates = []

    # Priority 1: PyInstaller bundled runtime (_internal/espeak or _MEIPASS/espeak)
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(("Priority 1 (Bundled PyInstaller _internal/espeak)", os.path.join(exe_dir, "_internal", "espeak")))
        meipass = getattr(sys, "_MEIPASS", "")
        if meipass:
            candidates.append(("Priority 1 (Bundled PyInstaller _MEIPASS/espeak)", os.path.join(meipass, "espeak")))

    # Priority 2: Project portable resources folder (resources/espeak)
    # Check relative to cwd and relative to script location
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidates.append(("Priority 2 (Project Resources)", os.path.join(proj_root, "resources", "espeak")))
    candidates.append(("Priority 2 (CWD Resources)", os.path.abspath(os.path.join("resources", "espeak"))))

    # Priority 3: System Program Files installation
    system_dirs = [
        r"C:\Program Files\eSpeak NG",
        r"C:\Program Files (x86)\eSpeak NG",
        r"C:\eSpeak NG",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\eSpeak NG"),
    ]
    for d in system_dirs:
        candidates.append(("Priority 3 (System Installation)", d))

    return candidates


def _find_executable_and_dll(search_dir: str) -> Tuple[Optional[str], Optional[str]]:
    exe_found = None
    dll_found = None
    if not os.path.isdir(search_dir):
        return None, None

    for root, dirs, files in os.walk(search_dir):
        rel_depth = root[len(search_dir):].count(os.sep)
        if rel_depth > 3:
            dirs.clear()
            continue

        for f in files:
            f_lower = f.lower()
            if f_lower in ("espeak-ng.exe", "espeak.exe") and not exe_found:
                exe_found = os.path.abspath(os.path.join(root, f))
            elif f_lower in ("libespeak-ng.dll", "espeak-ng.dll", "libespeak.dll") and not dll_found:
                dll_found = os.path.abspath(os.path.join(root, f))

        if exe_found and dll_found:
            break

    # If DLL found in search_dir root but exe not, pair them in search_dir
    if not exe_found and dll_found:
        cand_exe = os.path.join(search_dir, "espeak-ng.exe")
        if os.path.isfile(cand_exe):
            exe_found = cand_exe

    return exe_found, dll_found


def detect_espeak(force_rescan: bool = False) -> EspeakDetectionResult:
    """Fast discovery of eSpeak NG runtime with priority-based binding."""
    res = EspeakDetectionResult()
    log.info("Lightweight eSpeak NG discovery...")

    # 1. Search candidate directories (Priority 1: Bundled, Priority 2: Resources, Priority 3: System)
    for label, base_dir in _get_candidate_espeak_dirs():
        if os.path.isdir(base_dir):
            cand_exe, cand_dll = _find_executable_and_dll(base_dir)
            if cand_dll and os.path.isfile(cand_dll):
                res.is_found = True
                res.method_used = label
                res.exe_path = cand_exe or ""
                res.dll_path = cand_dll
                res.dir_path = os.path.dirname(cand_dll)
                _bind_env(res)
                log.info("eSpeak NG discovered via %s -> DLL: %s", label, res.dll_path)
                return res

    # 2. Priority 4: Check System PATH
    which_exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if which_exe:
        res.is_found = True
        res.method_used = "Priority 4 (System PATH)"
        res.exe_path = os.path.abspath(which_exe)
        res.dir_path = os.path.dirname(res.exe_path)
        res.in_path = True
        cand_dll = os.path.join(res.dir_path, "libespeak-ng.dll")
        if os.path.isfile(cand_dll):
            res.dll_path = cand_dll
        _bind_env(res)
        log.info("eSpeak NG discovered via System PATH -> EXE: %s", res.exe_path)
        return res

    log.warning("eSpeak NG not found in bundled, resources, system, or PATH directories.")
    return res


def _bind_env(res: EspeakDetectionResult) -> None:
    """Bind environment variables and EspeakWrapper library path."""
    if res.dir_path:
        cur_path = os.environ.get("PATH", "")
        if res.dir_path.lower() not in cur_path.lower():
            os.environ["PATH"] = res.dir_path + os.path.pathsep + cur_path
        os.environ["PHONEMIZER_ESPEAK_PATH"] = res.dir_path
        os.environ["ESPEAK_DATA_PATH"] = res.dir_path

    if res.dir_path and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(res.dir_path)
        except Exception:
            pass

    if res.dll_path and os.path.isfile(res.dll_path):
        os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = res.dll_path
        try:
            from phonemizer.backend.espeak.wrapper import EspeakWrapper
            EspeakWrapper.set_library(res.dll_path)
            log.info("EspeakWrapper.set_library() bound cleanly -> %s", res.dll_path)
        except Exception as exc:
            log.warning("EspeakWrapper.set_library() binding error: %s", exc)


class DependencyManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DependencyManager()
        return cls._instance

    def run_pipeline_trace(self, force_rescan: bool = False):
        return detect_espeak(force_rescan)

    def get_espeak_result(self, force_rescan: bool = False):
        return detect_espeak(force_rescan)


def run_pipeline_trace(force_rescan: bool = False):
    return detect_espeak(force_rescan)


def run_checks() -> List[str]:
    """Minimal startup check — verifies write access to temp and log folders only."""
    from config import TEMP_DIR, LOGS_DIR
    issues = []
    for d_name, d_path in [("TEMP_DIR", TEMP_DIR), ("LOGS_DIR", LOGS_DIR)]:
        t = os.path.join(d_path, ".perm_test")
        try:
            os.makedirs(d_path, exist_ok=True)
            with open(t, "w") as fh:
                fh.write("ok")
            os.remove(t)
        except Exception as exc:
            issues.append(f"Cannot write to {d_name} ({d_path}): {exc}")
    return issues


class AsyncDependencyWorker(QThread):
    status_changed = Signal(str)
    finished       = Signal(list)

    def run(self) -> None:
        log.info("[TIMELINE] Worker started")
        detect_espeak()
        issues = run_checks()
        log.info("[TIMELINE] Minimal startup dependency scan completed (issues=%d)", len(issues))
        self.finished.emit(issues)
