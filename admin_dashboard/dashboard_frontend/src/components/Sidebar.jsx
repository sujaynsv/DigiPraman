import { FaHome, FaBuilding, FaUsers, FaClipboardList, FaFileAlt } from 'react-icons/fa';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

function Sidebar({ currentView }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <FaHome />, to: '/' },
    { id: 'applications', label: 'Applications', icon: <FaFileAlt />, to: '/applications' },
    { id: 'organizations', label: 'Organizations', icon: <FaBuilding />, to: '/organizations' },
    { id: 'users', label: 'Beneficiaries', icon: <FaUsers />, to: '/users' },
    { id: 'schemes', label: 'Schemes', icon: <FaClipboardList />, to: '/schemes' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>📊 DigiPraman</h2>
      </div>
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <NavLink
            key={item.id}
            to={item.to}
            className={`nav-item ${currentView === item.id ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
