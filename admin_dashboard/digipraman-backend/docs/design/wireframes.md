# Wireframe Notes

## Beneficiary Home

- Top card greets the beneficiary and shows the most urgent verification with a status pill (e.g., "Pending capture") and due date.
- Cards list scheme name, sanctioned amount, risk tier placeholder, and a CTA button "Continue capture".
- Offline banner appears when the device is not connected, alongside a sync icon showing queued uploads.
- Floating Capture button opens the guided evidence flow and displays the number of pending artefacts.

## Capture Flow

- Stepper with four steps: Photo, Video, Documents, Review.
- Each capture step shows GPS lock indicator, timestamp, and quality meter. The capture button is disabled until GPS lock or minimum quality is achieved.
- Thumbnails appear immediately with status (pending upload / uploaded). Users can delete or retake before submission.
- Review screen summarizes collected artefacts, shows total size queued for upload, and provides a "Sync later" toggle.

## Officer Case View

- Left column: loan + beneficiary metadata, map widget highlighting evidence GPS points (leveraging PostGIS), and AI summary badges for each VIDYA layer.
- Center: evidence carousel with filters for photos/videos/docs plus inline AI annotations (blur score, detected asset tags, OCR extracted values).
- Right column: "VIDYA Flags" list grouped by layer, recommended action, and routing tier thresholds with ability to override.
- Footer contains decision buttons (Approve, Reject, Request More, Video) and audit log preview to maintain traceability.
