# Demo Dataset Plan

| Case ID | Scheme     | Scenario Highlights                       | Evidence Package                     | Expected Risk Score | Routing Tier       |
| ------- | ---------- | ----------------------------------------- | ------------------------------------ | ------------------- | ------------------ |
| C1      | Farm Mech  | Clean submission, GPS + timestamp perfect | 3 geo-tagged photos + vendor invoice | 42                  | Auto approve       |
| C2      | Farm Mech  | Invoice amount mismatch (12% higher)      | 2 photos + 1 invoice                 | 72                  | Officer review     |
| C3      | Dairy      | Low-light photo, GPS 18 km away           | 2 photos + 1 short video             | 88                  | Video verification |
| C4      | Dairy      | Duplicate receipt hash                    | 1 invoice (PNG) + POS slip           | 90                  | Video verification |
| C5      | MSME       | Clean POS slip, perfect metadata          | 4 photos + POS slip                  | 35                  | Auto approve       |
| C6      | MSME       | Device reuse detected across schemes      | 3 photos + 1 video                   | 77                  | Officer review     |
| C7      | Agri Infra | Timing anomaly (submitted midnight)       | 2 night photos + invoice             | 68                  | Officer review     |
| C8      | Agri Infra | Poor quality + blur + missing doc         | 1 blurry photo                       | 92                  | Video verification |
| C9      | Women SHG  | Historically flagged beneficiary          | 2 photos + invoice                   | 85                  | Officer review     |
| C10     | Women SHG  | Perfect submission for auto-approve demo  | 3 daylight photos                    | 33                  | Auto approve       |

## Evidence Storage Prep

- Host artefacts in an S3-compatible bucket using `loanId/case/evidenceType_timestamp.ext` naming.
- Maintain a manifest JSON per case capturing GPS (`Point` geojson), timestamp, checksum, and local file path for offline demos.
- Preload mobile app's offline store with C1, C2, and C3 to showcase sync behavior.

## Annotation Requirements

- Store VIDYA AI outputs (quality metrics, OCR text, hashes) per evidence item for replay during demos.
- Keep manual notes for officer narration (e.g., "highlight invoice mismatch"), referenced by `demo_script.md` checkpoints.
