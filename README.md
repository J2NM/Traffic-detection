# Vehicle detection, tracking and counting in video

AAI-521 Team 2 will detect and track cars in recorded video. The notebook will report how many cars cross a designated line and break that total down by category. The first breakdown will be by body color. Vehicle type is a possible future extension. We will compare both the overall count and the category counts with an independent human tally.

## Planned notebook

1. Open the video in Colab, preview a frame, and place a counting line across the road.
2. Detect cars with YOLO and follow each car across frames with a tracker.
3. Record each track at its first line crossing. Give Cosmos Reason 2 cropped views of the car to estimate its body color. Use **uncertain** when the color is unclear.
4. Export an annotated video, a CSV with one row per crossing, and a summary showing the overall count and counts by color.

## Evaluation

Reserve a clip or a separate time segment before tuning. A reviewer will log each crossing time and color independently. Match those observations to predicted crossings to report missed cars, extra counts, and color accuracy for matched cars with readable colors.

## Team

| Member | Responsibility |
| --- | --- |
| Tushar Kummar | Select and load footage, document the split, define color labels and compare a simple baseline with Cosmos Reason 2. Attach a color label to each track ID. |
| Obinna Edeh | Detect and track cars with YOLO, count first crossings and export the annotated video plus a crossing log with track IDs, timestamps and crop references. |
| Juan Norena | Independently label the evaluation clip, compare predictions with manual counts and produce overall totals, color breakdowns and error charts. |

The first milestone is to select the footage and agree on the line position and color labels. Keep videos, downloaded weights and generated outputs outside version control.

## Module 4 assignment checklist

This checklist follows the Team Assignment 4.1 Project Status Update Form. The separate grading rubric and point values are pending confirmation.

| Form section | What Team 2 will deliver | Owner and status |
| --- | --- | --- |
| Team information | List all three members, designate the representative, and include the repository and shared Drive folder links. The representative submits the completed form through the Module 4 group assignment link. | Team decision pending on representative and Drive link. |
| Project description | State the research question, input video, first-crossing rule, overall and category counts and comparison with a human tally. | Team reviews the scope documented above. |
| Selected dataset | Record dataset name, source link, usage terms, clip count, duration, resolution, frame rate and file size. Report labeled crossings per color. | Tushar. Footage selection pending. |
| Data provenance and prior use | Describe the camera view, known edits or crops and any preprocessing. Cite documented prior uses and identify unknowns. | Tushar. Complete after selecting footage. |
| Feature extraction and data quality | Describe how detections become tracks and how cropped views yield one color per crossing. Explain how glare, occlusion and unreadable paint affect labels. | Obinna documents detection and tracking. Tushar documents color classification and footage quality. |
| Responsibilities and roadblocks | Confirm individual contributions and record open decisions about footage, line placement and color labels. | All three members review before submission. |

## Implementation and final deliverables

These are planned project outputs. The first milestone is a manually labeled clip that everyone can use to check the notebook.

| Deliverable | Owner | Task |
| --- | --- | --- |
| Prepared footage and dataset split | Tushar Kummar | Select the footage, load it from Drive and document the split. |
| Color labels for tracked cars | Tushar Kummar | Define color labels, compare a simple baseline with Cosmos Reason 2 and attach one color label to each track ID. |
| Annotated video and crossing log | Obinna Edeh | Detect and track cars with YOLO. Count each track at its first crossing and export the video and log with track IDs, timestamps and crop references. |
| Manual tally and evaluation results | Juan Norena | Independently label the evaluation clip and compare predictions with the manual counts. |
| Count tables and error charts | Juan Norena | Report the overall count and color breakdown, then chart counting and classification errors. |
| Data and color classification sections | Tushar Kummar | Write the corresponding notebook section, report text and slides. |
| Detection, tracking and counting sections | Obinna Edeh | Write the corresponding notebook section, report text and slides. |
| Evaluation and reporting sections | Juan Norena | Write the corresponding notebook section, report text and slides. |

## Change log

- 2026-11-15: Documented project scope, team responsibilities and evaluation plans, and added ignore rules for local data and outputs.
- 2026-11-15: Mapped the Module 4 status form to team deliverables, owners and review criteria.
- 2026-11-15: Clarified overall car counts and category breakdowns in the project scope and evaluation.
- 2026-11-15: Redistributed notebook sections, model experiments and reporting across the three team members.
- 2026-11-15: Matched the deliverable, owner and task table to the Word status form.
