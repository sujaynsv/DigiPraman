import { useEffect, useMemo, useState } from 'react';
import { getApplications } from '../api/axios';
import './Applications.css';

const LIMIT = 100;

const STATUS_FILTERS = [
  { value: 'all', label: 'All Status' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'auto-approved', label: 'Auto-Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'video-required', label: 'Video-Required' },
];

const RISK_FILTERS = [
  { value: 'all', label: 'All Risk Levels' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
];

const numberFormatter = new Intl.NumberFormat('en-IN');

const formatCurrency = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—';
  }
  return `₹${numberFormatter.format(Number(value))}`;
};

const formatDate = (value) => {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

const resolveRiskLevel = (riskScore, fallback) => {
  if (fallback) return fallback.toLowerCase();
  if (!Number.isFinite(riskScore)) return 'medium';
  if (riskScore < 40) return 'low';
  if (riskScore <= 70) return 'medium';
  return 'high';
};

function Applications() {
  const [filters, setFilters] = useState({ search: '', status: 'all', risk: 'all' });
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [applications, setApplications] = useState([]);
  const [meta, setMeta] = useState({ total: 0, limit: LIMIT });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedSearch(filters.search.trim()), 350);
    return () => clearTimeout(handler);
  }, [filters.search]);

  useEffect(() => {
    fetchApplications();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch, filters.status, filters.risk]);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      setError('');

      const params = { limit: LIMIT };
      if (debouncedSearch) params.search = debouncedSearch;
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.risk !== 'all') params.risk_level = filters.risk;

      const response = await getApplications(params);
      const payload = response.data;
      const records = payload?.items ?? payload?.data ?? payload ?? [];
      const total = payload?.total ?? payload?.count ?? records.length;

      setApplications(Array.isArray(records) ? records : []);
      setMeta({ total, limit: params.limit });
    } catch (err) {
      console.error('Error fetching applications:', err);
      setError('Unable to load applications from the server.');
      setApplications([]);
    } finally {
      setLoading(false);
    }
  };

  const normalizedApplications = useMemo(
    () =>
      applications.map((app, index) => {
        const riskScore = Number(
          app.risk_score ?? app.risk?.score ?? app.risk_score_value
        );
        const riskLevel = resolveRiskLevel(riskScore, app.risk_level ?? app.risk?.level);
        const status = String(app.status ?? 'Pending').toLowerCase();

        return {
          key: app.id ?? app.application_id ?? `row-${index}`,
          applicationId: app.application_id ?? app.reference_id ?? app.id ?? '—',
          beneficiary:
            app.beneficiary_name ??
            app.applicant_name ??
            app.name ??
            app.user?.full_name ??
            'Unknown',
          beneficiaryId: app.beneficiary_identifier ?? app.user?.id ?? app.user_id ?? '—',
          loanType: app.loan_type ?? app.loan?.type ?? '—',
          amount: formatCurrency(app.loan_amount ?? app.amount ?? app.loan?.amount),
          riskScore: Number.isFinite(riskScore) ? riskScore : '—',
          riskLevel,
          status,
          statusLabel: (app.status_label ?? app.status ?? 'Pending').replace(/_/g, '-'),
          submitted: formatDate(app.submitted_at ?? app.created_at ?? app.updated_at),
        };
      }),
    [applications]
  );

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <section className="applications">
      <header className="applications-header">
        <div>
          <p className="applications-subtitle">
            Showing {Math.min(meta.limit, normalizedApplications.length)} of {numberFormatter.format(meta.total)} applications
          </p>
          <h1>Applications</h1>
        </div>
        <button type="button" className="pill-button" onClick={fetchApplications}>
          Export
        </button>
      </header>

      <div className="applications-toolbar">
        <label htmlFor="application-search" className="input-wrapper">
          <span className="icon">🔍</span>
          <input
            id="application-search"
            type="search"
            placeholder="Search by name or ID..."
            value={filters.search}
            onChange={(event) => handleFilterChange('search', event.target.value)}
          />
        </label>
        <select
          className="select"
          value={filters.status}
          onChange={(event) => handleFilterChange('status', event.target.value)}
        >
          {STATUS_FILTERS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <select
          className="select"
          value={filters.risk}
          onChange={(event) => handleFilterChange('risk', event.target.value)}
        >
          {RISK_FILTERS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="applications-table">
        <div className="table-head">
          <span>Application ID</span>
          <span>Beneficiary</span>
          <span>Loan Type</span>
          <span>Amount</span>
          <span>Risk Score</span>
          <span>Status</span>
          <span>Submitted</span>
          <span />
        </div>
        {loading ? (
          <div className="table-state">Loading applications…</div>
        ) : error ? (
          <div className="table-state error">{error}</div>
        ) : normalizedApplications.length === 0 ? (
          <div className="table-state">No applications match the current filters.</div>
        ) : (
          <ul className="table-body">
            {normalizedApplications.map((row) => (
              <li key={row.key} className="table-row">
                <div>
                  <p className="cell-primary">{row.applicationId}</p>
                  <p className="cell-secondary">{row.beneficiaryId}</p>
                </div>
                <div>
                  <p className="cell-primary">{row.beneficiary}</p>
                </div>
                <div>
                  <p className="cell-primary">{row.loanType}</p>
                </div>
                <div>
                  <p className="cell-primary">{row.amount}</p>
                </div>
                <div>
                  <span className={`risk-chip ${row.riskLevel}`}>
                    {typeof row.riskScore === 'number' ? row.riskScore : row.riskLevel}
                  </span>
                </div>
                <div>
                  <span className={`status-chip ${row.status}`}>{row.statusLabel}</span>
                </div>
                <div>
                  <p className="cell-primary">{row.submitted}</p>
                </div>
                <div>
                    <button
                      className="view-link"
                      onClick={() => window.open(`/applications/${row.key}`, "_blank")}
                    >
                      View
                    </button>

                  </div>


              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

export default Applications;