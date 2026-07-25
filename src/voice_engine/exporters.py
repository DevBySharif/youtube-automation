"""
exporters.py
Subtitle and Timeline Exporter for SRT, VTT, ASS, and Video Automation JSON format.
"""

import json
import os
from typing import Dict, Any, List


def _format_timestamp_srt(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def _format_timestamp_vtt(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"


def _format_timestamp_ass(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    return f"{hrs:01d}:{mins:02d}:{secs:02d}.{centis:02d}"


class SubtitleExporter:
    """Exports subtitle files (SRT, VTT, ASS) and Master Video Automation JSON."""

    @staticmethod
    def export_all(
        master_data: Dict[str, Any],
        base_output_path: str
    ) -> Dict[str, str]:
        """
        Export SRT, VTT, ASS, and JSON timeline files without re-running synthesis.
        """
        abs_path = os.path.abspath(base_output_path)
        dir_name = os.path.dirname(abs_path)
        base_name = os.path.splitext(os.path.basename(abs_path))[0]
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        srt_path = os.path.join(dir_name, f"{base_name}.srt")
        vtt_path = os.path.join(dir_name, f"{base_name}.vtt")
        ass_path = os.path.join(dir_name, f"{base_name}.ass")
        json_path = os.path.join(dir_name, f"{base_name}_automation.json")

        subs: List[Dict[str, Any]] = master_data.get("subtitle_blocks", [])

        # 1. Export SRT
        with open(srt_path, "w", encoding="utf-8") as f:
            for sub in subs:
                f.write(f"{sub['index']}\n")
                f.write(f"{_format_timestamp_srt(sub['start_time'])} --> {_format_timestamp_srt(sub['end_time'])}\n")
                f.write(f"{sub['text']}\n\n")

        # 2. Export VTT
        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for sub in subs:
                f.write(f"{_format_timestamp_vtt(sub['start_time'])} --> {_format_timestamp_vtt(sub['end_time'])}\n")
                f.write(f"{sub['text']}\n\n")

        # 3. Export ASS
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write("[Script Info]\nTitle: YouTube Narration Subtitles\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n")
            f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write("Style: Default,Roboto,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,10,10,50,1\n\n")
            f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            for sub in subs:
                f.write(f"Dialogue: 0,{_format_timestamp_ass(sub['start_time'])},{_format_timestamp_ass(sub['end_time'])},Default,,0,0,0,,{sub['text']}\n")

        # 4. Export Master Video Automation JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(master_data, f, indent=2)

        return {
            "srt": srt_path,
            "vtt": vtt_path,
            "ass": ass_path,
            "json": json_path,
        }
