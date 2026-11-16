# Counting cars by color in traffic video

AAI-521 Team 2 will use a traffic video from Google Drive to answer one question: How closely do automated counts by car color match an independent human tally?

## Planned notebook

1. Open the video in Colab, preview a frame, and place a counting line across the road.
2. Detect cars with YOLO and follow each car across frames with a tracker.
3. Record each track at its first line crossing. Give Cosmos Reason 2 cropped views of the car to estimate its body color. Use **uncertain** when the color is unclear.
4. Export an annotated video, a CSV with one row per crossing, and totals by color.

## Evaluation

Reserve a clip or a separate time segment before tuning. A reviewer will log each crossing time and color independently. Match those observations to predicted crossings to report missed cars, extra counts, and color accuracy for matched cars with readable colors.

## Team

| Member | Responsibility |
| --- | --- |
| Tushar Kummar | Select footage, document its source and prepare the data splits. |
| Obinna Edeh | Build the Colab notebook and run modeling experiments. |
| Juan Norena | Prepare the manual tally, evaluate predictions and review errors. |

The first milestone is to select the footage and agree on the line position and color labels. Keep videos, downloaded weights and generated outputs outside version control.

## Change log

- 2026-11-15: Documented project scope, team responsibilities and evaluation plans, and added ignore rules for local data and outputs.
