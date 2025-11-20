import { useState, useEffect } from 'react';
import { getSchemes, createScheme, getOrganizations } from '../api/axios';
import './Schemes.css';

function Schemes() {
  const [schemes, setSchemes] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    _org_id: '',
  });

  useEffect(() => {
    loadSchemes();
    loadOrganizations();
  }, []);

  const loadSchemes = async () => {
    try {
      setLoading(true);
      const response = await getSchemes();
      setSchemes(response.data);
    } catch (error) {
      console.error('Error loading schemes:', error);
      alert('Failed to load schemes');
    } finally {
      setLoading(false);
    }
  };

  const loadOrganizations = async () => {
    try {
      const response = await getOrganizations();
      setOrganizations(response.data);
      if (response.data.length > 0) {
        setFormData((prev) => ({ ...prev, _org_id: response.data[0].id }));
      }
    } catch (error) {
      console.error('Error loading organizations:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await createScheme(formData);
      alert('Scheme created successfully!');
      setShowForm(false);
      setFormData({ code: '', name: '', _org_id: organizations[0]?.id || '' });
      loadSchemes();
    } catch (error) {
      console.error('Error creating scheme:', error);
      alert(error.response?.data?.detail || 'Failed to create scheme');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="schemes">
      <div className="header">
        <h1>Loan Schemes</h1>
        <button className="add-btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? '❌ Cancel' : '➕ Add Scheme'}
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <form className="form-card" onSubmit={handleSubmit}>
          <h3>Create Scheme</h3>

          <div className="form-group">
            <label>Organization *</label>
            <select
              name="_org_id"
              value={formData._org_id}
              onChange={handleChange}
              required
            >
              <option value="">Select Organization</option>
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Scheme Code *</label>
            <input
              type="text"
              name="code"
              value={formData.code}
              onChange={handleChange}
              placeholder="e.g., PMEGP-2024"
              required
            />
          </div>

          <div className="form-group">
            <label>Scheme Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g., Prime Minister's Employment Generation Programme"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Creating...' : 'Create Scheme'}
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
                <th>Code</th>
                <th>Name</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {schemes.length === 0 ? (
                <tr>
                  <td colSpan="3" style={{ textAlign: 'center' }}>
                    No schemes found
                  </td>
                </tr>
              ) : (
                schemes.map((scheme) => (
                  <tr key={scheme.id}>
                    <td><strong>{scheme.code}</strong></td>
                    <td>{scheme.name}</td>
                    <td>{new Date(scheme.created_at).toLocaleDateString()}</td>
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

export default Schemes;
