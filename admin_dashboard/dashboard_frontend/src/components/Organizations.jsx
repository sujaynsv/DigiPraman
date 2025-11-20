import { useState, useEffect } from 'react';
import { getOrganizations, createOrganization } from '../api/axios';
import './Organizations.css';

function Organizations() {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    config: {},
  });

  useEffect(() => {
    loadOrganizations();
  }, []);

  const loadOrganizations = async () => {
    try {
      setLoading(true);
      const response = await getOrganizations();
      setOrganizations(response.data);
    } catch (error) {
      console.error('Error loading organizations:', error);
      alert('Failed to load organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await createOrganization(formData);
      alert('Organization created successfully!');
      setShowForm(false);
      setFormData({ name: '', type: '', config: {} });
      loadOrganizations();
    } catch (error) {
      console.error('Error creating organization:', error);
      alert(error.response?.data?.detail || 'Failed to create organization');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="organizations">
      <div className="header">
        <h1>Organizations</h1>
        <button className="add-btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? '❌ Cancel' : '➕ Add Organization'}
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <form className="form-card" onSubmit={handleSubmit}>
          <h3>Create Organization</h3>
          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="e.g., Rural Development Bank"
            />
          </div>
          <div className="form-group">
            <label>Type</label>
            <input
              type="text"
              name="type"
              value={formData.type}
              onChange={handleChange}
              placeholder="e.g., financial_institution"
            />
          </div>
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Creating...' : 'Create Organization'}
          </button>
        </form>
      )}

      {/* List */}
      {loading && !showForm ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Created At</th>
                <th>ID</th>
              </tr>
            </thead>
            <tbody>
              {organizations.length === 0 ? (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center' }}>
                    No organizations found. Create one above!
                  </td>
                </tr>
              ) : (
                organizations.map((org) => (
                  <tr key={org.id}>
                    <td><strong>{org.name}</strong></td>
                    <td>{org.type || 'N/A'}</td>
                    <td>{new Date(org.created_at).toLocaleDateString()}</td>
                    <td className="id-cell">{org.id.substring(0, 8)}...</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Organizations;
