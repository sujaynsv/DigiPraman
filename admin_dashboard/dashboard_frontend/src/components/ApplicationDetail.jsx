import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getApplicationDetail } from '../api/axios';
import './ApplicationDetail.css';

const numberFormatter = new Intl.NumberFormat('en-IN');

const formatCurrency = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—';
  }
  return `₹${numberFormatter.format(Number(value))}`;
};

const formatDate = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

function ApplicationDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError('');
        const res = await getApplicationDetail(id);
        setData(res.data);
      } catch (err) {
        console.error('Error loading application detail', err);
        setError('Unable to load application details.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return <div className="app-detail"><p>Loading application…</p></div>;
  }

  if (error || !data) {
    return <div className="app-detail"><p className="error">{error || 'Application not found.'}</p></div>;
  }

  const riskTier = data.risk?.tier || 'Medium';
  const riskScore = data.risk?.score;
  const breakdown = data.risk?.breakdown || [];

  return (
    <div className="app-detail">
      {/* Top bar with back + title */}
      <header className="app-detail-header">
        <div>
          <Link to="/applications" className="back-link">← Back to Applications</Link>
          <h1 className="app-detail-title">{data.loan_ref_no}</h1>
          <p className="app-detail-subtitle">{data.beneficiary_name}</p>
        </div>
        <div>
          <span className={`risk-pill ${riskTier.toLowerCase()}`}>{riskTier || 'Risk'}</span>
        </div>
      </header>

      {/* Summary cards */}
      <section className="app-detail-summary">
        <article className="summary-card">
          <h3>Loan Amount</h3>
          <p className="summary-value">{formatCurrency(data.sanctioned_amount)}</p>
          <p className="summary-caption">{data.loan_type || '—'}</p>
        </article>

        <article className="summary-card">
          <h3>Risk Score</h3>
          <p className="summary-value">
            {riskScore !== null && riskScore !== undefined ? `${riskScore}/100` : '—'}
          </p>
          <p className="summary-caption">{riskTier || 'Risk Category'}</p>
        </article>

        <article className="summary-card">
          <h3>Contact</h3>
          <p className="summary-value">{data.beneficiary_mobile || '—'}</p>
          <p className="summary-caption">{data.beneficiary_email || 'Contact details'}</p>
        </article>

        <article className="summary-card">
          <h3>Submitted</h3>
          <p className="summary-value">{formatDate(data.created_at)}</p>
          <p className="summary-caption">{data.lifecycle_status || 'Status'}</p>
        </article>
      </section>

      {/* Tabs bar – only Risk Analysis active for now */}
      <nav className="app-detail-tabs">
        <button className="tab-btn">Details</button>
        <button className="tab-btn">Evidence</button>
        <button className="tab-btn active">Risk Analysis</button>
        <button className="tab-btn">History</button>
      </nav>

      {/* Risk breakdown section */}
      <section className="app-detail-panel">
        <h2 className="panel-title">Risk Breakdown</h2>

        <div className="risk-breakdown-list">
          {breakdown.map((item) => (
            <div key={item.key} className="risk-breakdown-row">
              <div className="risk-breakdown-label">
                <span>{item.label}</span>
                <span>{item.score ?? 0}/100</span>
              </div>
              <div className="risk-breakdown-bar">
                <div
                  className="risk-breakdown-bar-value"
                  style={{ width: `${Math.min(item.score || 0, 100)}%` }}
                />
              </div>
            </div>
          ))}
          {breakdown.length === 0 && (
            <p className="empty-state">No risk breakdown available for this application.</p>
          )}
        </div>
      </section>

      {/* Actions */}
      <section className="app-detail-actions">
        <button className="primary-action">Approve</button>
        <button className="secondary-action">Request More Info</button>
        <button className="danger-action">Reject</button>
      </section>
    </div>
  );
}

export default ApplicationDetail;
