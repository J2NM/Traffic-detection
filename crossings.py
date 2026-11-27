"""Detect car line crossings and export review artifacts for the team."""

import csv
import json
import math
from collections import deque
from pathlib import Path
from tempfile import mkdtemp


class CrossingCounter:
    """Count the first finite-line crossing per ID using stable-side anchors."""

    def __init__(self, line_endpoints, margin=3.0, max_gap=30):
        self.a, self.b = [tuple(map(float, point)) for point in line_endpoints]
        if len(self.a) != 2 or len(self.b) != 2:
            raise ValueError("Line endpoints must each contain x and y.")
        self.dx, self.dy = self.b[0] - self.a[0], self.b[1] - self.a[1]
        self.length = math.hypot(self.dx, self.dy)
        if not all(map(math.isfinite, (*self.a, *self.b, margin))):
            raise ValueError("Line coordinates and margin must be finite.")
        if self.length == 0 or margin < 0 or max_gap < 1:
            raise ValueError("Use distinct endpoints, a nonnegative margin and positive gap.")
        self.margin, self.max_gap = margin, max_gap
        self.anchors = {}
        self.counted = set()

    def distance(self, point):
        return (self.dx * (point[1] - self.a[1]) - self.dy * (point[0] - self.a[0])) / self.length

    def update(self, track_id, point, frame_index):
        """Return interpolated crossing frame, or None when no new crossing occurs."""
        if track_id in self.counted:
            return None
        distance = self.distance(point)
        if abs(distance) <= self.margin:
            return None
        previous = self.anchors.get(track_id)
        self.anchors[track_id] = (point, distance, frame_index)
        if previous is None:
            return None
        old_point, old_distance, old_frame = previous
        if frame_index - old_frame > self.max_gap or old_distance * distance >= 0:
            return None
        fraction = old_distance / (old_distance - distance)
        intersection = tuple(old_point[i] + fraction * (point[i] - old_point[i]) for i in range(2))
        projection = ((intersection[0] - self.a[0]) * self.dx + (intersection[1] - self.a[1]) * self.dy) / self.length**2
        if not 0 <= projection <= 1:
            return None
        self.counted.add(track_id)
        return old_frame + fraction * (frame_index - old_frame)


def track_crossings(path, line_endpoints, *, output_dir="outputs", weights="yolo11n.pt",
                    confidence=0.25, margin=3.0, max_gap=30, device=None):
    """Return (crossing records, annotated video path) for one constant-rate clip.

    Endpoints use full-resolution pixel coordinates. Each call creates a fresh
    tracker and unique output directory. CSV crop_paths contains a JSON list of
    paths relative to that directory. Records use the same relative paths.
    A run is complete only when summary.json exists.
    """
    import cv2
    from ultralytics import YOLO

    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if not 0 < confidence <= 1:
        raise ValueError("confidence must be in (0, 1].")
    counter = CrossingCounter(line_endpoints, margin, max_gap)
    capture = cv2.VideoCapture(str(path))
    writer = None
    try:
        fps = capture.get(cv2.CAP_PROP_FPS)
        ok, frame = capture.read()
        if not ok or not math.isfinite(fps) or fps <= 0:
            raise ValueError("Video must decode and report a positive frame rate.")
        height, width = frame.shape[:2]
        if any(not (0 <= x < width and 0 <= y < height) for x, y in (counter.a, counter.b)):
            raise ValueError("Line endpoints must lie within the original video frame.")
        model = YOLO(weights)
        car_id = next((key for key, name in model.names.items() if name == "car"), None)
        if car_id is None:
            raise ValueError("The selected detector must include a car class.")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        run_dir = Path(mkdtemp(prefix="crossings-", dir=output_dir))
        (run_dir / "crops").mkdir()
        video_output = run_dir / "annotated.mp4"
        writer = cv2.VideoWriter(str(video_output), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
        if not writer.isOpened():
            raise RuntimeError("OpenCV could not create the annotated MP4.")
        records, recent = [], {}
        frame_index = 0
        with (run_dir / "crossings.csv").open("w", newline="", encoding="utf-8") as handle:
            table = csv.DictWriter(handle, fieldnames=["track_id", "time_seconds", "crop_paths"])
            table.writeheader()
            while ok:
                result = model.track(frame, persist=True, tracker="bytetrack.yaml", classes=[car_id],
                                     conf=confidence, device=device, verbose=False)[0]
                boxes = result.boxes
                if boxes is not None and boxes.id is not None:
                    for track_id, box in zip(boxes.id.int().cpu().tolist(), boxes.xyxy.cpu().tolist()):
                        x1, y1, x2, y2 = box
                        left, top = max(0, int(x1)), max(0, int(y1))
                        right, bottom = min(width, math.ceil(x2)), min(height, math.ceil(y2))
                        crop = frame[top:bottom, left:right]
                        if track_id not in counter.counted and crop.size:
                            history = recent.setdefault(track_id, deque(maxlen=3))
                            history.append((frame_index, crop.copy()))
                        crossing_frame = counter.update(track_id, ((x1 + x2) / 2, y2), frame_index)
                        if crossing_frame is not None:
                            crop_paths = []
                            for crop_frame, image in recent.pop(track_id, []):
                                relative = Path("crops") / f"track_{track_id}_frame_{crop_frame}.jpg"
                                if not cv2.imwrite(str(run_dir / relative), image):
                                    raise RuntimeError(f"Could not save crop {relative}")
                                crop_paths.append(relative.as_posix())
                            record = dict(track_id=track_id, time_seconds=round(crossing_frame / fps, 6), crop_paths=crop_paths)
                            records.append(record)
                            table.writerow({**record, "crop_paths": json.dumps(crop_paths)})
                            handle.flush()
                for track_id in list(recent):
                    if frame_index - recent[track_id][-1][0] > max_gap:
                        del recent[track_id]
                for track_id, anchor in list(counter.anchors.items()):
                    if frame_index - anchor[2] > max_gap:
                        del counter.anchors[track_id]
                annotated = result.plot()
                cv2.line(annotated, tuple(map(round, counter.a)), tuple(map(round, counter.b)), (0, 255, 255), 2)
                cv2.putText(annotated, f"Cars: {len(records)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                writer.write(annotated)
                frame_index += 1
                ok, frame = capture.read()
        writer.release()
        summary = dict(total_cars=len(records), frames_processed=frame_index, fps=fps,
                       width=width, height=height, line_endpoints=[counter.a, counter.b],
                       weights=str(weights), tracker="bytetrack.yaml", confidence=confidence,
                       margin=margin, max_gap=max_gap, anchor="bottom_center",
                       timestamp_basis="zero-based frame index / fps")
        (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return records, video_output
    finally:
        capture.release()
        if writer is not None:
            writer.release()
