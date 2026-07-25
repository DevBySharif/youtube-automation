"""
queue_manager.py
Image Batch Scheduler and Generation Queue Manager supporting pause, resume, retry, and status tracking.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from image_engine.registry import ImageProviderRegistry
from image_engine.capabilities import ImageOutputMetadata
from image_engine.validator import ImageQualityValidator


@dataclass
class ImageGenerationTask:
    task_id: str
    image_index: int
    scene_index: int
    prompt: str
    negative_prompt: str
    output_path: str
    style: str
    status: str = "pending"  # pending, running, completed, failed, cancelled
    progress_pct: int = 0
    error_message: Optional[str] = None
    output_metadata: Optional[ImageOutputMetadata] = None


class ImageBatchScheduler:
    """Manages batch queue generation of image events."""

    def __init__(self):
        self._queue: List[ImageGenerationTask] = []
        self._is_paused: bool = False

    def populate_queue(self, image_plan_events: List[Dict[str, Any]], output_dir: str) -> List[ImageGenerationTask]:
        self._queue.clear()
        for idx, ev in enumerate(image_plan_events, start=1):
            out_path = f"{output_dir}/scene_{ev.get('scene_index', idx)}_img_{idx}.png"
            task = ImageGenerationTask(
                task_id=f"img_task_{idx}",
                image_index=ev.get("image_index", idx),
                scene_index=ev.get("scene_index", 1),
                prompt=ev.get("positive_prompt", ev.get("main_subject", "")),
                negative_prompt=ev.get("negative_prompt", ""),
                output_path=out_path,
                style=ev.get("visual_style", "cinematic"),
            )
            self._queue.append(task)
        return list(self._queue)

    def run_all(self, provider_id: Optional[str] = None) -> List[ImageOutputMetadata]:
        provider = ImageProviderRegistry.get_instance().get_provider(provider_id)
        results = []

        for task in self._queue:
            if self._is_paused:
                break
            task.status = "running"
            task.progress_pct = 50

            try:
                res = provider.generate_image(
                    prompt=task.prompt,
                    output_path=task.output_path,
                    negative_prompt=task.negative_prompt,
                    style=task.style,
                    image_index=task.image_index,
                    scene_index=task.scene_index,
                )
                val = ImageQualityValidator.validate_image(res.output_path)
                if not val.is_valid:
                    task.status = "failed"
                    task.error_message = val.error_message
                else:
                    task.status = "completed"
                    task.progress_pct = 100
                    task.output_metadata = res
                    results.append(res)
            except Exception as exc:
                task.status = "failed"
                task.error_message = f"Generation exception: {exc}"

        return results

    def pause(self) -> None:
        self._is_paused = True

    def resume(self) -> None:
        self._is_paused = False

    def get_queue(self) -> List[ImageGenerationTask]:
        return list(self._queue)
