# Demo Script (6–6.5 minutes)

## Segment 1 – Problem + Overview (0:00–1:00)

- Hook: "Loan utilization checks still take weeks; DigiPraman closes the loop in a single visit." (15s)
- Slide: ecosystem diagram (mobile + VIDYA AI + officer + admin). (25s)
- Transition: "Let’s walk through a beneficiary submission all the way to an officer decision." (20s)

## Segment 2 – Beneficiary Offline Capture (1:00–2:15)

- Start mobile app in airplane mode, show queued verification card (C2). (20s)
- Capture photo → show GPS lock + timestamp overlay. (25s)
- Capture invoice doc, highlight realtime quality meter + OCR preview. (30s)
- Explain offline queue indicator + "Sync later" toggle. (20s)

## Segment 3 – Sync + VIDYA AI (2:15–3:15)

- Turn connectivity on; watch sync spinner complete. (20s)
- Show backend log or Postman call to `/ai/analyze` returning risk JSON (projected). (25s)
- Narrate risk score 72 → "officer review" with flags (amount mismatch, GPS drift). (15s)

## Segment 4 – Officer Review (3:15–4:30)

- Switch to officer portal medium-risk queue, open case C2. (20s)
- Walk through evidence carousel, map with PostGIS pins. (25s)
- Highlight VIDYA explanations per layer, add context on weights. (20s)
- Record decision "Approve with caution" or "Request more"; show audit log entry. (20s)

## Segment 5 – High-Risk + Video (4:30–5:15)

- Open case C3 (score 88). Show video-required banner + quick WebRTC join. (25s)
- Mention tamper/duplicate detection and why human validation still needed. (20s)

## Segment 6 – Admin + Wrap (5:15–6:00)

- Export compliance log `/reports/compliance`. (15s)
- Show threshold configurator referencing `risk_rules.json`. (15s)
- Conclude with KPI summary + next steps (API integrations, scale testing). (15s)

## Backup Notes

- Keep pre-recorded AI response payloads (`docs/ai/sample_risk_analysis.json`) for the narrator in case live service lags.
- Have SMS/WhatsApp notification stubs ready to trigger via Postman.
