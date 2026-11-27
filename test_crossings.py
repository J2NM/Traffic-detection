"""Regression checks for crossing geometry and artifact export without model weights."""

import csv
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from crossings import CrossingCounter, track_crossings


class CounterTests(unittest.TestCase):
    def test_first_crossing_and_reverse(self):
        counter = CrossingCounter(((0, 10), (20, 10)), margin=1)
        self.assertIsNone(counter.update(1, (5, 5), 0))
        self.assertEqual(counter.update(1, (5, 15), 10), 5)
        self.assertIsNone(counter.update(1, (5, 5), 20))
        counter.update(2, (5, 15), 0)
        self.assertEqual(counter.update(2, (5, 5), 10), 5)

    def test_finite_segment_and_missing_tracks(self):
        counter = CrossingCounter(((0, 10), (20, 10)), max_gap=5)
        counter.update(1, (25, 5), 0)
        self.assertIsNone(counter.update(1, (25, 15), 1))
        counter.update(2, (5, 5), 0)
        self.assertIsNone(counter.update(2, (5, 15), 10))

    def test_deadband_and_diagonal(self):
        counter = CrossingCounter(((0, 10), (20, 10)), margin=2)
        counter.update(1, (5, 5), 0)
        self.assertIsNone(counter.update(1, (5, 10), 1))
        self.assertIsNone(counter.update(1, (5, 11), 2))
        self.assertEqual(counter.update(1, (5, 15), 4), 2)
        diagonal = CrossingCounter(((0, 0), (20, 20)), margin=0)
        diagonal.update(1, (10, 5), 0)
        self.assertEqual(diagonal.update(1, (10, 15), 2), 1)

    def test_invalid_line(self):
        for endpoints in [((0, 0), (0, 0)), ((0, 0), (float('nan'), 1))]:
            with self.assertRaises(ValueError):
                CrossingCounter(endpoints)

    def test_export_and_fresh_runs(self):
        import cv2
        import numpy as np

        class Tensor:
            def __init__(self, value):
                self.value = value

            def int(self):
                return self

            def cpu(self):
                return self

            def tolist(self):
                return self.value

        class Detector:
            names = {2: 'car'}

            def __init__(self, weights):
                self.index = 0

            def track(self, frame, **kwargs):
                bottom = 20 + self.index * 5
                self.index += 1
                boxes = types.SimpleNamespace(id=Tensor([7]), xyxy=Tensor([[20, bottom - 10, 40, bottom]]))
                return [types.SimpleNamespace(boxes=boxes, plot=lambda: frame.copy())]

        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'input.avi'
            writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*'MJPG'), 10, (64, 64))
            self.assertTrue(writer.isOpened())
            for _ in range(8):
                writer.write(np.full((64, 64, 3), 128, dtype=np.uint8))
            writer.release()
            with patch.dict(sys.modules, {'ultralytics': types.SimpleNamespace(YOLO=Detector)}):
                first, video = track_crossings(source, ((0, 35), (63, 35)), output_dir=folder)
                second, other_video = track_crossings(source, ((0, 35), (63, 35)), output_dir=folder)
            self.assertEqual(first, second)
            self.assertNotEqual(video, other_video)
            self.assertEqual(len(first), 1)
            self.assertEqual(first[0]['time_seconds'], 0.3)
            self.assertEqual(len(first[0]['crop_paths']), 3)
            for relative in first[0]['crop_paths']:
                self.assertTrue((video.parent / relative).is_file())
            with (video.parent / 'crossings.csv').open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(json.loads(rows[0]['crop_paths']), first[0]['crop_paths'])
            summary = json.loads((video.parent / 'summary.json').read_text())
            self.assertEqual(summary['frames_processed'], 8)
            cap = cv2.VideoCapture(str(video))
            self.assertTrue(cap.read()[0])
            cap.release()
            empty_boxes = types.SimpleNamespace(id=None)
            with patch.object(Detector, 'track', side_effect=lambda frame, **kwargs: [
                types.SimpleNamespace(boxes=empty_boxes, plot=lambda: frame.copy())
            ]), patch.dict(sys.modules, {'ultralytics': types.SimpleNamespace(YOLO=Detector)}):
                empty, empty_video = track_crossings(source, ((0, 35), (63, 35)), output_dir=folder)
            self.assertEqual(empty, [])
            with (empty_video.parent / 'crossings.csv').open() as handle:
                self.assertEqual(list(csv.DictReader(handle)), [])
            before = set(Path(folder).glob('crossings-*'))
            with patch.dict(sys.modules, {'ultralytics': types.SimpleNamespace(YOLO=Detector)}), patch.object(cv2, 'imwrite', return_value=False):
                with self.assertRaises(RuntimeError):
                    track_crossings(source, ((0, 35), (63, 35)), output_dir=folder)
            failed = (set(Path(folder).glob('crossings-*')) - before).pop()
            self.assertFalse((failed / 'summary.json').exists())


if __name__ == '__main__':
    unittest.main()
