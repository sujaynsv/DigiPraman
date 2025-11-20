import { useState, useEffect } from 'react';
import { getStats, testConnection } from '../api/axios';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Testing...');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkConnection();
    loadStats();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await testConnection();
      setConnectionStatus(`✅ Connected: ${response.data.message}`);
    } catch (error) {
      setConnectionStatus(`❌ Connection failed: ${error.message}`);
    }
  };

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
      alert('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      {/* Connection Status */}
      <div className={`status-card ${connectionStatus.includes('✅') ? 'success' : 'error'}`}>
        <h3>Backend Connection</h3>
        <p>{connectionStatus}</p>
      </div>

      {/* Statistics */}
      {loading ? (
        <div className="loading">Loading statistics...</div>
      ) : stats ? (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_organizations}</div>
            <div className="stat-label">Organizations</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_users}</div>
            <div className="stat-label">Total Users</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_beneficiaries}</div>
            <div className="stat-label">Beneficiaries</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_officers}</div>
            <div className="stat-label">Officers</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_admins}</div>
            <div className="stat-label">Admins</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_schemes}</div>
            <div className="stat-label">Schemes</div>
          </div>
        </div>
      ) : (
        <div className="error">Failed to load statistics</div>
      )}

      <button onClick={loadStats} className="refresh-btn">
        🔄 Refresh Stats
      </button>
    </div>
  );
}

export default Dashboard;
