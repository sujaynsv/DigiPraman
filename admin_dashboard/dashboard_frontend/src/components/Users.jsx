import { useState, useEffect } from 'react';
import { getUsers, createUser, getOrganizations } from '../api/axios';
import './Users.css';

function Users() {
  const [users, setUsers] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    mobile: '',
    email: '',
    role: 'beneficiary',
    _org_id: '',
  });

  useEffect(() => {
    loadUsers();
    loadOrganizations();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await getUsers({ role: 'beneficiary' });
      setUsers(response.data);
    } catch (error) {
      console.error('Error loading users:', error);
      alert('Failed to load users');
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
      await createUser(formData);
      alert('User created successfully!');
      setShowForm(false);
      setFormData({
        name: '',
        mobile: '',
        email: '',
        role: 'beneficiary',
        _org_id: organizations[0]?.id || '',
      });
      loadUsers();
    } catch (error) {
      console.error('Error creating user:', error);
      alert(error.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="users">
      <div className="header">
        <h1>Beneficiaries</h1>
        <button className="add-btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? '❌ Cancel' : '➕ Add Beneficiary'}
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <form className="form-card" onSubmit={handleSubmit}>
          <h3>Add Beneficiary</h3>
          
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
            <label>Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Mobile *</label>
            <input
              type="tel"
              name="mobile"
              value={formData.mobile}
              onChange={handleChange}
              placeholder="+919876543210"
              required
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Creating...' : 'Create Beneficiary'}
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
                <th>Mobile</th>
                <th>Email</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center' }}>
                    No beneficiaries found
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id}>
                    <td><strong>{user.name}</strong></td>
                    <td>{user.mobile}</td>
                    <td>{user.email || 'N/A'}</td>
                    <td>
                      <span className={`status ${user.status}`}>
                        {user.status}
                      </span>
                    </td>
                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
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

export default Users;
