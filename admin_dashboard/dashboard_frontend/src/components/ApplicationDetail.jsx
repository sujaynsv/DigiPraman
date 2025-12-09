import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "../components/ApplicationDetail.css";
import api from "../api/axios";

export default function ApplicationDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState("details");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApplication();
  }, []);

  const fetchApplication = async () => {
    try {
      const res = await api.get(`/applications/${id}`);
      setData(res.data);
    } catch (err) {
      console.error("Error fetching details:", err);
    } finally {
      setLoading(false);
    }
  };

  // 🔥 Update Status API
  const handleAction = async (action) => {
    try {
      const res = await api.post(`/applications/${id}/status`, { action });
      const newStatus = res.data.status;

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
  if (!data) return <h2 style={{ textAlign: "center", color: "red" }}>Unable to load application details</h2>;

  const status = (data.status || data.lifecycle_status || "").toLowerCase();
  const riskTier = (data.risk?.tier || "Medium").toLowerCase();
  const showActions = !["approved", "rejected"].includes(status);

  return (
    <div className="app-detail-container">

      {/* Header */}
      <div className="app-header-row">
        <h1>{data.loan_ref_no}</h1>
        <span className={`risk-badge ${riskTier}`}>
          {data.risk?.tier || "Medium"} Risk
        </span>
      </div>

      <p className="beneficiary-name">{data.beneficiary?.name}</p>

      {/* Summary Cards */}
      <div className="app-summary-grid">
        <div className="card-box">
          <label>Loan Amount</label>
          <h3>₹{data.loan_amount}</h3>
          <p>{data.loan_type}</p>
        </div>

        <div className="card-box">
          <label>Risk Score</label>
          <h3>{data.risk?.score ? `${data.risk.score}/100` : "N/A/100"}</h3>
        </div>

        <div className="card-box">
          <label>Contact</label>
          <h3>{data.beneficiary?.mobile}</h3>
          <p>{data.beneficiary?.email}</p>
        </div>

        <div className="card-box">
          <label>Submitted</label>
          <h3>{data.submitted_at?.split("T")[0] || "-"}</h3>
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
          <p><strong>Beneficiary:</strong> {data.beneficiary?.name}</p>
          <p><strong>Mobile:</strong> {data.beneficiary?.mobile}</p>
          <p><strong>Email:</strong> {data.beneficiary?.email}</p>
          <p><strong>Loan Type:</strong> {data.loan_type}</p>
          <p><strong>Amount:</strong> ₹{data.loan_amount}</p>
          <p><strong>Status:</strong> {data.status}</p>
          <p><strong>Purpose:</strong> {data.purpose || "N/A"}</p>
        </div>
      )}

      {/* ---------- EVIDENCE TAB ---------- */}
      {activeTab === "evidence" && (
        <div className="tab-section">
          <h3>Evidence</h3>

          {(!data.evidence || data.evidence.length === 0) && (
            <p className="no-evidence">No evidence uploaded</p>
          )}

          <div className="evidence-grid">
            {data.evidence?.map((item, index) => (
              <div key={index} className="evidence-card">
                {item.file_type?.includes("image") ? (
                  <img
                    src={item.base64}
                    alt="evidence"
                    onClick={() => window.open(item.base64)}
                  />
                ) : (
                  <a href={item.base64} download={item.file_name} target="_blank" rel="noreferrer">
                    📄 {item.file_name}
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ---------- RISK TAB ---------- */}
      {activeTab === "risk" && (
        <div className="tab-section">
          <h3>Risk Analysis</h3>
          <p><strong>Risk Score:</strong> {data.risk?.score || "N/A"}</p>
          <p><strong>Tier:</strong> {data.risk?.tier || "Medium"}</p>

          <pre className="risk-json">
            {JSON.stringify(data.risk?.breakdown, null, 2)}
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
  {status !== "approved" && status !== "rejected" && (
    <>
      <button className="approve" onClick={() => handleAction("approve")}>Approve</button>
      <button className="request" onClick={() => handleAction("needs_more")}>Request More Info</button>
      <button className="reject" onClick={() => handleAction("reject")}>Reject</button>
    </>
  )}

  {/* Show schedule meeting only when application is rejected */}
  {status === "rejected" && (
    <button
      style={{
        background:"#6c63ff",
        color:"#fff",
        padding:"10px 18px",
        borderRadius:"8px",
        marginLeft:"10px",
        fontWeight:"600"
      }}
      onClick={async () => {
        try {
          const meetingUrl = `https://meet.jit.si/LoanRoom-undefined`;
          await api.post("/applications/schedule-meet", {
            app_id: data.id,
            mobile: data.beneficiary?.mobile, // send mobile dynamically
            link: meetingUrl
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
        background:"red",
        color:"#fff",
        padding:"10px 18px",
        borderRadius:"8px",
        marginLeft:"10px",
        fontWeight:"600"
      }}
    >
      Start Video Verification 🔴
    </button>
  )}

</div>

    </div>
  );
}