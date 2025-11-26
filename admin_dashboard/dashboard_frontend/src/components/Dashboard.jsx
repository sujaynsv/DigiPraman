// import { useState, useEffect, useMemo } from 'react';
// import { getStats, testConnection } from '../api/axios';
// import './Dashboard.css';

// const numberFormatter = new Intl.NumberFormat('en-IN');

// function Dashboard() {
//   const [stats, setStats] = useState(null);
//   const [connectionStatus, setConnectionStatus] = useState('Testing connection…');
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     checkConnection();
//     loadStats();
//   }, []);

//   const checkConnection = async () => {
//     try {
//       const response = await testConnection();
//       setConnectionStatus(`Connected · ${response.data.message}`);
//     } catch (error) {
//       setConnectionStatus(`Offline · ${error.message}`);
//     }
//   };

//   const loadStats = async () => {
//     try {
//       setLoading(true);
//       const response = await getStats();
//       setStats(response.data);
//     } catch (error) {
//       console.error('Error loading stats:', error);
//       setStats(null);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const verificationCards = useMemo(() => {
//     if (!stats) return [];

//     const cards = [
//       {
//         key: 'pending_review',
//         label: 'Pending Review',
//         value:
//           stats.pending_review ??
//           stats.verification_pending ??
//           stats.total_pending ??
//           null,
//         change: stats.pending_review_change ?? null,
//         accent: 'info',
//       },
//       {
//         key: 'approved',
//         label: 'Approved',
//         value: stats.approved ?? stats.total_approved ?? null,
//         change: stats.approved_change ?? null,
//         accent: 'success',
//       },
//       {
//         key: 'flagged',
//         label: 'Flagged',
//         value: stats.flagged ?? stats.total_flagged ?? null,
//         change: stats.flagged_change ?? null,
//         accent: 'warning',
//       },
//       {
//         key: 'rejected',
//         label: 'Rejected',
//         value: stats.rejected ?? stats.total_rejected ?? null,
//         change: stats.rejected_change ?? null,
//         accent: 'error',
//       },
//     ].filter((card) => card.value !== null);

//     if (cards.length) {
//       return cards;
//     }

//     return [
//       { label: 'Organizations', value: stats.total_organizations ?? 0, accent: 'neutral' },
//       { label: 'Users', value: stats.total_users ?? 0, accent: 'neutral' },
//       { label: 'Beneficiaries', value: stats.total_beneficiaries ?? 0, accent: 'neutral' },
//       { label: 'Schemes', value: stats.total_schemes ?? 0, accent: 'neutral' },
//     ];
//   }, [stats]);

//   const riskRows = useMemo(() => {
//     if (!stats?.risk_distribution) return [];

//     const risk = stats.risk_distribution;
//     const normalize = (entry) => ({
//       count: entry?.count ?? entry?.value ?? entry ?? 0,
//       percentage: entry?.percentage ?? entry?.percent ?? null,
//     });

//     return [
//       { label: 'Low Risk', color: 'low', ...normalize(risk.low) },
//       { label: 'Medium Risk', color: 'medium', ...normalize(risk.medium) },
//       { label: 'High Risk', color: 'high', ...normalize(risk.high) },
//     ].filter((row) => row.count > 0 || row.percentage !== null);
//   }, [stats]);

//   const recentApplications = stats?.recent_applications ?? [];
//   const connectionOk = connectionStatus.startsWith('Connected');

//   const formatNumber = (value) => numberFormatter.format(value ?? 0);

//   return (
//     <div className="dashboard">
//       <header className="dashboard-header">
//         <div>
//           <p className="eyebrow">Loan verification overview</p>
//           <h1>Dashboard</h1>
//         </div>
//         <div className={`connection-pill ${connectionOk ? 'online' : 'offline'}`}>
//           {connectionStatus}
//         </div>
//       </header>

//       {loading ? (
//         <div className="loading">Loading latest insights…</div>
//       ) : !stats ? (
//         <div className="error">Unable to load statistics. Please try again.</div>
//       ) : (
//         <>
//           <section className="verification-cards">
//             {verificationCards.map((card) => {
//               const numericChange =
//                 typeof card.change === 'number'
//                   ? card.change
//                   : Number(String(card.change ?? '').replace(/[^0-9.-]/g, ''));
//               const hasChange = card.change !== null && !Number.isNaN(numericChange);
//               const changeLabel = hasChange
//                 ? `${numericChange > 0 ? '+' : ''}${numericChange}%`
//                 : card.change;

//               return (
//                 <article className={`metric-card ${card.accent}`} key={card.label}>
//                   <div className="metric-label">{card.label}</div>
//                   <div className="metric-value">{formatNumber(card.value)}</div>
//                   {card.change !== null && (
//                     <div className={`metric-trend ${hasChange && numericChange < 0 ? 'down' : 'up'}`}>
//                       {hasChange && numericChange < 0 ? '▼' : '▲'} {changeLabel} from last week
//                     </div>
//                   )}
//                 </article>
//               );
//             })}
//           </section>

//           <section className="dashboard-content">
//             <article className="panel recent-panel">
//               <div className="panel-header">
//                 <div>
//                   <h2>Recent Applications</h2>
//                   <p>Latest submissions synced from the core tables</p>
//                 </div>
//               </div>
//               {recentApplications.length ? (
//                 <ul className="applications-list">
//                   {recentApplications.map((app) => (
//                     <li key={app.id ?? app.application_id} className="application-item">
//                       <div>
//                         <p className="applicant-name">{app.applicant_name ?? app.name ?? '—'}</p>
//                         <p className="application-id">{app.application_id ?? app.reference_id ?? 'ID unavailable'}</p>
//                       </div>
//                       <div className="application-meta">
//                         <span className={`risk-badge ${app.risk_level?.toLowerCase() ?? 'medium'}`}>
//                           {app.risk_level ?? 'Review'}
//                         </span>
//                         {app.loan_amount && (
//                           <p className="application-amount">₹{formatNumber(app.loan_amount)}</p>
//                         )}
//                       </div>
//                     </li>
//                   ))}
//                 </ul>
//               ) : (
//                 <div className="empty-state">No applications synced yet.</div>
//               )}
//             </article>

//             <article className="panel risk-panel">
//               <div className="panel-header">
//                 <div>
//                   <h2>Risk Distribution</h2>
//                   <p>Breakdown of current application cohorts</p>
//                 </div>
//               </div>
//               {riskRows.length ? (
//                 <div className="risk-list">
//                   {riskRows.map((row) => (
//                     <div className="risk-row" key={row.label}>
//                       <div className="risk-row-header">
//                         <span>{row.label}</span>
//                         <span>
//                           {formatNumber(row.count)}
//                           {row.percentage !== null && ` (${row.percentage}%)`}
//                         </span>
//                       </div>
//                       <div className="risk-bar">
//                         <div
//                           className={`risk-bar-value ${row.color}`}
//                           style={{ width: `${Math.min(row.percentage ?? 100, 100)}%` }}
//                         />
//                       </div>
//                     </div>
//                   ))}
//                 </div>
//               ) : (
//                 <div className="empty-state">Risk insights will appear once data is available.</div>
//               )}
//             </article>
//           </section>
//         </>
//       )}

//       <button onClick={loadStats} className="refresh-btn">
//         Refresh Data
//       </button>
//     </div>
//   );
// }

// export default Dashboard;







import { useState, useEffect, useMemo } from 'react';
import { getStats, testConnection } from '../api/axios';
import './Dashboard.css';

const numberFormatter = new Intl.NumberFormat('en-IN');

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Testing connection…');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkConnection();
    loadStats();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await testConnection();
      setConnectionStatus(`Connected · ${response.data.message}`);
    } catch (error) {
      setConnectionStatus(`Offline · ${error.message}`);
    }
  };

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  /* ====== METRIC CARDS ====== */
  // const verificationCards = useMemo(() => {

  //   if (!stats) return [];

  //   return [
  //     {
  //       key: 'pending',
  //       label: 'Pending Review',
  //       value: stats.pending_review,
  //       change: stats.pending_review_change,
  //       accent: 'info',
  //     },
  //     {
  //       key: 'approved',
  //       label: 'Approved',
  //       value: stats.approved,
  //       change: stats.approved_change,
  //       accent: 'success',
  //     },
  //     {
  //       key: 'flagged',
  //       label: 'Flagged',
  //       value: stats.flagged,
  //       change: stats.flagged_change,
  //       accent: 'warning',
  //     },
  //     {
  //       key: 'rejected',
  //       label: 'Rejected',
  //       value: stats.rejected,
  //       change: stats.rejected_change,
  //       accent: 'error',
  //     },
  //   ];
  // }, [stats]);


  const verificationCards = useMemo(() => {
  if (!stats) return [];

  return [
    {
      key: 'verification_pending',
      label: 'Verification Pending',
      value: stats.verification_pending ?? 0,
      change: stats.verification_pending_change ?? 0,
      accent: 'info',
    },
    {
      key: 'approved',
      label: 'Approved',
      value: stats.approved,
      change: stats.approved_change,
      accent: 'success',
    },
    {
      key: 'flagged',
      label: 'Flagged',
      value: stats.flagged,
      change: stats.flagged_change,
      accent: 'warning',
    },
    {
      key: 'rejected',
      label: 'Rejected',
      value: stats.rejected,
      change: stats.rejected_change,
      accent: 'error',
    },
  ];
}, [stats]);

  /* ====== RISK DISTRIBUTION ====== */
  const riskRows = useMemo(() => {
    if (!stats?.risk_distribution) return [];

    return [
      {
        label: 'Low Risk',
        color: 'low',
        count: stats.risk_distribution.low.count,
        percentage: stats.risk_distribution.low.percentage,
      },
      {
        label: 'Medium Risk',
        color: 'medium',
        count: stats.risk_distribution.medium.count,
        percentage: stats.risk_distribution.medium.percentage,
      },
      {
        label: 'High Risk',
        color: 'high',
        count: stats.risk_distribution.high.count,
        percentage: stats.risk_distribution.high.percentage,
      },
    ];
  }, [stats]);

  const recentApplications = stats?.recent_applications || [];
  const connectionOk = connectionStatus.startsWith('Connected');

  const formatNumber = (value) => numberFormatter.format(value ?? 0);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Loan verification overview</p>
          <h1>Dashboard</h1>
        </div>
        <div className={`connection-pill ${connectionOk ? 'online' : 'offline'}`}>
          {connectionStatus}
        </div>
      </header>

      {loading ? (
        <div className="loading">Loading latest insights…</div>
      ) : !stats ? (
        <div className="error">Unable to load statistics.</div>
      ) : (
        <>
          {/* ==== METRIC CARDS ==== */}
          <section className="verification-cards">
            {verificationCards.map((card) => {
              const change = card.change;

              return (
                <article className={`metric-card ${card.accent}`} key={card.key}>
                  <div className="metric-label">{card.label}</div>
                  <div className="metric-value">{formatNumber(card.value)}</div>
                  {change !== null && (
                    <div className={`metric-trend ${change < 0 ? 'down' : 'up'}`}>
                      {change < 0 ? '▼' : '▲'} {Math.abs(change)}% from last week

                    </div>
                  )}
                </article>
              );
            })}
          </section>

          <section className="dashboard-content">
            {/* ==== RECENT APPLICATIONS ==== */}
            <article className="panel recent-panel">
              <div className="panel-header">
                <h2>Recent Applications</h2>
              </div>

              <ul className="applications-list">
                {recentApplications.map((app) => (
                  <li key={app.application_id} className="application-item">
                    <div>
                      <p className="applicant-name">{app.applicant_name}</p>
                      <p className="application-id">{app.loan_ref_no}</p>
                    </div>

                    <div className="application-meta">
                      <span className={`risk-badge ${app.risk_tier.toLowerCase()}`}>
                        {app.risk_tier}
                      </span>
                      <p className="application-amount">
                        ₹{formatNumber(app.loan_amount)}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </article>

            {/* ==== RISK DISTRIBUTION ==== */}
            <article className="panel risk-panel">
              <div className="panel-header">
                <h2>Risk Distribution</h2>
              </div>

              <div className="risk-list">
                {riskRows.map((row) => (
                  <div className="risk-row" key={row.label}>
                    <div className="risk-row-header">
                      <span>{row.label}</span>
                      <span>
                        {formatNumber(row.count)} ({row.percentage}%)
                      </span>
                    </div>
                    <div className="risk-bar">
                      <div
                        className={`risk-bar-value ${row.color}`}
                        style={{ width: `${row.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>
        </>
      )}

      <button onClick={loadStats} className="refresh-btn">
        Refresh Data
      </button>
    </div>
  );
}

export default Dashboard;
