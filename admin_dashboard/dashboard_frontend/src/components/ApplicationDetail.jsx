import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "../components/ApplicationDetail.css";
import api from "../api/axios";

export default function ApplicationDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [showEvidenceDebug, setShowEvidenceDebug] = useState(false);
  const [activeTab, setActiveTab] = useState("details");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApplication();
  }, []);

  const fetchApplication = async () => {
    try {
      const res = await api.get(`/applications/${id}`);
      const payload = res.data || {};

      // 🔍 High‑signal debug
      console.groupCollapsed("🔍 /applications/:id payload", id);
      console.log("Full payload:", payload);
      console.log("payload.verification_evidence:", payload.verification_evidence);
      console.log("payload.evidence:", payload.evidence);
      console.groupEnd();

      const app = payload.application || payload;
      setData(app);

      const ev =
        payload.verification_evidence ||
        app.verification_evidence ||
        payload.evidence ||
        app.evidence ||
        [];

      // 🔍 Debug per evidence item and base64 presence
      console.groupCollapsed("🔍 Resolved evidence array");
      console.log("Raw evidence array:", ev);
      if (Array.isArray(ev)) {
        ev.forEach((item, idx) => {
          const hasFileName = typeof item.file_name === "string" && item.file_name.length > 0;
          console.log(`[#${idx}] id=${item.id ?? "n/a"}`, {
            keys: Object.keys(item),
            file_name_present: hasFileName,
            file_name_sample: hasFileName ? item.file_name.slice(0, 30) + "..." : null,
          });
        });
      } else {
        console.log("Evidence is not an array:", ev);
      }
      console.groupEnd();

      setEvidence(Array.isArray(ev) ? ev : []);
    } catch (err) {
      console.error("Error fetching details:", err);
    } finally {
      setLoading(false);
    }
  };

  // helper: wrap base64 string into data URL
  const base64ToImgSrc = (maybeBase64, mime = "image/jpeg") => {
    if (!maybeBase64) return null;
    // if already a full data URL
    if (maybeBase64.startsWith("data:image")) return maybeBase64;
    return `data:${mime};base64,${maybeBase64}`;
  };

  // 🔥 Update Status API
  const handleAction = async (action) => {
    try {
      const res = await api.post(`/applications/${id}/status`, { action });
      const newStatus =
        res.data.status ||
        res.data.lifecycle_status ||
        data?.lifecycle_status ||
        data?.status;

      setData((prev) => ({
        ...prev,
        status: newStatus,
        lifecycle_status: newStatus,
      }));

      alert(`Status updated to: ${newStatus}`);
    } catch (err) {
      console.error("Update failed:", err);
      alert("Failed to update status");
    }
  };

  if (loading) return <h2 style={{ textAlign: "center" }}>Loading...</h2>;
  if (!data)
    return (
      <h2 style={{ textAlign: "center", color: "red" }}>
        Unable to load application details
      </h2>
    );

  const status = (data.status || data.lifecycle_status || "").toLowerCase();
  const riskTier = (data.risk_tier || "Medium").toLowerCase();
  const riskJson = data.risk_score_json || {};
  const showActions = !["approved", "rejected"].includes(status);

  return (
    <div className="app-detail-container">
      {/* Header */}
      <div className="app-header-row">
        <h1>{data.loan_ref_no}</h1>
        <span className={`risk-badge ${riskTier}`}>
          {(data.risk_tier || "Medium").charAt(0).toUpperCase() +
            (data.risk_tier || "Medium").slice(1)}{" "}
          Risk
        </span>
      </div>

      {/* beneficiary may not exist as nested object; keep fallback */}
      <p className="beneficiary-name">
        {data.beneficiary?.name || data.beneficiary_name || "Unknown"}
      </p>

      {/* Summary Cards */}
      <div className="app-summary-grid">
        <div className="card-box">
          <label>Loan Amount</label>
          <h3>
            ₹
            {data.sanctioned_amount ??
              data.disbursed_amount ??
              data.loan_amount ??
              "-"}
          </h3>
          <p>{data.loan_type}</p>
        </div>

        <div className="card-box">
          <label>Risk Score</label>
          <h3>
            {riskJson.score ? `${riskJson.score}/100` : "N/A/100"}
          </h3>
        </div>

        <div className="card-box">
          <label>Contact</label>
          <h3>{data.beneficiary?.mobile || data.mobile || "-"}</h3>
          <p>{data.beneficiary?.email || data.email || "-"}</p>
        </div>

        <div className="card-box">
          <label>Submitted</label>
          <h3>
            {(data.submitted_at || data.created_at || "")
              .toString()
              .split("T")[0] || "-"}
          </h3>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-buttons">
        {["details", "evidence", "risk", "history"].map((tab) => (
          <button
            key={tab}
            className={activeTab === tab ? "active" : ""}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* ---------- DETAILS TAB ---------- */}
      {activeTab === "details" && (
        <div className="tab-section">
          <h3>Application Details</h3>
          <p>
            <strong>Beneficiary:</strong>{" "}
            {data.beneficiary?.name || data.beneficiary_name || "-"}
          </p>
          <p>
            <strong>Mobile:</strong>{" "}
            {data.beneficiary?.mobile || data.mobile || "-"}
          </p>
          <p>
            <strong>Email:</strong>{" "}
            {data.beneficiary?.email || data.email || "-"}
          </p>
          <p>
            <strong>Loan Type:</strong> {data.loan_type || "-"}
          </p>
          <p>
            <strong>Amount:</strong> ₹
            {data.sanctioned_amount ??
              data.disbursed_amount ??
              data.loan_amount ??
              "-"}
          </p>
          <p>
            <strong>Status:</strong> {data.status || data.lifecycle_status || "-"}
          </p>
          <p>
            <strong>Purpose:</strong> {data.purpose || "N/A"}
          </p>
        </div>
      )}

      {/* ---------- EVIDENCE TAB ---------- */}
      {activeTab === "evidence" && (
        <div className="tab-section">
          <h3>Evidence</h3>

          {/* small runtime indicator about what we see */}
          <p style={{ fontSize: 12, color: "#6b7280", marginBottom: 4 }}>
            Evidence items: {Array.isArray(evidence) ? evidence.length : 0}
          </p>

          <button
            type="button"
            style={{ marginBottom: 8, fontSize: 12 }}
            onClick={() => setShowEvidenceDebug((v) => !v)}
          >
            {showEvidenceDebug ? "Hide" : "Show"} evidence debug
          </button>
          {showEvidenceDebug && (
            <pre
              style={{
                maxHeight: 200,
                overflow: "auto",
                fontSize: 11,
                background: "#111",
                color: "#0f0",
                padding: 8,
                borderRadius: 4,
                marginBottom: 8,
              }}
            >
              {JSON.stringify(evidence, null, 2)}
            </pre>
          )}

          {(!evidence || evidence.length === 0) && (
            <p className="no-evidence">
              No evidence array found on /applications/:id response.
            </p>
          )}

          <div className="evidence-grid">
            {evidence.map((item, index) => {
              // file_name is the base64-encoded string per your description
              const base64Raw =
                item.file_name || // ← main source (DB column)
                item.base64 ||
                item.base64_data ||
                null;

              const mime =
                item.file_type ||
                item.mime_type ||
                item.mimetype ||
                item.content_type ||
                "image/jpeg";

              const imgSrc = base64ToImgSrc(base64Raw, mime);

              if (!imgSrc) {
                console.warn(
                  "Evidence item has no usable base64 in file_name/base64/base64_data",
                  item
                );
                return null;
              }

              const label = item.display_name || item.id || `evidence-${index + 1}`;

              return (
                <div key={item.id || index} className="evidence-card">
                  <img
                    src={imgSrc}
                    alt={label}
                    onClick={() => window.open(imgSrc)}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ---------- RISK TAB ---------- */}
      {activeTab === "risk" && (
        <div className="tab-section">
          <h3>Risk Analysis</h3>
          <p>
            <strong>Risk Score:</strong> {riskJson.score || "N/A"}
          </p>
          <p>
            <strong>Tier:</strong> {data.risk_tier || "Medium"}
          </p>

          <pre className="risk-json">
            {JSON.stringify(riskJson.breakdown || riskJson, null, 2)}
          </pre>
        </div>
      )}

      {/* ---------- HISTORY TAB ---------- */}
      {activeTab === "history" && (
        <div className="tab-section">
          <h3>History</h3>
          <p>Timeline logs will appear here.</p>
        </div>
      )}

      {/* ---------- ACTION BUTTONS ---------- */}
      <div className="action-buttons">
        {/* Buttons shown only when not already finalized */}
        {showActions && (
          <>
            <button
              className="approve"
              onClick={() => handleAction("approve")}
            >
              Approve
            </button>
            <button
              className="request"
              onClick={() => handleAction("needs_more")}
            >
              Request More Info
            </button>
            <button
              className="reject"
              onClick={() => handleAction("reject")}
            >
              Reject
            </button>
          </>
        )}

        {/* Show schedule meeting only when application is rejected */}
        {status === "rejected" && (
          <button
            style={{
              background: "#6c63ff",
              color: "#fff",
              padding: "10px 18px",
              borderRadius: "8px",
              marginLeft: "10px",
              fontWeight: "600",
            }}
            onClick={async () => {
              try {
                const meetingUrl = `https://meet.jit.si/LoanRoom-${data.id}`;
                await api.post("/applications/schedule-meet", {
                  app_id: data.id,
                  mobile: data.beneficiary?.mobile || data.mobile,
                  link: meetingUrl,
                });
                alert("Meeting scheduled & SMS sent!");
              } catch {
                alert("Failed to send SMS");
              }
            }}
          >
            Schedule Meeting 📩
          </button>
        )}

        {/* High risk applicant → enable immediate video verification */}
        {riskTier === "high" && (
          <button
            onClick={() => window.open(`/jitsi/${data.id}`, "_blank")}
            className="video-btn"
            style={{
              background: "red",
              color: "#fff",
              padding: "10px 18px",
              borderRadius: "8px",
              marginLeft: "10px",
              fontWeight: "600",
            }}
          >
            Start Video Verification 🔴
          </button>
        )}
      </div>
    </div>
  );
}